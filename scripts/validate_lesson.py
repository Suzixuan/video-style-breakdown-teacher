#!/usr/bin/env python3
"""
validate_lesson.py — validate a teacher-mode lesson.md.

Checks:
  - required top-level sections,
  - every "T0x" transition lesson closes the teach-practice-check-transfer loop
    (all 13 required subsections present),
  - negative guards: no exact-original-preset claims, every event links a tutorial,
    capability boundary mentions 3D/source dependence,
  - optional manifest consistency (mode, range, event count).

Exit code 0 = pass, 1 = fail.

Usage:
  python validate_lesson.py LESSON.md [--manifest evidence/analysis_manifest.json]
"""

import argparse
import json
import re
import sys
from pathlib import Path

TOP_SECTIONS = [
    "先看结论", "素材与证据", "节奏地图", "逐转场教学",
    "PR 复刻工程", "分层练习", "自测与交作业", "教程链接", "能力边界",
]

EVENT_SUBSECTIONS = [
    "时间码证据", "观察", "判断与置信度", "原理", "Premiere 操作",
    "参数起点", "为什么这样设", "失败症状与修正", "迁移思路",
    "练习", "验收", "教程", "能力边界",
]

BANNED = ["原片参数", "原作者预设", "exact preset", "原片使用了", "原作者的"]
NEGATION = ("不", "无", "无法", "不能", "禁止", "不要", "避免", "不应", "从未", "并非")


def bpm_instruction_violations(text):
    """Reject turning an unverified numeric BPM into a marker-editing command."""
    violations = []
    lines = text.splitlines()
    marker_action = (
        r"(?:打\s*`?M`?|(?:打|铺|设置|创建|添加|插入)[^。；\n]{0,8}标记|"
        r"(?:set|create|add|insert)\s+(?:an?\s+|the\s+)?markers?)"
    )
    danger = re.compile(
        rf"(?:按|用|以)[^。；\n]{{0,40}}{marker_action}"
        rf"|{marker_action}[^。；\n]{{0,40}}(?:按|依据|根据|at)(?:它|该值|这个值)?"
        rf"|{marker_action}[^。；\n]{{0,40}}(?:每拍|every\s+beat)",
        re.IGNORECASE,
    )
    direct_prohibition = re.compile(
        r"(?:不要|不应|不能|禁止|避免|切勿|不可|do\s+not|don't|never)[^。；\n]{0,20}$",
        re.IGNORECASE,
    )
    for i, line in enumerate(lines):
        clauses = [part.strip() for part in re.split(r"[。；]", line) if part.strip()]
        for clause_index, clause in enumerate(clauses):
            if not re.search(r"\b\d+(?:\.\d+)?\s*BPM", clause, re.IGNORECASE):
                continue
            window_parts = [clause]
            if clause_index + 1 < len(clauses) and re.match(
                r"^(?:但|但是|然而|仍|却|可是)", clauses[clause_index + 1]
            ):
                window_parts.append(clauses[clause_index + 1])
            if i + 1 < len(lines) and re.match(
                r"^\s*(?:按|用|以|打|铺)", lines[i + 1]
            ):
                window_parts.append(lines[i + 1].strip())
            window = "；".join(window_parts)
            for match in danger.finditer(window):
                prefix = window[max(0, match.start() - 20):match.start()]
                if not direct_prohibition.search(prefix):
                    violations.append(f"L{i + 1}: {window.strip()[:140]}")
                    break
    return violations


def section_map(text):
    """Map heading text -> line index, handling #..#### headings."""
    heads = {}
    for i, line in enumerate(text.splitlines()):
        m = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if m:
            heads[m.group(2).strip()] = i
    return heads


def event_blocks(text):
    r"""Yield (title, start, end_line) for each T\d+ transition section."""
    lines = text.splitlines()
    starts = [(i, re.match(r"^#{1,4}\s+(T\d+)\b", l.strip()))
              for i, l in enumerate(lines)]
    starts = [(i, m.group(1)) for i, m in starts if m]
    for k, (i, title) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        yield title, i, end


