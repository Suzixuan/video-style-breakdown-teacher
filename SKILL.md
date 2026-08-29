---
name: video-style-breakdown-teacher
description: "视频风格拆解与 Premiere 微课程编排（Video Style Breakdown Teacher）。Use when the user asks to analyze a reference video's editing style, identify effects or transitions, learn Premiere from that reference, or turn the evidence into a prerequisite-aware curriculum with practical exercises and PASS checkpoints. Produces an evidence-backed lesson plus a human-readable curriculum.md, curriculum.yaml, and units/*.yaml when Curriculum mode is requested; distinguishes PR-native approximations from effects that require After Effects, 3D, plug-ins, or source animation. Triggers include 视频拆解、剪辑风格分析、转场拆解、Premiere 教学、PR 私人教练、课程路线、break down this video's editing, teach this video's style."
---

# Video Style Breakdown Teacher

Current release: **0.2.0 — Interactive Curriculum**.

把任意视频的片段（默认前 30 秒）拆解成可教学的 Premiere 教案，并在 Curriculum 模式下把复杂效果拆成有依赖关系、可操作、可验收的微课程。先产出视觉与音频证据，再推理；Python 负责 evidence/schema/validation，Codex 负责教育拆解与排课。

v0.1 的 `lesson.md` 工作流继续可用。v0.2 不连接 Premiere MCP，也不能声称已检查用户工程；交互式只读 Coach 属于后续阶段。

## 锁定决策（不可违反）

1. **证据先于效果名**：先描述在证据帧/波形里看到了什么，再给效果命名；命名只作为假设。
2. **观察 / 推断 / 复刻分离**：教案中必须区分"证据中看到"（观察）、"据此判断"（推断/置信度）、"PR 复刻参数"（复刻），三者不能混写。
3. **每一节转场课必须闭环**：观察→原理→PR 操作→参数起点→为什么→失败修正→迁移→练习→验收→教程→能力边界，缺一不可（`validate_lesson.py` 会检查）。
4. **绝不声称还原原作者精确预设**：只能给"PR 复刻起点"参数；无法从成片确定的插件、预设、轨道结构一律标"无法确定"。
5. **复杂效果先拆能力**：不再默认“一个转场 = 一课”。当效果同时引入超过 3 个新 Premiere 概念时，必须拆成前置微课程与综合课。
6. **教育优先**：每课只有一个主要目标，要求学习者完成实际作品，并提供结构、参数、视觉三类 PASS 条件；默认不替学习者完成练习。

## 选择输出模式

- **Breakdown（兼容 v0.1）**：用户只要拆片报告时，生成 `lesson.md` 并运行 `validate_lesson.py`。
- **Curriculum（v0.2）**：用户要学习路线、微课程或“私人教练”时，在 Breakdown 证据基础上额外生成学习者直接阅读的 `curriculum.md`，以及机器校验用的 `curriculum.yaml` 与 `units/*.yaml`，并运行两种 validator。不得让用户通过阅读 YAML 才能看到完整课程。

Curriculum 模式开始前读取：

- [references/skill-taxonomy.md](references/skill-taxonomy.md)：选择 canonical skill ID 和依赖；
- [references/curriculum-schema.md](references/curriculum-schema.md)：建立课程地图；
- [references/unit-schema.md](references/unit-schema.md)：编写每课练习与 checkpoint；
- [references/coach-behavior.md](references/coach-behavior.md)：保持教育优先和当前无 MCP 的边界。

## 工作流

按顺序执行；每步产出都可独立验证。

### 1. 确定源视频与分析范围

- 用户给视频 → 确认路径与要分析的片段（默认前 30 秒）。
- 确认哪些瞬间是用户关注点（如"01.4 秒那个闪帧"）；其余事件由场景检测自动挑。
- 运行环境：需要 `ffmpeg`/`ffprobe` 在 PATH；Python 3.10+，建议有 Pillow（拼图与波形）。缺依赖时报错信息会说明安装方法，不要假装没有依赖也能分析。

### 2. 生成证据包

运行 `scripts/analyze_video.py`，按模式产出证据：

```bash
python scripts/analyze_video.py 视频.mp4 --out 输出目录 --mode teacher \
  --range-start 0 --range-end 30 --user-focus 1.4 2.48 4.2 7.4 10.4 21.4
```

- `quick`：约 10k–25k tokens，只给 1–2 张概览＋少量事件表，适合快速判断风格。
- `teacher`：约 30k–70k tokens，3 张概览＋6 张事件表＋波形＋节拍候选，默认模式。
- `forensic`：逐源帧核对，通常超过 80k tokens，仅在用户要求逐帧证据时使用。
- 输出 `analysis_manifest.json` + `overview/` + `events/` + `waveform.png`；清单结构见 `examples/sample-first-30s/evidence/analysis_manifest.json`。

### 3. 读证据并逐转场推理

先读 `analysis_manifest.json`（文件都不大），再看对应概览与事件表图片：

- 每个事件表：先看窗口内帧的时间码与采样间隔，再观察中心位置、亮度极性、颜色边缘、形状连续性。
- 用音频 `onset_times` 与 `tempo_candidate_bpm` 对节奏（一拍≈帧数），但注明这是候选不是乐谱。
- 场景检测只是候选：故障闪帧会在一个转场内多次触发，不要把每次检测当独立镜头。
- 只对证据明确支持的环节给高置信；不确定的给中/低置信并说明替代假设。

