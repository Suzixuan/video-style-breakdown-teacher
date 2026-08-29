# Curriculum Schema v2.0

`curriculum.yaml` 是机器可读的课程地图；`lesson.md` 仍是兼容 v0.1 的人读拆片报告。

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

运行：

```powershell
python scripts/validate_curriculum.py lessons/<video-id>/curriculum.yaml --strict
```