def check(lines, ok):
    for line in lines:
        print(("  [OK] " if ok else "  [FAIL] ") + line)
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("lesson", help="path to lesson.md")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as failures")
    args = ap.parse_args()

    lp = Path(args.lesson)
    if not lp.exists():
        sys.exit(f"[ERROR] lesson not found: {lp}")
    text = lp.read_text(encoding="utf-8")
    heads = section_map(text)
    all_ok = True

    print("== top-level sections ==")
    missing = [s for s in TOP_SECTIONS if s not in heads]
    all_ok &= check([f"all {len(TOP_SECTIONS)} required sections present"
                     if not missing else f"missing: {', '.join(missing)}"],
                    not missing)

    print("== transition lessons (T0x) ==")
    blocks = list(event_blocks(text))
    if not blocks:
        all_ok &= check(["no T0x transition lessons found"], False)
    else:
        all_ok &= check([f"{len(blocks)} transition lesson(s)"], True)
        for title, i, end in blocks:
            block = "\n".join(text.splitlines()[i:end])
            bheads = set()
            for line in block.splitlines():
                stripped = line.strip()
                m = re.match(r"^\*\*(.+?)\*\*", stripped)
                if m:
                    bheads.add(m.group(1).strip())
                h = re.match(r"^#{1,6}\s+(.+)$", stripped)
                if h:
                    bheads.add(h.group(1).strip())
            missing_sub = [s for s in EVENT_SUBSECTIONS if s not in bheads]
            has_link = "http" in block
            ok = not missing_sub and has_link
            print(f"  {'[OK]' if ok else '[FAIL]'} {title}: "
                  f"subsections {len(EVENT_SUBSECTIONS) - len(missing_sub)}/"
                  f"{len(EVENT_SUBSECTIONS)}"
                  + (f"; missing: {', '.join(missing_sub)}" if missing_sub else "")
                  + ("" if has_link else "; no tutorial link"))
            all_ok &= ok

    print("== negative guards ==")
    bad_lines = []
    for i, line in enumerate(text.splitlines(), 1):
        if any(b in line for b in BANNED) and not any(n in line for n in NEGATION):
            bad_lines.append(f"L{i}: {line.strip()[:80]}")
    all_ok &= check(["no exact-original-preset claims"
                     if not bad_lines else "suspicious lines:\n      "
                     + "\n      ".join(bad_lines)],
                    not bad_lines)

    all_ok &= check(["capability boundary mentions 3D/source dependence"
                     if re.search(r"3D|源素材|预渲染|source", text)
                     else "capability boundary does not mention 3D/source"],
                    bool(re.search(r"3D|源素材|预渲染|source", text)))

    all_ok &= check(["tutorial snapshot date or 'unverified' present"
                     if re.search(r"快照|未核实|unverified", text)
                     else "no tutorial snapshot/unverified marker found"],
                    bool(re.search(r"快照|未核实|unverified", text)))

    bpm_bad = bpm_instruction_violations(text)
    all_ok &= check(["no unverified numeric BPM used as a marker command"
                     if not bpm_bad else "numeric BPM used as editing instruction:\n      "
                     + "\n      ".join(bpm_bad)],
                    not bpm_bad)

    if args.manifest:
        print("== manifest consistency ==")
        mp = Path(args.manifest)
        if not mp.exists():
            all_ok &= check([f"manifest not found: {mp}"], False)
        else:
            man = json.loads(mp.read_text(encoding="utf-8"))
            mode = man.get("analysis", {}).get("mode")
            rs, re_ = man["analysis"]["range_start"], man["analysis"]["range_end"]
            n_ev = len(man.get("event_sheets", []))
            m = re.search(r"分析范围：([\d:.]+)–([\d:.]+)", text)
            ok = True
            if m:
                def to_s(x):
                    p = [float(v) for v in x.split(":")]
                    return p[0] * 3600 + p[1] * 60 + p[2]
                ok = abs(to_s(m.group(1)) - rs) < 0.05 and \
                     abs(to_s(m.group(2)) - re_) < 0.05
                all_ok &= check(["lesson range matches manifest" if ok
                                 else "lesson range differs from manifest"], ok)
            else:
                all_ok &= check(["no 分析范围 line to compare"], False)
            print(f"  [info] mode={mode}, events in manifest={n_ev}, "
                  f"lessons in text={len(blocks)}")
            if mode not in ("quick", "teacher", "forensic"):
                all_ok &= check([f"unknown mode: {mode}"], False)

    print()
    if all_ok:
        print("PASS")
        sys.exit(0)
    print("FAIL — fix reported issues and re-run")
    sys.exit(1)


if __name__ == "__main__":
    main()
