#!/usr/bin/env python3
"""Validate a v2 curriculum.yaml and its units/*.yaml files."""

import argparse
from datetime import date
import re
import sys
from pathlib import Path

import yaml

try:
    from scripts.validate_lesson import bpm_instruction_violations
except ModuleNotFoundError:  # direct execution from scripts/
    from validate_lesson import bpm_instruction_violations


CAPABILITIES = {
    "PR-native", "PR-approximation", "AE-preferred", "3D-source-required"
}
CHECKPOINT_TYPES = ("structural", "parameter", "visual")
COURSE_SECTION_HEADINGS = (
    "## 你会做出什么",
    "## 跟我做",
    "## 你现在应该看到",
    "## 做错了怎么修",
    "## 交作业",
    "## 继续学习",
    "## 能力边界",
)


def load_yaml(path, errors):
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        errors.append(f"cannot read YAML {path}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"YAML root must be a mapping: {path}")
        return {}
    return data


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def find_cycle(graph):
    visiting = set()
    visited = set()
    trail = []

    def visit(node):
        if node in visiting:
            start = trail.index(node)
            return trail[start:] + [node]
        if node in visited:
            return None
        visiting.add(node)
        trail.append(node)
        for dependency in graph.get(node, []):
            cycle = visit(dependency)
            if cycle:
                return cycle
        trail.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in graph:
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def taxonomy_ids(path, errors):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read taxonomy {path}: {exc}")
        return set()
    ids = set(re.findall(r"^\| `([a-z0-9-]+)` \|", text, re.MULTILINE))
    if not ids:
        errors.append(f"taxonomy contains no canonical skill rows: {path}")
    return ids


def taxonomy_graph(path, errors):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read taxonomy {path}: {exc}")
        return {}
    graph = {}
    pattern = re.compile(
        r"^\| `([a-z0-9-]+)` \| [^|]+ \| [^|]+ \| ([^|]+)\|$",
        re.MULTILINE,
    )
    for skill_id, dependency_cell in pattern.findall(text):
        dependency_cell = dependency_cell.strip()
        graph[skill_id] = [] if dependency_cell == "—" else [
            dependency.strip() for dependency in dependency_cell.split(",")
        ]
    if not graph:
        errors.append(f"taxonomy contains no dependency rows: {path}")
    for skill_id, dependencies in graph.items():
        for dependency in dependencies:
            if dependency not in graph:
                errors.append(f"taxonomy skill {skill_id} requires unknown skill: {dependency}")
    cycle = find_cycle(graph)
    if cycle:
        errors.append("taxonomy dependency cycle: " + " -> ".join(cycle))
    return graph


def timecode_seconds(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{2}:\d{2}(?::\d{2})?", value):
        return None
    parts = [int(part) for part in value.split(":")]
    if parts[-1] >= 60 or (len(parts) == 3 and parts[-2] >= 60):
        return None
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def valid_iso_date(value):
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def validate_human_curriculum(path, lesson_ids, units, errors):
    """Require a course index plus executable learner-facing lesson files."""
    human_path = path.parent / "curriculum.md"
    try:
        text = human_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"human-readable curriculum.md is required: {exc}")
        return

    course_dir = path.parent / "course"
    course_index = course_dir / "README.md"
    if not course_index.exists():
        errors.append(f"learner-facing course/README.md is required: {course_index}")

    for lesson_id in lesson_ids:
        if not isinstance(lesson_id, str) or lesson_id not in units:
            continue
        link = f"course/{lesson_id}.md"
        if link not in text:
            errors.append(f"curriculum.md missing course link: {link}")
        lesson_path = course_dir / f"{lesson_id}.md"
        try:
            lesson_text = lesson_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"learner-facing lesson is required for {lesson_id}: {exc}")
            continue
        unit_title = units[lesson_id].get("title")
        expected_heading = f"# {lesson_id}｜{unit_title}"
        if nonempty(unit_title) and expected_heading not in lesson_text.splitlines()[:3]:
            errors.append(
                f"course/{lesson_id}.md title must match unit: {expected_heading}"
            )
        for heading in COURSE_SECTION_HEADINGS:
            if heading not in lesson_text:
                errors.append(f"course/{lesson_id}.md missing learner section: {heading}")
        if len(lesson_text) < 1000:
            errors.append(
                f"course/{lesson_id}.md is too shallow for an executable lesson: "
                f"{len(lesson_text)} characters"
            )
        step_count = len(re.findall(r"^\d+\.\s+", lesson_text, re.MULTILINE))
        if step_count < 5:
            errors.append(
                f"course/{lesson_id}.md needs at least 5 numbered actions; found {step_count}"
            )
        if "https://" not in lesson_text:
            errors.append(f"course/{lesson_id}.md needs at least one direct tutorial/source link")
        if lesson_id != "L12" and "../evidence/" not in lesson_text:
            errors.append(f"course/{lesson_id}.md must cite reference-video evidence")


