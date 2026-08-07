#!/usr/bin/env python3
"""
collect_tutorials.py — collect ranked YouTube/Bilibili tutorials for lesson topics.

For each --queries "topic:search query" the script:
  - pulls YouTube results with live metadata via yt-dlp when available,
  - pulls Bilibili candidates from a web-search JSON (--search-json) and enriches
    them with yt-dlp; on HTTP 412 or any failure the entry is marked unverified
    instead of guessing view counts,
  - ranks by title/query relevance then log-scaled view count,
  - writes tutorial-research.json + tutorial-research.md snapshots.

The model must still open candidates and confirm they actually demonstrate the
Premiere control used in the lesson before embedding the link.

Usage:
  python collect_tutorials.py --out DIR \
      --queries "match-cut:Premiere Pro match cut transition tutorial" \
      --queries "rgb-glitch:Premiere Pro glitch RGB split tutorial"

  Optional: --search-json search_results.json  (web-search tool output)
"""

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

STOPWORDS = {"a", "an", "the", "in", "on", "of", "to", "for", "with", "and", "or",
             "how", "tutorial", "premiere", "pro", "pr", "教程"}


def fmt_duration(seconds):
    if seconds is None:
        return "?"
    seconds = int(seconds)
    if seconds >= 60:
        return f"{seconds // 60}:{seconds % 60:02d}"
    return f"{seconds}s"


def fmt_views(v):
    return "?" if v is None else f"{v:,}"


def relevance(title, query):
    terms = {t for t in re.findall(r"[a-z0-9\u4e00-\u9fff]{2,}", query.lower())
             if t not in STOPWORDS}
    if not terms:
        return 0.5
    title_l = title.lower() if title else ""
    hit = sum(1 for t in terms if t in title_l)
    return hit / len(terms)


def yt_search(query, limit, out_errors):
    try:
        import yt_dlp
    except ImportError:
        out_errors.append("YouTube metadata requires yt-dlp; supply --search-json instead.")
        return []
    opts = {"quiet": True, "skip_download": True, "noplaylist": True,
            "socket_timeout": 15}
    rows = []
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch{max(limit * 2, limit)}:{query}",
                                    download=False)
            for e in (info.get("entries") or [])[:max(limit * 2, limit)]:
                rows.append({
                    "title": e.get("title"), "url": e.get("webpage_url"),
                    "views": e.get("view_count"), "duration_s": e.get("duration"),
                    "channel": e.get("channel"), "verified": True,
                })
    except Exception as exc:
        out_errors.append(f"YouTube search failed: {exc}")
    return rows


def load_topic_entries(data, topic):
    """Return web-search entries for a topic.

    Accepts either a flat list / {"results": [...]} (all entries apply to every
    topic), or a grouped {"queries": {topic: [entries]}} payload (recommended so
    candidates stay topic-scoped).
    """
    if isinstance(data, dict):
        grouped = data.get("queries")
        if isinstance(grouped, dict) and topic in grouped:
            return grouped[topic] or []
        return data.get("results", []) or []
    return data or []


def from_search_json(data, topic, host_pattern):
    entries = load_topic_entries(data, topic)
    rows = []
    for e in entries:
        url = e.get("url", "")
        if re.search(host_pattern, url, re.I):
            rows.append({
                "title": e.get("title"), "url": url,
                "views": None, "duration_s": None,
                "channel": None, "verified": False,
            })
    return rows


def enrich_bilibili(rows, out_errors):
    """Try live metadata per Bilibili URL; HTTP 412/misc -> keep unverified."""
    try:
        import yt_dlp
    except ImportError:
        out_errors.append("Bilibili enrichment requires yt-dlp; entries stay unverified.")
        return rows
    opts = {"quiet": True, "skip_download": True, "noplaylist": True,
            "socket_timeout": 15}
    with yt_dlp.YoutubeDL(opts) as ydl:
        for r in rows:
            try:
                info = ydl.extract_info(r["url"], download=False)
                r["title"] = info.get("title", r["title"])
                r["views"] = info.get("view_count")
                r["duration_s"] = info.get("duration")
                r["channel"] = info.get("channel")
                r["verified"] = True
            except Exception as exc:
                msg = str(exc)
                if "412" in msg:
                    out_errors.append(
                        f"Bilibili HTTP 412 for {r['url']}; marked unverified.")
                else:
                    out_errors.append(f"Bilibili metadata failed for {r['url']}: {msg[:200]}")
    return rows


