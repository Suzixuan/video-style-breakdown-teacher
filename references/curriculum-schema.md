# Curriculum Schema v2.0

Curriculum 模式同时交付三层内容：

- `lesson.md`：兼容 v0.1 的人读拆片报告，解释参考片证据与转场推理；
- `curriculum.md`：人读课程路线和课次入口；
- `course/README.md` + `course/Lxx.md`：学习者直接阅读和操作的完整课件；
- `curriculum.yaml` + `units/*.yaml`：机器可读的课程地图和逐课数据。

不允许只交付 YAML 或摘要；README 和最终回复应优先链接 `course/README.md`。

## 人读课程必填结构

- `curriculum.md` 覆盖全部课次并链接对应 `course/Lxx.md`；
- `course/README.md` 说明素材、序列规格、学习顺序和当前交互边界；
- 每个 `course/Lxx.md` 至少包含 `你会做出什么`、`跟我做`、`你现在应该看到`、`做错了怎么修`、`交作业`、`继续学习`、`能力边界`；
- 每个课件至少包含五条编号操作，且引用对应证据或明确说明本课是综合/原创实践。

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
- 同目录必须存在 `curriculum.md`、`course/README.md` 和全部 `course/Lxx.md` 实操课件。

运行：

```powershell
python scripts/validate_curriculum.py lessons/<video-id>/curriculum.yaml --strict
```