### 4. 收集教程链接

运行 `scripts/collect_tutorials.py`，为每个主题（如 match cut、RGB split、速度重映射）收集 YouTube/Bilibili 教程并按相关度＋播放量排名：

```bash
python scripts/collect_tutorials.py --out 输出目录 \
  --queries "match-cut:Premiere Pro match cut transition tutorial" \
  --queries "rgb-glitch:Premiere Pro glitch RGB split tutorial"
```

- YouTube 用 yt-dlp 拉实时元数据；Bilibili 可能返回 HTTP 412，此时通过网页搜索补条目并标 `unverified`，禁止编造播放量。
- 产出 `tutorial-research.json` 与 `tutorial-research.md`（快照格式见 `examples/sample-first-30s/tutorial-research-auto/tutorial-research.md`）。
- 模型随后人工打开候选并确认"确实演示了教案用到的那个 PR 控件"，再写进教案；播放量只是日期快照。

### 5. 写教案

严格按 `references/lesson-template.md` 的结构写 `lesson.md`。要点：

- 开头：分析范围、源参数、证据模式、结论摘要（3 条最值得先学原则）。
- 逐转场：每个事件一小节，证据→判断（带置信度）→原理→PR 操作→参数起点→为什么→失败症状→迁移→练习→验收→教程→能力边界。
- PR 复刻工程：序列/轨道建议、搭建顺序、分层练习（10 分钟/30 分钟/迁移挑战）。
- 能力边界：明确哪些是 3D/预渲染源素材，PR 不能凭空制造。
- 闪烁安全提示：片中有 1–2 帧高反差闪帧时，提醒降低预览亮度、减少连续闪烁。
- 链接数量与年份：引用教程时标注检索日期快照；未核实的播放量写"未核实"。

### 6. 校验

```bash
python scripts/validate_lesson.py 输出目录/lesson.md \
  --manifest 输出目录/evidence/analysis_manifest.json
```

校验通过（exit 0）才算完成。失败时按提示修复后重跑，不要跳过。

### 7. Curriculum Compiler（仅 Curriculum 模式）

从参考片最终效果向前寻找真正需要的 prerequisite，而不是从 Premiere 全功能开始讲：

```text
analysis_manifest.json + lesson.md
→ Codex 区分最终效果与基础能力
→ 按 taxonomy 建立 skill graph
→ curriculum.md（完整人读课程）
→ curriculum.yaml（机器课程地图）
→ units/Lxx.yaml
→ validate_curriculum.py
```

编排约束：

- 普通微课程 10–25 分钟，综合/Capstone 30–60 分钟；
- 一课一个 `primary_skill`，最多 3 个 `new_skills`；
- 每课有实际 `exercise.deliverable`、三类 checkpoint 和至少一个 tutorial topic；
- `curriculum.md` 必须覆盖全部课次，并逐课写清目标、本课作品、结构/参数/视觉 PASS 与能力边界；
- README 或最终交付默认链接 `curriculum.md`，不能把 YAML 当作学习者入口；
- 教程按本课 skill 检索，每课最多 1–3 个，相关片段未核实就不编 timestamp；
- Capstone 复刻剪辑语言和原则，不要求像素级复制；
- 3D/预渲染源动画只能作为合法取得的素材输入，不能写成 PR 自己生成。

运行：

```bash
python scripts/validate_curriculum.py 输出目录/curriculum.yaml --strict
```

首次回复不要倾倒全部课程。只概述最终目标、课数、为什么从第一课开始，并邀请用户打开 Premiere；在 v0.2 无 MCP 时，后续只能引导用户按 Unit 自查。

## 能力边界（对用户要诚实）

- 能高置信识别：形状匹配、插帧长度、亮度翻转、RGB 边缘、HUD 叠层、节奏关系。
- 不能仅凭导出片确定：原作者插件、预设、轨道结构、精确参数。
- 机械虹膜、内部穿行、真实反射/透视旋转等明显依赖 3D 或预渲染源素材：标 `3D/source-required`，PR 负责选材、定时、合成与声音。
- 教案参数是"PR 复刻起点"，不是反推的原始参数。

## 资源

- `scripts/analyze_video.py` — 证据包生成（场景检测、概览/事件拼图、波形、节拍候选、manifest）。
- `scripts/collect_tutorials.py` — YouTube/Bilibili 教程检索、排名、快照生成。
- `scripts/validate_lesson.py` — 教案结构与负面守卫校验。
- `scripts/validate_curriculum.py` — 人读课程完整性、课程/技能依赖、Unit 练习、checkpoint、教程主题与 Capstone 校验。
- `references/lesson-template.md` — 教案模板与每节要求（写作时必读）。
- `references/skill-taxonomy.md` — v0.2 canonical skill ID 与依赖。
- `references/curriculum-schema.md`、`references/unit-schema.md` — 人读课程、机器课程地图与 Unit 格式。
- `references/coach-behavior.md` — 教育优先状态机及未来 MCP 权限边界。
- `examples/sample-first-30s/` — teacher 模式完整样例（教案＋证据＋教程快照）。
- `examples/verification-quick/` — quick 模式样例（轻量证据）。
