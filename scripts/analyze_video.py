#!/usr/bin/env python3
"""
analyze_video.py — generate the evidence bundle for a video-style breakdown.

Produces, under --out:
  evidence/analysis_manifest.json   schema v1.0 (same shape as the skill's examples)
  evidence/overview/overview-*.jpg  montage sheets per 10s chunk (teacher) or one sheet (quick)
  evidence/events/event-*.jpg       per-transition montage sheets
  evidence/waveform.png             audio waveform (1600x300)

Modes:
  quick    light evidence, ~1 overview sheet + a few event sheets (10k-25k tokens)
  teacher  default, 3 overview sheets + ~6 event sheets + waveform (30k-70k tokens)
  forensic per-source-frame event windows, no overview sheets (>80k tokens)

Requirements: ffmpeg and ffprobe on PATH (or --ffmpeg-dir), Python 3.10+, Pillow.
Scene detection threshold is a normalized 0..1 mean-absolute-difference candidate
detector; flashes and glitch bursts are grouped, never counted as edits directly.

Usage:
  python analyze_video.py VIDEO --out DIR [--mode teacher] [--range-start 0] \
      [--range-end 30] [--user-focus 1.4 2.48 ...] [--ffmpeg-dir DIR]
"""

import argparse
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

SKILL_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0"


def find_tool(name, ffmpeg_dir):
    if ffmpeg_dir:
        cand = Path(ffmpeg_dir) / (name + ".exe")
        if cand.exists():
            return str(cand)
    env_dir = os.environ.get("VST_FFMPEG_DIR")
    if env_dir:
        cand = Path(env_dir) / (name + ".exe")
        if cand.exists():
            return str(cand)
    on_path = shutil.which(name)
    if on_path:
        return on_path
    return None


def run_ff(cmd, binary=True):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", "replace")
        raise RuntimeError(f"ffmpeg failed ({proc.returncode}): {err[-1200:]}")
    return proc.stdout if binary else proc.stdout.decode("utf-8", "replace")


def ffprobe_meta(ffprobe, video):
    out = run_ff([ffprobe, "-v", "error", "-print_format", "json",
                  "-show_format", "-show_streams", video], binary=True)
    data = json.loads(out)
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not v:
        raise RuntimeError("no video stream found in source")
    fps_num, _, fps_den = v["r_frame_rate"].partition("/")
    fps = float(fps_num) / float(fps_den or 1)
    fmt = data.get("format", {})
    return {
        "path": os.path.abspath(video),
        "duration_seconds": round(float(fmt.get("duration", v.get("duration", 0))), 2),
        "width": int(v["width"]),
        "height": int(v["height"]),
        "fps": round(fps, 3),
        "has_audio": a is not None,
        "audio_rate": int(a.get("sample_rate", 0)) if a else None,
    }


