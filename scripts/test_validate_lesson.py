import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_lesson.py")
SPEC = importlib.util.spec_from_file_location("validate_lesson", MODULE_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class BpmInstructionGuardTests(unittest.TestCase):
    def test_rejects_cross_line_marker_grid(self):
        text = "252.1 BPM 未核实。\n按 6 帧打 M 铺满序列。"
        self.assertTrue(VALIDATOR.bpm_instruction_violations(text))

    def test_rejects_adversative_override(self):
        text = "252.1 BPM 不可靠；但仍按它打标记。"
        self.assertTrue(VALIDATOR.bpm_instruction_violations(text))

    def test_rejects_frame_grid_after_unverified_label(self):
        text = "252.1 BPM 未核实，按 6 帧打 M。"
        self.assertTrue(VALIDATOR.bpm_instruction_violations(text))

    def test_rejects_chinese_create_marker_wording(self):
        text = "按 252.1 BPM 每拍创建一个标记。"
        self.assertTrue(VALIDATOR.bpm_instruction_violations(text))

    def test_rejects_english_marker_command(self):
        text = "Set a Marker on every beat at 252.1 BPM."
        self.assertTrue(VALIDATOR.bpm_instruction_violations(text))

    def test_accepts_direct_prohibition(self):
        text = "252.1 BPM 只是候选；不要按 6 帧打 M 铺满序列。"
        self.assertFalse(VALIDATOR.bpm_instruction_violations(text))

    def test_accepts_evidence_without_editing_command(self):
        text = "算法给出252.1 BPM候选，但它不是人工确认的主拍。"
        self.assertFalse(VALIDATOR.bpm_instruction_violations(text))

    def test_accepts_prohibition_followed_by_manual_marking(self):
        text = "不要按252.1 BPM自动铺满标记；先按乐句和强冲击人工打M。"
        self.assertFalse(VALIDATOR.bpm_instruction_violations(text))

    def test_accepts_english_prohibition(self):
        text = "Do not set markers at 252.1 BPM; mark phrases manually."
        self.assertFalse(VALIDATOR.bpm_instruction_violations(text))


if __name__ == "__main__":
    unittest.main()