def rank(rows, query, limit):
    scored = []
    for r in rows:
        if not r.get("url"):
            continue
        rel = relevance(r.get("title"), query)
        view_s = 0.0 if r.get("views") is None else min(1.0, math.log10(1 + r["views"]) / 7.0)
        s = round(0.7 * rel + 0.3 * view_s, 4)
        r["rel"] = rel
        r["score"] = s
        scored.append(r)
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:limit]


def render_md(topics, generated):
    lines = ["# Tutorial research snapshot", "",
             f"Generated: `{generated}`", "",
             "Ranking favors direct title/query relevance, then log-scaled view count. "
             "Manually confirm teaching completeness before assigning a link.", ""]
    for t in topics:
        lines += [f"## {t['topic']}", "", f"Search: `{t['query']}`", ""]
        for engine, rows, errs in (("YouTube", t["youtube"], t.get("youtube_errors", [])),
                                   ("Bilibili", t["bilibili"], t.get("bilibili_errors", []))):
            lines.append(f"### {engine}")
            if rows:
                lines += ["", "| Rank | Tutorial | Views | Duration | Channel | Score |",
                          "|---:|---|---:|---:|---|---:|"]
                for i, r in enumerate(rows, 1):
                    tag = "" if r.get("verified") else " *(unverified)*"
                    lines.append(
                        f"| {i} | [{r['title']}]({r['url']}) | {fmt_views(r.get('views'))} | "
                        f"{fmt_duration(r.get('duration_s'))} | {r.get('channel') or '?'} | "
                        f"{r['score']}{tag} |")
                lines.append("")
            elif errs:
                lines += ["", f"Metadata unavailable: `{errs[0]}`", ""]
            else:
                lines += ["", "No candidates found.", ""]
    lines += ["## Review checklist", "",
              "- Open the candidate and confirm it demonstrates the exact Premiere "
              "control used in the lesson.",
              "- Reject preset ads, compilations without instruction, and misleading titles.",
              "- Treat view counts as a dated snapshot, not a quality guarantee.",
              "- If Bilibili reports HTTP 412, discover pages through web search and mark "
              "missing metadata as unverified.", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--queries", action="append", required=True, metavar="topic:query",
                    help='e.g. "match-cut:Premiere Pro match cut transition tutorial"')
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--search-json", default=None,
                    help="web-search tool output JSON with title/url entries")
    args = ap.parse_args()

    search_data = None
    if args.search_json:
        search_data = json.loads(Path(args.search_json).read_text(encoding="utf-8"))

    generated = datetime.now(timezone.utc).isoformat()
    topics = []
    for spec in args.queries:
        topic, _, query = spec.partition(":")
        yt_errs, bl_errs = [], []
        yt_rows = yt_search(query, args.limit, yt_errs)
        if search_data is not None and not yt_rows:
            yt_rows = from_search_json(search_data, topic,
                                       r"(youtube\.com/watch|youtu\.be/)")
        bl_rows = from_search_json(search_data, topic,
                                   r"bilibili\.com/video|b23\.tv") \
            if search_data is not None else []
        bl_rows = enrich_bilibili(bl_rows, bl_errs)
        topics.append({
            "topic": topic,
            "query": query,
            "youtube": rank(yt_rows, query, args.limit),
            "bilibili": rank(bl_rows, query, args.limit),
            "youtube_errors": yt_errs,
            "bilibili_errors": bl_errs,
        })
        print(f"[{topic}] youtube={len(topics[-1]['youtube'])} "
              f"bilibili={len(topics[-1]['bilibili'])} "
              f"(yt errors: {len(yt_errs)}, bili errors: {len(bl_errs)})")

    out = Path(args.out)
    auto_dir = out / "tutorial-research-auto"
    auto_dir.mkdir(parents=True, exist_ok=True)
    payload = {"generated": generated,
               "ranking_note": "Relevance then log-scaled views; unverified entries "
                               "must be confirmed before use.",
               "topics": topics}
    (auto_dir / "tutorial-research.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (auto_dir / "tutorial-research.md").write_text(
        render_md(topics, generated), encoding="utf-8")
    print(f"written: {auto_dir / 'tutorial-research.json'}")
    print(f"written: {auto_dir / 'tutorial-research.md'}")


if __name__ == "__main__":
    main()
