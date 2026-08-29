# Unit Schema v2.0

每个 `units/Lxx.yaml` 表示一次 10–25 分钟的普通微课程，或一次 30–60 分钟的综合/Capstone 课程。

```yaml
id: L03
title: 圆形 Match Cut
type: micro
goal: 学会用位置和缩放完成形状连续的硬切。
primary_skill: match-cut
new_skills: [match-cut]
skills: [match-cut, position, scale]
prerequisites: [L01, L02]
estimated_minutes: 20
source_reference: {start: 1.88, end: 3.08}
capability: PR-native
assets:
  required: [source-A, source-B]
exercise:
  description: 使用两个圆形主体制作一次 Match Cut。
  deliverable: 一个无空帧、中心连续的切点
steps:
  - id: step-1
    instruction: 把两个素材相邻放在 V1。
    verify: {type: timeline}
checkpoints:
  structural:
    - id: adjacent-clips
      pass: 两个 Clip 相邻且没有空帧
  parameter:
    - id: motion-adjusted
      pass: 至少调整 Position 或 Scale
  visual:
    - id: center-continuity
      pass: 播放确认切点前后主体中心偏移不明显
tutorials:
  topics: [premiere match cut, premiere position scale]
  recommended:
    - title: 已核实的教程标题
      url: https://example.com/tutorial
      language: zh
      verified: true
      snapshot_date: "2026-08-28"
      relevant_section: {start: "02:14", end: "05:40"}
      teaches: [match-cut, position, scale]
challenge: 换一组圆形物体重做。
next: L04
```

## 约束

- 只有一个 `primary_skill`；`new_skills` 不超过 3 个，复杂效果必须拆课。
- 每课必须产生 `exercise.deliverable`，不能只要求“理解”。
- 三类 checkpoint 都必须存在并写明可观察的 `pass` 条件。
- `tutorials.topics` 至少一项；`tutorials.recommended` 如存在，最多 3 个，必须带已核实快照日期、HTTPS URL、与本课 skill 相交的 `teaches`，以及经过人工确认的 `{start, end}` 时间段。timestamp 不确定时不要创建 `recommended`，只保留检索 topic。
- `capability` 只能是 `PR-native`、`PR-approximation`、`AE-preferred` 或 `3D-source-required`。
- 视觉 checkpoint 是辅助判断，不得伪造像素相似度或把结构通过冒充视觉通过。
