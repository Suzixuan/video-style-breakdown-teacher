# Curriculum Schema v2.0

Curriculum 模式同时交付三层内容：

- `lesson.md`：兼容 v0.1 的人读拆片报告，解释参考片证据与转场推理；
- `curriculum.md`：学习者直接阅读和练习的完整课程；
- `curriculum.yaml` + `units/*.yaml`：机器可读的课程地图和逐课数据。

不允许只交付 YAML；README 和最终回复应优先链接 `curriculum.md`。

## curriculum.md 必填结构

- 一个课程标题和使用说明；
- 覆盖 `curriculum.yaml.lessons` 中的全部课次，标题格式为 `## Lxx｜课程标题`；
- 每课至少包含 `目标`、`本课作品`、`结构 PASS`、`参数 PASS`、`视觉 PASS`、`能力边界`；
- 人读标题必须与对应 `units/Lxx.yaml` 的 `title` 一致。

## 必填字段

```yaml
version: "2.0"
course_id: example
taxonomy: ../../references/skill-taxonomy.md
video:
  id: example
  range: {start: 0.0, end: 30.0}
  fps: 25
goal:
  description: 最终作品目标
difficulty:
  overall: beginner-intermediate
skills:
  - id: position
    name: Position
    level: beginner
    requires: []
lessons: [L01, L02]
capstone:
  lesson: L02
  target_range: {start: 1.36, end: 4.72}
```

## 约束

- `course_id`、skill ID、lesson ID 唯一；lesson ID 对应 `units/<ID>.yaml`。
- `skills[].requires` 只能引用课程内 skill，且依赖图无环。
- `lessons` 按教学顺序排列；Unit 的 prerequisite 只能指向它前面的 Unit。
- `capstone.lesson` 必须是最后一课，且目标时间段落在分析范围内。
- 所有课程 skill 必须出现在 `taxonomy` 指向的表中。
- 同目录必须存在 `curriculum.md`，并完整覆盖机器课程地图中的所有课次和三类 PASS。

运行：

```powershell
python scripts/validate_curriculum.py lessons/<video-id>/curriculum.yaml --strict
```