def scene_events(ffmpeg, video, start, end, threshold, fps_s=5.0, width=160):
    """Sample grayscale frames and return (raw_count, bursts, diff_times)."""
    cmd = [ffmpeg, "-ss", f"{start:.3f}", "-i", video, "-t", f"{end - start:.3f}",
           "-vf", f"fps={fps_s},scale={width}:-2,format=gray",
           "-f", "rawvideo", "pipe:1"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw = proc.stdout.read()
    proc.wait()
    if proc.returncode != 0:
        return 0, [], []
    # frame size from the effective scaled height
    probe = run_ff([ffmpeg, "-ss", f"{start:.3f}", "-i", video, "-frames:v", "1",
                    "-vf", f"scale={width}:-2,format=gray",
                    "-f", "rawvideo", "pipe:1"], binary=True)
    h = len(probe) // width if width else 0
    if h == 0 or len(raw) < width * h:
        return 0, [], []
    fsize = width * h
    n = len(raw) // fsize
    diffs = []
    prev = None
    for i in range(n):
        frame = raw[i * fsize:(i + 1) * fsize]
        if prev is not None:
            d = sum(abs(a - b) for a, b in zip(frame, prev)) / (255.0 * fsize)
            diffs.append((start + i / fps_s, d))
        prev = frame
    raw_events = [(t, d) for t, d in diffs if d > threshold]
    bursts = []
    for t, d in raw_events:
        if bursts and t - bursts[-1]["end"] <= 0.5:
            bursts[-1]["end"] = t
            bursts[-1]["frames"] += 1
            if d > bursts[-1]["score"]:
                bursts[-1]["score"] = d
                bursts[-1]["peak"] = t
        else:
            bursts.append({"start": t, "end": t, "peak": t,
                           "score": d, "frames": 1})
    return len(raw_events), bursts, diffs


def extract_frames(ffmpeg, video, win_start, win_end, sampling_fps, scale_w, tmpdir):
    """Extract jpg frames for [win_start, win_end] at sampling_fps into tmpdir.
    Returns list of (index, filepath)."""
    cmd = [ffmpeg, "-ss", f"{win_start:.3f}", "-i", video,
           "-t", f"{win_end - win_start:.3f}",
           "-vf", f"fps={sampling_fps},scale={scale_w}:-2",
           "-q:v", "4", "-frames:v", "4096", "-y",
           str(tmpdir / "f-%04d.jpg")]
    run_ff(cmd, binary=True)
    files = sorted(tmpdir.glob("f-*.jpg"))
    return files


def _load_default_font(size):
    from PIL import ImageFont
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return None


def make_sheet(frames, out_path, cell_w, aspect, start, sampling_fps, label):
    """Compose frames into a labeled montage grid (5 columns)."""
    from PIL import Image, ImageDraw
    cell_h = int(cell_w / aspect)
    chip_h = 20
    n = len(frames)
    cols = 5
    rows = math.ceil(n / cols)
    pad = 6
    w = cols * cell_w + (cols + 1) * pad
    h = rows * (cell_h + chip_h) + (rows + 1) * pad + 30
    sheet = Image.new("RGB", (w, h), (10, 10, 14))
    draw = ImageDraw.Draw(sheet)
    font = _load_default_font(14)
    if label:
        draw.text((pad, 6), label, fill=(230, 230, 235), font=font)
    for i, fp in enumerate(frames):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + pad)
        y = 30 + pad + r * (cell_h + chip_h + pad)
        try:
            im = Image.open(fp).convert("RGB")
        except Exception:
            continue
        im.thumbnail((cell_w, cell_h))
        ix = x + (cell_w - im.width) // 2
        iy = y + (cell_h - im.height) // 2
        sheet.paste(im, (ix, iy))
        t = start + i / sampling_fps
        ts = str(timedelta(seconds=t))[:12]
        draw.rectangle([x, y + cell_h, x + cell_w, y + cell_h + chip_h],
                       fill=(24, 24, 30))
        draw.text((x + 4, y + cell_h + 3), ts, fill=(0, 229, 255), font=font)
    sheet.save(out_path, quality=88)