def validate_curriculum(path, strict=False):
    errors = []
    warnings = []
    info = []
    curriculum = load_yaml(path, errors)
    if not curriculum:
        return errors, warnings, info

    if str(curriculum.get("version")) != "2.0":
        errors.append("version must be '2.0'")
    if not nonempty(curriculum.get("course_id")):
        errors.append("course_id is required")
    if not nonempty(curriculum.get("goal", {}).get("description")):
        errors.append("goal.description is required")

    video = curriculum.get("video", {})
    video_range = video.get("range", {})
    range_start = video_range.get("start")
    range_end = video_range.get("end")
    if not all(isinstance(v, (int, float)) for v in (range_start, range_end)):
        errors.append("video.range.start/end must be numeric")
    elif range_start < 0 or range_end <= range_start:
        errors.append("video range must satisfy 0 <= start < end")
    if not isinstance(video.get("fps"), (int, float)) or video.get("fps", 0) <= 0:
        errors.append("video.fps must be positive")

    taxonomy_value = curriculum.get("taxonomy")
    canonical_skill_graph = {}
    if not nonempty(taxonomy_value):
        errors.append("taxonomy path is required")
        taxonomy = set()
    else:
        taxonomy_path = (path.parent / taxonomy_value).resolve()
        if not taxonomy_path.exists():
            errors.append(f"taxonomy not found: {taxonomy_path}")
            taxonomy = set()
            canonical_skill_graph = {}
        else:
            taxonomy = taxonomy_ids(taxonomy_path, errors)
            canonical_skill_graph = taxonomy_graph(taxonomy_path, errors)

    skill_rows = curriculum.get("skills")
    if not isinstance(skill_rows, list) or not skill_rows:
        errors.append("skills must be a non-empty list")
        skill_rows = []
    skill_ids = []
    skill_graph = {}
    for index, row in enumerate(skill_rows):
        label = f"skills[{index}]"
        if not isinstance(row, dict) or not nonempty(row.get("id")):
            errors.append(f"{label}.id is required")
            continue
        skill_id = row["id"]
        if skill_id in skill_ids:
            errors.append(f"duplicate skill id: {skill_id}")
        skill_ids.append(skill_id)
        requires = row.get("requires", [])
        if not isinstance(requires, list):
            errors.append(f"{label}.requires must be a list")
            requires = []
        elif not all(nonempty(dependency) for dependency in requires):
            errors.append(f"{label}.requires entries must be non-empty skill IDs")
            requires = [dependency for dependency in requires if nonempty(dependency)]
        skill_graph[skill_id] = requires
        if taxonomy and skill_id not in taxonomy:
            errors.append(f"skill not found in taxonomy: {skill_id}")
    skill_set = set(skill_ids)
    for skill_id, dependencies in skill_graph.items():
        for dependency in dependencies:
            if dependency not in skill_set:
                errors.append(f"skill {skill_id} requires unknown skill: {dependency}")
        if skill_id in canonical_skill_graph and set(dependencies) != set(canonical_skill_graph[skill_id]):
            errors.append(
                f"skill {skill_id} dependencies differ from taxonomy: "
                f"curriculum={dependencies}, taxonomy={canonical_skill_graph[skill_id]}"
            )
    cycle = find_cycle(skill_graph)
    if cycle:
        errors.append("skill dependency cycle: " + " -> ".join(cycle))

    lesson_ids = curriculum.get("lessons")
    if not isinstance(lesson_ids, list) or not lesson_ids:
        errors.append("lessons must be a non-empty ordered list")
        lesson_ids = []
    valid_lesson_ids = [lesson_id for lesson_id in lesson_ids if isinstance(lesson_id, str)]
    if len(valid_lesson_ids) != len(set(valid_lesson_ids)):
        errors.append("lesson IDs must be unique")
    lesson_id_set = set(valid_lesson_ids)
    if strict and len(lesson_ids) < 10:
        errors.append("strict sample curriculum requires at least 10 micro/synthesis lessons")
    elif len(lesson_ids) < 10:
        warnings.append("curriculum has fewer than 10 lessons")

    units_dir = path.parent / "units"
    unit_graph = {}
    used_skills = set()
    units = {}
    unit_skills_by_lesson = {}
    new_skills_by_lesson = {}
    for index, lesson_id in enumerate(lesson_ids):
        if not isinstance(lesson_id, str) or not re.fullmatch(r"L\d{2,}", lesson_id):
            errors.append(f"invalid lesson ID: {lesson_id!r}")
            continue
        unit_path = units_dir / f"{lesson_id}.yaml"
        if not unit_path.exists():
            errors.append(f"missing unit file: {unit_path}")
            continue
        unit = load_yaml(unit_path, errors)
        units[lesson_id] = unit
        if unit.get("id") != lesson_id:
            errors.append(f"{lesson_id}: unit id must match filename")
        for field in ("title", "goal", "primary_skill"):
            if not nonempty(unit.get(field)):
                errors.append(f"{lesson_id}: {field} is required")

        unit_type = unit.get("type")
        if unit_type not in {"micro", "synthesis", "capstone"}:
            errors.append(f"{lesson_id}: type must be micro, synthesis, or capstone")
        minutes = unit.get("estimated_minutes")
        if not isinstance(minutes, int):
            errors.append(f"{lesson_id}: estimated_minutes must be an integer")
        elif unit_type == "micro" and not 10 <= minutes <= 25:
            errors.append(f"{lesson_id}: micro lesson must take 10–25 minutes")
        elif unit_type in {"synthesis", "capstone"} and not 30 <= minutes <= 60:
            errors.append(f"{lesson_id}: synthesis/capstone must take 30–60 minutes")

        capability = unit.get("capability")
        if capability not in CAPABILITIES:
            errors.append(f"{lesson_id}: invalid capability {capability!r}")
        reference = unit.get("source_reference", {})
        ref_start, ref_end = reference.get("start"), reference.get("end")
        if not all(isinstance(v, (int, float)) for v in (ref_start, ref_end)):
            errors.append(f"{lesson_id}: source_reference.start/end must be numeric")
        elif (all(isinstance(v, (int, float)) for v in (range_start, range_end)) and
              (ref_start < range_start or ref_end <= ref_start or ref_end > range_end)):
            errors.append(f"{lesson_id}: source_reference falls outside video range")

        unit_skills = unit.get("skills")
        if not isinstance(unit_skills, list) or not unit_skills:
            errors.append(f"{lesson_id}: skills must be a non-empty list")
            unit_skills = []
        for skill_id in unit_skills:
            if not nonempty(skill_id):
                errors.append(f"{lesson_id}: skills entries must be non-empty skill IDs")
                continue
            used_skills.add(skill_id)
            if skill_id not in skill_set:
                errors.append(f"{lesson_id}: unknown curriculum skill {skill_id}")
            if taxonomy and skill_id not in taxonomy:
                errors.append(f"{lesson_id}: skill not found in taxonomy {skill_id}")
        unit_skills_by_lesson[lesson_id] = {
            skill_id for skill_id in unit_skills if nonempty(skill_id)
        }
        if unit.get("primary_skill") not in unit_skills:
            errors.append(f"{lesson_id}: primary_skill must appear in skills")
        new_skills = unit.get("new_skills")
        if not isinstance(new_skills, list):
            errors.append(f"{lesson_id}: new_skills must be a list")
            new_skills = []
        if len(new_skills) > 3:
            errors.append(f"{lesson_id}: introduces more than 3 new skills; split the lesson")
        for skill_id in new_skills:
            if not nonempty(skill_id):
                errors.append(f"{lesson_id}: new_skills entries must be non-empty skill IDs")
                continue
            if skill_id not in unit_skills:
                errors.append(f"{lesson_id}: new skill {skill_id} is absent from skills")
        new_skills_by_lesson[lesson_id] = {
            skill_id for skill_id in new_skills if nonempty(skill_id)
        }

        prerequisites = unit.get("prerequisites")
        if not isinstance(prerequisites, list):
            errors.append(f"{lesson_id}: prerequisites must be a list")
            prerequisites = []
        unit_graph[lesson_id] = prerequisites
        prior = {value for value in lesson_ids[:index] if isinstance(value, str)}
        for prerequisite in prerequisites:
            if not nonempty(prerequisite):
                errors.append(f"{lesson_id}: prerequisites entries must be lesson IDs")
            elif prerequisite not in lesson_id_set:
                errors.append(f"{lesson_id}: unknown prerequisite {prerequisite}")
            elif prerequisite not in prior:
                errors.append(f"{lesson_id}: prerequisite {prerequisite} must appear earlier")

        exercise = unit.get("exercise", {})
        if not nonempty(exercise.get("description")):
            errors.append(f"{lesson_id}: exercise.description is required")
        if not nonempty(exercise.get("deliverable")):
            errors.append(f"{lesson_id}: exercise.deliverable is required")
        if not isinstance(unit.get("steps"), list) or not unit.get("steps"):
            errors.append(f"{lesson_id}: at least one actionable step is required")
        bpm_bad = bpm_instruction_violations(
            yaml.safe_dump(unit, allow_unicode=True, sort_keys=False)
        )
        if bpm_bad:
            errors.append(
                f"{lesson_id}: unverified numeric BPM used as an editing command: "
                + " | ".join(bpm_bad)
            )

        checkpoints = unit.get("checkpoints")
        if not isinstance(checkpoints, dict):
            errors.append(f"{lesson_id}: checkpoints must be a mapping")
            checkpoints = {}
        for checkpoint_type in CHECKPOINT_TYPES:
            conditions = checkpoints.get(checkpoint_type)
            if not isinstance(conditions, list) or not conditions:
                errors.append(f"{lesson_id}: checkpoint {checkpoint_type} is required")
                continue
            for condition in conditions:
                if not isinstance(condition, dict) or not nonempty(condition.get("pass")):
                    errors.append(f"{lesson_id}: {checkpoint_type} condition needs a PASS statement")

        tutorials = unit.get("tutorials", {})
        topics = tutorials.get("topics") if isinstance(tutorials, dict) else None
        if not isinstance(topics, list) or not topics or not all(nonempty(v) for v in topics):
            errors.append(f"{lesson_id}: tutorials.topics requires at least one topic")
        recommended = tutorials.get("recommended", []) if isinstance(tutorials, dict) else []
        if not isinstance(recommended, list):
            errors.append(f"{lesson_id}: tutorials.recommended must be a list")
            recommended = []
        elif len(recommended) > 3:
            errors.append(f"{lesson_id}: no more than 3 recommended tutorials")
        for tutorial in recommended:
            if not isinstance(tutorial, dict):
                errors.append(f"{lesson_id}: recommended tutorial must be a mapping")
                continue
            if not all(nonempty(tutorial.get(field)) for field in ("title", "url", "language")):
                errors.append(f"{lesson_id}: tutorial needs title, url, and language")
            if not re.fullmatch(r"https://[^\s]+", str(tutorial.get("url", ""))):
                errors.append(f"{lesson_id}: tutorial URL must use https")
            if tutorial.get("verified") is not True:
                errors.append(f"{lesson_id}: recommended tutorial must be verified before embedding")
            if not valid_iso_date(tutorial.get("snapshot_date")):
                errors.append(f"{lesson_id}: tutorial snapshot_date must be a real YYYY-MM-DD date")
            section = tutorial.get("relevant_section")
            if not isinstance(section, dict):
                errors.append(f"{lesson_id}: tutorial relevant_section must have start/end")
            else:
                section_start = timecode_seconds(section.get("start"))
                section_end = timecode_seconds(section.get("end"))
                if section_start is None or section_end is None or section_end <= section_start:
                    errors.append(f"{lesson_id}: tutorial relevant_section must be ordered MM:SS/HH:MM:SS")
            teaches = tutorial.get("teaches")
            if (not isinstance(teaches, list) or not teaches or
                    not any(skill_id in unit_skills_by_lesson.get(lesson_id, set())
                            for skill_id in teaches)):
                errors.append(f"{lesson_id}: tutorial teaches must overlap this unit's skills")

        expected_next = lesson_ids[index + 1] if index + 1 < len(lesson_ids) else None
        if unit.get("next") != expected_next:
            errors.append(f"{lesson_id}: next must be {expected_next!r}")

    cycle = find_cycle(unit_graph)
    if cycle:
        errors.append("lesson prerequisite cycle: " + " -> ".join(cycle))

    introduced_by = {}
    for lesson_id, introduced in new_skills_by_lesson.items():
        for skill_id in introduced:
            if skill_id in introduced_by:
                errors.append(
                    f"skill {skill_id} is introduced more than once: "
                    f"{introduced_by[skill_id]}, {lesson_id}"
                )
            else:
                introduced_by[skill_id] = lesson_id
    for skill_id in skill_set:
        if skill_id not in introduced_by:
            errors.append(f"curriculum skill has no introducing unit: {skill_id}")

    def prerequisite_closure(lesson_id):
        closure = set()
        pending = list(unit_graph.get(lesson_id, []))
        while pending:
            prerequisite = pending.pop()
            if prerequisite in closure:
                continue
            closure.add(prerequisite)
            pending.extend(unit_graph.get(prerequisite, []))
        return closure

    for lesson_id in units:
        available = set(new_skills_by_lesson.get(lesson_id, set()))
        for prerequisite in prerequisite_closure(lesson_id):
            available.update(new_skills_by_lesson.get(prerequisite, set()))
        for skill_id in unit_skills_by_lesson.get(lesson_id, set()):
            if skill_id not in available:
                errors.append(
                    f"{lesson_id}: skill {skill_id} is not introduced by this unit or its prerequisite closure"
                )
            for dependency in skill_graph.get(skill_id, []):
                if dependency not in available:
                    errors.append(
                        f"{lesson_id}: dependency {dependency} for {skill_id} is absent from prerequisite closure"
                    )

    validate_human_curriculum(path, lesson_ids, units, errors)

    if units_dir.exists():
        expected_files = {f"{lesson_id}.yaml" for lesson_id in lesson_ids if isinstance(lesson_id, str)}
        extra_files = sorted(p.name for p in units_dir.glob("*.yaml") if p.name not in expected_files)
        if extra_files:
            warnings.append("unreferenced unit files: " + ", ".join(extra_files))

    capstone = curriculum.get("capstone")
    if not isinstance(capstone, dict):
        errors.append("capstone is required")
    else:
        capstone_lesson = capstone.get("lesson")
        if not lesson_ids or capstone_lesson != lesson_ids[-1]:
            errors.append("capstone.lesson must be the final lesson")
        elif units.get(capstone_lesson, {}).get("type") != "capstone":
            errors.append("capstone lesson unit must have type: capstone")
        if not nonempty(capstone.get("deliverable")):
            errors.append("capstone.deliverable is required")
        target = capstone.get("target_range", {})
        target_start, target_end = target.get("start"), target.get("end")
        if not all(isinstance(v, (int, float)) for v in (target_start, target_end)):
            errors.append("capstone.target_range.start/end must be numeric")
        elif (all(isinstance(v, (int, float)) for v in (range_start, range_end)) and
              (target_start < range_start or target_end <= target_start or target_end > range_end)):
            errors.append("capstone target range falls outside video range")

    unused_skills = sorted(skill_set - used_skills)
    if unused_skills:
        warnings.append("curriculum skills unused by units: " + ", ".join(unused_skills))
    info.append(f"lessons={len(lesson_ids)}, skills={len(skill_set)}, used_skills={len(used_skills)}")
    if strict and warnings:
        errors.extend(f"strict: {warning}" for warning in warnings)
    return errors, warnings, info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("curriculum", type=Path, help="path to curriculum.yaml")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()
    errors, warnings, info = validate_curriculum(args.curriculum.resolve(), args.strict)
    print("== curriculum validation ==")
    for item in info:
        print(f"  [info] {item}")
    for item in warnings:
        print(f"  [WARN] {item}")
    for item in errors:
        print(f"  [FAIL] {item}")
    if errors:
        print("\nFAIL — fix reported issues and re-run")
        return 1
    print("  [OK] human curriculum, schema, skill graph, lesson graph, exercises, checkpoints, tutorials, capstone")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
