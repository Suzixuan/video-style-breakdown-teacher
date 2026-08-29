import tempfile
import unittest
from pathlib import Path
import shutil

import yaml

from scripts.validate_curriculum import (
    find_cycle,
    taxonomy_graph,
    taxonomy_ids,
    validate_curriculum,
)


class CurriculumValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.course = cls.repo / "lessons" / "pS_L7x9PaY1vXXSh"

    def test_detects_dependency_cycle(self):
        self.assertEqual(find_cycle({"a": ["b"], "b": ["a"]}), ["a", "b", "a"])

    def test_accepts_acyclic_graph(self):
        self.assertIsNone(find_cycle({"a": [], "b": ["a"], "c": ["b"]}))

    def test_reads_only_canonical_taxonomy_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "taxonomy.md"
            path.write_text(
                "| Skill ID | Category |\n| --- | --- |\n| `position` | Motion |\n"
                "Text with `not-a-row` should not count.\n",
                encoding="utf-8",
            )
            errors = []
            self.assertEqual(taxonomy_ids(path, errors), {"position"})
            self.assertEqual(errors, [])

    def test_reads_taxonomy_dependencies(self):
        errors = []
        graph = taxonomy_graph(
            self.repo / "references" / "skill-taxonomy.md", errors
        )
        self.assertEqual(graph["match-cut"], ["position", "scale", "hard-cut"])
        self.assertEqual(graph["timeline-navigation"], [])
        self.assertEqual(errors, [])

    def test_yaml_library_preserves_null_next(self):
        self.assertIsNone(yaml.safe_load("next: null\n")["next"])

    def copy_course(self, temp):
        root = Path(temp)
        course = root / "lessons" / "sample"
        references = root / "references"
        course.mkdir(parents=True)
        shutil.copy2(self.course / "curriculum.yaml", course)
        shutil.copy2(self.course / "curriculum.md", course)
        shutil.copytree(self.course / "units", course / "units")
        references.mkdir(parents=True)
        shutil.copy2(self.repo / "references" / "skill-taxonomy.md", references)
        curriculum_path = course / "curriculum.yaml"
        curriculum = yaml.safe_load(curriculum_path.read_text(encoding="utf-8"))
        curriculum["taxonomy"] = "../../references/skill-taxonomy.md"
        curriculum_path.write_text(
            yaml.safe_dump(curriculum, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        return curriculum_path

    def mutate_unit(self, curriculum_path, lesson_id, mutate):
        unit_path = curriculum_path.parent / "units" / f"{lesson_id}.yaml"
        unit = yaml.safe_load(unit_path.read_text(encoding="utf-8"))
        mutate(unit)
        unit_path.write_text(
            yaml.safe_dump(unit, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def test_full_sample_curriculum_passes_strict_validation(self):
        errors, warnings, _ = validate_curriculum(
            self.course / "curriculum.yaml", strict=True
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_rejects_missing_human_readable_curriculum(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            (curriculum_path.parent / "curriculum.md").unlink()
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertTrue(
                any("human-readable curriculum.md is required" in error for error in errors),
                errors,
            )

    def test_rejects_incomplete_human_lesson(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            human_path = curriculum_path.parent / "curriculum.md"
            text = human_path.read_text(encoding="utf-8")
            text = text.replace("**视觉 PASS**", "**视觉检查**", 1)
            human_path.write_text(text, encoding="utf-8")
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertIn(
                "curriculum.md L01 missing learner section: **视觉 PASS**", errors
            )

    def test_rejects_lesson_prerequisite_cycle(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            self.mutate_unit(
                curriculum_path, "L01", lambda unit: unit.update(prerequisites=["L12"])
            )
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertTrue(any("prerequisite" in error for error in errors), errors)

    def test_rejects_missing_visual_checkpoint(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            self.mutate_unit(
                curriculum_path,
                "L03",
                lambda unit: unit["checkpoints"].pop("visual"),
            )
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertIn("L03: checkpoint visual is required", errors)

    def test_rejects_missing_structural_parameter_and_empty_pass(self):
        mutations = {
            "structural": lambda unit: unit["checkpoints"].pop("structural"),
            "parameter": lambda unit: unit["checkpoints"].pop("parameter"),
            "empty PASS": lambda unit: unit["checkpoints"]["visual"][0].update({"pass": ""}),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                curriculum_path = self.copy_course(temp)
                self.mutate_unit(curriculum_path, "L03", mutate)
                errors, _, _ = validate_curriculum(curriculum_path, strict=True)
                self.assertTrue(any("checkpoint" in error or "PASS" in error for error in errors), errors)

    def test_rejects_skill_cycle(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            curriculum = yaml.safe_load(curriculum_path.read_text(encoding="utf-8"))
            curriculum["skills"][0]["requires"] = ["beat-cutting"]
            curriculum_path.write_text(
                yaml.safe_dump(curriculum, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertTrue(any("skill dependency cycle" in error for error in errors), errors)

    def test_rejects_curriculum_dependency_drift_from_taxonomy(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            curriculum = yaml.safe_load(curriculum_path.read_text(encoding="utf-8"))
            match_cut = next(row for row in curriculum["skills"] if row["id"] == "match-cut")
            match_cut["requires"] = ["position"]
            curriculum_path.write_text(
                yaml.safe_dump(curriculum, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertTrue(any("dependencies differ from taxonomy" in error for error in errors), errors)

    def test_rejects_unknown_skill_and_missing_taxonomy_entry(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            self.mutate_unit(
                curriculum_path,
                "L03",
                lambda unit: unit["skills"].append("invented-preset"),
            )
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertTrue(any("unknown curriculum skill invented-preset" in error for error in errors), errors)
            self.assertTrue(any("taxonomy invented-preset" in error for error in errors), errors)

    def test_rejects_missing_exercise_and_capstone(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            self.mutate_unit(
                curriculum_path,
                "L03",
                lambda unit: unit["exercise"].update(deliverable=""),
            )
            curriculum = yaml.safe_load(curriculum_path.read_text(encoding="utf-8"))
            del curriculum["capstone"]
            curriculum_path.write_text(
                yaml.safe_dump(curriculum, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertIn("L03: exercise.deliverable is required", errors)
            self.assertIn("capstone is required", errors)

    def test_rejects_more_than_three_new_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            self.mutate_unit(
                curriculum_path,
                "L01",
                lambda unit: unit["new_skills"].append("position"),
            )
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertTrue(any("more than 3 new skills" in error for error in errors), errors)

    def test_rejects_skill_absent_from_prerequisite_closure(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            self.mutate_unit(
                curriculum_path,
                "L09",
                lambda unit: unit.update(prerequisites=["L08"]),
            )
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertTrue(any("skill opacity is not introduced" in error for error in errors), errors)

    def test_rejects_unverified_bpm_editing_command(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            self.mutate_unit(
                curriculum_path,
                "L10",
                lambda unit: unit["steps"][0].update(
                    instruction="按 252.1 BPM 自动铺设所有 PR 标记。"
                ),
            )
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertTrue(any("numeric BPM" in error for error in errors), errors)

    def test_rejects_unverified_or_malformed_tutorial(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            bad_tutorial = {
                "title": "Bad tutorial",
                "url": "not-a-url",
                "language": "en",
                "verified": False,
                "snapshot_date": "today",
                "relevant_section": {"start": "later", "end": "earlier"},
                "teaches": ["unrelated-skill"],
            }
            self.mutate_unit(
                curriculum_path,
                "L03",
                lambda unit: unit["tutorials"].update(recommended=[bad_tutorial]),
            )
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            expected = ("URL must use https", "must be verified", "snapshot_date", "relevant_section", "teaches")
            for fragment in expected:
                self.assertTrue(any(fragment in error for error in errors), (fragment, errors))

    def test_rejects_impossible_tutorial_snapshot_date(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            tutorial = {
                "title": "Verified title",
                "url": "https://example.com/tutorial",
                "language": "en",
                "verified": True,
                "snapshot_date": "2026-99-99",
                "relevant_section": {"start": "02:14", "end": "05:40"},
                "teaches": ["match-cut"],
            }
            self.mutate_unit(
                curriculum_path,
                "L03",
                lambda unit: unit["tutorials"].update(recommended=[tutorial]),
            )
            errors, _, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertTrue(any("real YYYY-MM-DD" in error for error in errors), errors)

    def test_accepts_verified_structured_tutorial(self):
        with tempfile.TemporaryDirectory() as temp:
            curriculum_path = self.copy_course(temp)
            tutorial = {
                "title": "Verified title",
                "url": "https://example.com/tutorial",
                "language": "en",
                "verified": True,
                "snapshot_date": "2026-08-28",
                "relevant_section": {"start": "02:14", "end": "05:40"},
                "teaches": ["match-cut"],
            }
            self.mutate_unit(
                curriculum_path,
                "L03",
                lambda unit: unit["tutorials"].update(recommended=[tutorial]),
            )
            errors, warnings, _ = validate_curriculum(curriculum_path, strict=True)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