def extract_audio(ffmpeg, video, start, end):
    cmd = [ffmpeg, "-ss", f"{start:.3f}", "-i", video, "-t", f"{end - start:.3f}",
           "-vn", "-ac", "1", "-ar", "44100", "-f", "f32le", "pipe:1"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw = proc.stdout.read()
    proc.wait()
    if proc.returncode != 0 or len(raw) < 4:
        return []
    return list(struct.unpack(f"<{len(raw)//4}f", raw[: (len(raw) // 4) * 4]))


def audio_analysis(samples, start, end):
    if not samples:
        return None
    rms = math.sqrt(sum(s * s for s in samples) / len(samples))
    frame_len, hop = 512, 256
    energy = []
    for i in range(0, len(samples) - frame_len, hop):
        block = samples[i:i + frame_len]
        energy.append(sum(s * s for s in block) / frame_len)
    mean_e = sum(energy) / len(energy) if energy else 0.0
    onsets = []
    for i in range(2, len(energy) - 2):
        e = energy[i]
        if e > mean_e * 2.0 and e >= energy[i - 2] and e >= energy[i - 1] \
                and e >= energy[i + 1] and e >= energy[i + 2]:
            onsets.append(start + (i * hop) / 44100.0)
    # autocorrelation of the energy envelope over 0.2s..2.0s lags
    lag_min = int(0.2 * 44100 / hop)
    lag_max = int(2.0 * 44100 / hop)
    best_lag, best_score = None, -1.0
    for lag in range(lag_min, min(lag_max, len(energy) // 2) + 1):
        num = sum(energy[i] * energy[i + lag] for i in range(len(energy) - lag))
        den = sum(e * e for e in energy) + 1e-9
        score = num / den
        if score > best_score:
            best_score, best_lag = score, lag
    bpm = round(60.0 / ((best_lag * hop) / 44100.0), 1) if best_lag else None
    return {
        "tempo_candidate_bpm": bpm,
        "onset_count": len(onsets),
        "onset_times": [round(t, 3) for t in onsets],
        "rms_mean": round(rms, 5),
        "method_note": "Energy-onset autocorrelation; candidate tempo, not a musical ground truth",
    }


def render_waveform(samples, start, end, out_path):
    from PIL import Image, ImageDraw
    W, H = 1600, 300
    img = Image.new("RGB", (W, H), (10, 10, 16))
    draw = ImageDraw.Draw(img)
    mid = H // 2
    draw.line([(0, mid), (W, mid)], fill=(40, 44, 60))
    if not samples:
        img.save(out_path)
        return
    bins = 1200
    per = max(1, len(samples) // bins)
    for b in range(min(bins, len(samples) // per)):
        block = samples[b * per:(b + 1) * per]
        peak = max(abs(s) for s in block) if block else 0.0
        bar = int(peak * (mid - 8))
        x = 4 + b * (W - 8) // bins
        draw.line([(x, mid - bar), (x, mid + bar)], fill=(0, 210, 235))
    img.save(out_path)


def pick_events(bursts, user_focus, target, margin=0.6):
    picked = []
    for t in user_focus:
        picked.append({"peak_time": round(float(t), 3), "peak_score": None,
                       "detected_frames": None, "source": "user-focus"})
    scene = sorted(bursts, key=lambda b: b["score"], reverse=True)
    for b in scene:
        if len(picked) >= target:
            break
        if all(abs(b["peak"] - p["peak_time"]) > margin for p in picked):
            picked.append({"peak_time": round(b["peak"], 3),
                           "peak_score": round(b["score"], 3),
                           "detected_frames": b["frames"],
                           "source": "scene-detector"})
    picked.sort(key=lambda p: p["peak_time"])
    return picked[:target]


def fmt_ts(seconds):
    """Zero-padded HH-MM-SS-mmm for filenames."""
    ms = int(round((seconds - int(seconds)) * 1000))
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02d}-{m:02d}-{sec:02d}-{ms:03d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", default="teacher",
                    choices=["quick", "teacher", "forensic"])
    ap.add_argument("--range-start", type=float, default=0.0)
    ap.add_argument("--range-end", type=float, default=30.0)
    ap.add_argument("--user-focus", type=float, nargs="*", default=[],
                    help="user-identified transition times to force into event sheets")
    ap.add_argument("--scene-threshold", type=float, default=0.3)
    ap.add_argument("--ffmpeg-dir", default=None,
                    help="directory containing ffmpeg.exe/ffprobe.exe")
    args = ap.parse_args()

    ffmpeg = find_tool("ffmpeg", args.ffmpeg_dir)
    ffprobe = find_tool("ffprobe", args.ffmpeg_dir)
    if not ffmpeg or not ffprobe:
        sys.exit("[ERROR] ffmpeg/ffprobe not found. Install FFmpeg (winget install "
                 "Gyan.FFmpeg) or pass --ffmpeg-dir to the folder containing them.")

    src = ffprobe_meta(ffprobe, args.video)
    start, end = max(0.0, args.range_start), min(args.range_end, src["duration_seconds"])
    if end <= start:
        sys.exit("[ERROR] empty analysis range")
    aspect = src["width"] / src["height"]

    if args.mode == "teacher":
        chunk, ov_fps, ev_fps, ev_target = 10.0, 2.0, 12.5, 6
        intensity = "medium"
    elif args.mode == "quick":
        chunk, ov_fps, ev_fps, ev_target = end - start, 1.0, 6.0, 2
        intensity = "low"
    else:
        chunk, ov_fps, ev_fps, ev_target = None, None, src["fps"], 2
        intensity = "high"

    print(f"[1/5] probing source: {src['width']}x{src['height']} @ {src['fps']}fps")
    raw_count, bursts, _ = scene_events(ffmpeg, args.video, start, end,
                                        args.scene_threshold)
    print(f"[2/5] scene candidates: {raw_count} raw, {len(bursts)} grouped bursts")

    out = Path(args.out)
    ov_dir = out / "evidence" / "overview"
    ev_dir = out / "evidence" / "events"
    ov_dir.mkdir(parents=True, exist_ok=True)
    ev_dir.mkdir(parents=True, exist_ok=True)

    overview_sheets = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        if chunk:
            t = start
            idx = 0
            while t < end - 1e-6:
                c_end = min(t + chunk, end)
                frames = extract_frames(ffmpeg, args.video, t, c_end, ov_fps, 360, tmp)
                label = f"{args.mode} overview {t:.0f}-{c_end:.0f}s  @ {ov_fps}fps"
                name = f"overview-{idx + 1:02d}-{fmt_ts(t)}.jpg"
                make_sheet(frames, ov_dir / name, 300, aspect, t, ov_fps, label)
                overview_sheets.append({
                    "file": os.path.join("overview", name),
                    "start": round(t, 3), "end": round(c_end, 3),
                    "sampled_frames": len(frames), "sampling_fps": ov_fps,
                })
                t = c_end
                idx += 1

    events = pick_events(bursts, args.user_focus, ev_target)
    event_sheets = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for i, ev in enumerate(events, 1):
            ws = max(start, ev["peak_time"] - 0.6)
            we = min(end, ev["peak_time"] + 0.6)
            frames = extract_frames(ffmpeg, args.video, ws, we, ev_fps, 300, tmp)
            fname = f"event-{i:02d}-{fmt_ts(ev['peak_time'])}.jpg"
            make_sheet(frames, ev_dir / fname, 300, aspect, ws, ev_fps,
                       f"{args.mode} event {i}  peak {fmt_ts(ev['peak_time'])}")
            event_sheets.append({
                "peak_time": ev["peak_time"], "peak_score": ev["peak_score"],
                "detected_frames": ev["detected_frames"], "source": ev["source"],
                "file": os.path.join("events", fname),
                "window_start": round(ws, 3), "window_end": round(we, 3),
                "sampling_fps": ev_fps, "sampled_frames": len(frames),
                "source_frame_near_peak": round(ev["peak_time"] * src["fps"]),
            })
            for f in frames:
                f.unlink(missing_ok=True)

    print(f"[3/5] wrote {len(overview_sheets)} overview sheets, {len(event_sheets)} event sheets")

    waveform_rel = "waveform.png"
    audio = extract_audio(ffmpeg, args.video, start, end) if src["has_audio"] else []
    render_waveform(audio, start, end, out / "evidence" / waveform_rel)
    audio_blk = audio_analysis(audio, start, end)
    print(f"[4/5] audio: {len(audio)} samples, tempo candidate "
          f"{audio_blk['tempo_candidate_bpm'] if audio_blk else 'n/a'} bpm")

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "skill_version": SKILL_VERSION,
        "source": src,
        "analysis": {
            "mode": args.mode,
            "range_start": round(start, 3),
            "range_end": round(end, 3),
            "duration_seconds": round(end - start, 3),
            "scene_threshold": args.scene_threshold,
            "raw_scene_events": raw_count,
            "grouped_scene_bursts": len(bursts),
            "warning": "Scene detections are candidates; flashes and glitch bursts "
                       "are not automatically separate edits.",
        },
        "overview_sheets": overview_sheets,
        "event_sheets": event_sheets,
        "waveform": waveform_rel,
        "audio_analysis": audio_blk,
        "token_note": {
            "visual_sheet_count": len(overview_sheets) + len(event_sheets),
            "intensity": intensity,
            "disclaimer": "Exact Codex tokens depend on model, image handling, "
                          "context, reasoning, and tool results.",
        },
    }
    mp = out / "evidence" / "analysis_manifest.json"
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[5/5] manifest written: {mp}")
    print(f"      visual sheets: {len(overview_sheets) + len(event_sheets)} "
          f"({intensity} token intensity)")


if __name__ == "__main__":
    main()
