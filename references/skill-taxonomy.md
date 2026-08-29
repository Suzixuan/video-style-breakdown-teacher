# Premiere 微课程 Skill Taxonomy v0.2

本表是 `curriculum.yaml` 与 `units/*.yaml` 可引用技能 ID 的唯一来源。它描述教学依赖，不声称 Premiere 能生成原片中的 3D 或预渲染动画。

| Skill ID | 分类 | 中文名 | 建议前置 |
| --- | --- | --- | --- |
| `timeline-navigation` | Timeline | 时间线与播放头 | — |
| `razor-cut` | Timeline | 剃刀与帧级切割 | timeline-navigation |
| `trim` | Timeline | 修剪 | timeline-navigation |
| `track-management` | Timeline | 轨道管理 | timeline-navigation |
| `markers` | Timeline | 手工标记 | timeline-navigation |
| `position` | Motion | 位置 | timeline-navigation |
| `scale` | Motion | 缩放 | timeline-navigation |
| `keyframes` | Motion | 关键帧 | position, scale |
| `bezier` | Motion | Bezier 速度曲线 | keyframes |
| `ease` | Motion | 缓入缓出 | keyframes |
| `hard-cut` | Transition | 硬切 | razor-cut |
| `match-cut` | Transition | 形状匹配剪辑 | position, scale, hard-cut |
| `push-transition` | Transition | 推进转场 | keyframes |
| `mask-transition` | Transition | 蒙版转场 | keyframes, mask |
| `speed-ramp` | Transition | 速度重映射 | keyframes |
| `opacity` | Compositing | 不透明度 | timeline-navigation |
| `blend-mode` | Compositing | 混合模式 | opacity |
| `mask` | Compositing | 蒙版 | opacity |
| `adjustment-layer` | Compositing | 调整图层 | track-management |
| `rgb-split` | Compositing | RGB 通道错位 | adjustment-layer |
| `invert` | Compositing | 正负片闪变 | adjustment-layer |
| `hud-overlay` | Compositing | HUD 叠加 | blend-mode |
| `waveform` | Audio | 波形阅读 | timeline-navigation |
| `beat-cutting` | Audio | 手工听拍剪辑 | waveform, markers, razor-cut |
| `lumetri-basics` | Color | Lumetri 基础 | adjustment-layer |
| `contrast` | Color | 对比度控制 | lumetri-basics |

## 使用边界

- 一课只能声明一个 `primary_skill`，并最多引入三个 `new_skills`；辅助技能可复用已通过技能。
- 机械虹膜、表芯内部穿行和真实三维透视属于 `3D-source-required`；本 taxonomy 只覆盖 PR 中的选材、定时、近似蒙版与合成。
- 依赖图由课程按参考视频实际需要裁剪，不要求学习者先学完整 Premiere 历史或全部工具。
