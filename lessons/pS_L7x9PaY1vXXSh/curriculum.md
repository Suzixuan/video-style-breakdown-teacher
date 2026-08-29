# pS_L7x9PaY1vXXSh：Premiere 12 课课程入口

> 这里是课程入口，不再用几段摘要冒充教学。请打开 [完整 12 课实操课](course/README.md)，从 L01 开始逐步操作。

## 课程怎么组织

```text
参考视频证据
  ↓
基础技能：帧级切割、构图对齐
  ↓
组合技能：Match Cut、关键帧、Bezier、Mask
  ↓
包装技能：Invert、RGB Split、HUD
  ↓
节奏组织：手工标记与卡点
  ↓
综合复刻 → 原创 5 秒 Capstone
```

| 课次 | 实操课 | 完成后能证明什么 |
|---|---|---|
| L01 | [帧级短切](course/L01.md) | 能准确做出 2 / 4 / 2 帧插入，而不是凭感觉说“快一点” |
| L02 | [Position / Scale 对齐](course/L02.md) | 能用叠加检查两个主体的圆心和尺寸 |
| L03 | [圆形 Match Cut](course/L03.md) | 不依赖转场插件也能让三个镜头接顺 |
| L04 | [8 帧关键帧推进](course/L04.md) | 能建立并检查两个 Scale 关键帧 |
| L05 | [Bezier 加速度](course/L05.md) | 能区分起止值与中间速度曲线 |
| L06 | [圆形 Mask Transition](course/L06.md) | 能用椭圆蒙版揭示目标素材且不出现灰边 |
| L07 | [Adjustment Layer + Invert](course/L07.md) | 能做可关闭、非破坏性的 1–2 帧反相 |
| L08 | [6 帧 RGB Split](course/L08.md) | 能把故障限制在短窗口并保持主体可读 |
| L09 | [HUD 合成](course/L09.md) | 能建立人物、故障、界面的视觉层级 |
| L10 | [手工卡点](course/L10.md) | 能用耳朵、波形、标记共同决定切点 |
| L11 | [综合复刻](course/L11.md) | 能分结构、运动、接缝三遍完成 3.36 秒片段 |
| L12 | [原创 Capstone](course/L12.md) | 能把参考片语言迁移成原创 5 秒作品 |

## 当前交互边界

本任务没有暴露 Premiere MCP，也没有可调用的 `capture_frame`、`export_frame`、Sequence 或 Timeline 工具。因此课程能教你操作、规定截图和验收标准，但不能声称已经读取或检查你的 Premiere 工程。你提交时间线与 Program Monitor 截图后，才可以进行基于证据的人工复核。

参考片为什么这样剪，见 [逐转场证据拆解](lesson.md)；机器课程地图见 [curriculum.yaml](curriculum.yaml)。
