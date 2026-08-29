# Video Style Breakdown Teacher

把任意视频的剪辑风格拆解成一份可教学的 Premiere Pro 教案，并进一步编排为有依赖关系、可实践、可验收的微课程。当前版本：**v0.2.0 Interactive Curriculum**。

本仓库是一个**长期学习与更新**的仓库：技能脚本、教案模板、已拆解的课程都会持续沉淀在这里。

## 特性

- **证据先行**：场景检测、事件表拼图、音频波形、节拍候选全部由脚本自动生成（`analysis_manifest.json` 统一定义）。
- **三种分析模式**：`quick`（约10k–25k tokens）、`teacher`（默认，约30k–70k tokens）、`forensic`（逐源帧，>80k tokens）。
- **教程检索**：自动收集 YouTube/Bilibili 教程并按相关度＋播放量排名；B 站遇 HTTP 412 时如实标注 `unverified`，绝不编造播放量。
- **质量校验**：`validate_lesson.py` 检查教案结构完整性（13 项子节闭环）与负面守卫（不声称还原原作者精确预设、不把未核实BPM直接变成打标命令）。
- **课程编排**：`curriculum.md` 是路线入口，`course/Lxx.md` 是逐步实操课件，`curriculum.yaml` 与 `units/*.yaml` 负责 skill graph 和机器校验。
- **课程校验**：`validate_curriculum.py` 检查人读课程完整性、依赖环、悬空引用、练习交付物、三类 PASS checkpoint、教程主题与 Capstone。
- **诚实边界**：明确区分 PR-native / PR-approximation / AE-preferred / 3D-source-required，不把 PR 描述成"一键 3D 特效"。

> v0.2 尚未连接 Premiere MCP：它能生成和校验课程，但不能读取或修改用户的 PR 工程。MCP 只读 Coach 是后续版本。

## 目录结构

```
video-style-breakdown-teacher/
├── SKILL.md                  # 技能入口（可直接作为 Codex 技能安装）
├── HANDOFF.md                # 内部交接文档（换电脑继续工作的说明）
├── agents/openai.yaml        # 技能 UI 元数据
├── scripts/                  # 证据、教程与校验脚本
│   ├── analyze_video.py      # 证据包生成（场景/概览/事件/波形/节拍/manifest）
│   ├── collect_tutorials.py  # YouTube/Bilibili 教程检索、排名、快照
│   ├── validate_lesson.py    # 教案结构与负面守卫校验
│   └── validate_curriculum.py # 课程依赖与 Unit 校验
├── references/
│   ├── lesson-template.md    # 教案模板（写作必读）
│   ├── skill-taxonomy.md     # canonical skill ID
│   ├── curriculum-schema.md  # 课程地图 schema
│   ├── unit-schema.md        # 微课程 schema
│   └── coach-behavior.md     # Coach 行为与版本边界
├── examples/                 # 样例产出（teacher 模式 + quick 模式）
└── lessons/                  # 已拆解的课程（长期累积）
    └── pS_L7x9PaY1vXXSh/     # 证据拆解 + course/12课实操 + 机器课程文件
```

## 快速开始

### 环境要求

- Python 3.10+；PyYAML 为课程校验必需，建议安装 Pillow（拼图与波形）
- `ffmpeg` / `ffprobe` 在 PATH
- 可选：`yt-dlp`（教程收集的实时元数据）

安装（Windows 示例）：

```bash
winget install Gyan.FFmpeg
python -m pip install --user pillow pyyaml yt-dlp
```

> 中文 Windows 下运行脚本请加 `PYTHONUTF8=1`，否则 Python 可能用 GBK 读取 UTF-8 文件报错。

### 拆解一个视频

```bash
# 1. 生成证据包（teacher 模式，前 30 秒）
python scripts/analyze_video.py 视频.mp4 --out 输出目录 --mode teacher \
  --range-start 0 --range-end 30 --user-focus 1.4 2.48 4.2 7.4 10.4 21.4

# 2. 收集教程链接（每个主题一条 --queries）
python scripts/collect_tutorials.py --out 输出目录 \
  --queries "match-cut:Premiere Pro match cut transition tutorial" \
  --queries "rgb-glitch:Premiere Pro glitch RGB split tutorial"

# 3. 按 references/lesson-template.md 写 lesson.md

# 4. 校验
python scripts/validate_lesson.py 输出目录/lesson.md \
  --manifest 输出目录/evidence/analysis_manifest.json

# Curriculum 模式先写课程路线、course/Lxx.md、机器地图与 Units，再运行
python scripts/validate_curriculum.py 输出目录/curriculum.yaml --strict
```

校验通过（exit 0）才算完成。

## 已收录课程

| 课程 | 视频 | 内容 |
|---|---|---|
| [pS_L7x9PaY1vXXSh](lessons/pS_L7x9PaY1vXXSh/lesson.md) | 黑白金科幻产品广告（1080×1920, 25fps, 前30秒）；源视频需由学习者在本地合法取得，不随公开仓库分发 | [直接上 12 课 Premiere 实操课](lessons/pS_L7x9PaY1vXXSh/course/README.md)：每课包含界面路径、逐步操作、应见结果、故障修复和交作业；[课程路线](lessons/pS_L7x9PaY1vXXSh/curriculum.md)；[机器地图](lessons/pS_L7x9PaY1vXXSh/curriculum.yaml) |

> 证据拼图包含低分辨率参考帧，仅用于评论、教学与课程复核。源视频不随公开仓库分发；使用者应自行确认其素材取得和使用权限。

## 脚本说明

- **analyze_video.py**：`ffprobe` 读取源参数 → 场景检测（归一化像素差，0.3 阈值，0.5s 内聚簇）→ 概览/事件拼图 → 波形 → 能量 onset 自相关的节拍候选 → 写 `analysis_manifest.json`（schema 1.0）。
- **collect_tutorials.py**：按主题分组；YouTube 用 yt-dlp 拉实时元数据，B 站从网页搜索 JSON 取候选再尝试补充；评分 = 标题相关度 ×0.7 + 对数播放量 ×0.3。
- **validate_lesson.py**：检查 9 个顶层章节、每节转场课的 13 个子节、负面守卫（精确原片预设断言、未核实BPM打标指令）、manifest 一致性。
- **validate_curriculum.py**：读取人读课程、机器课程地图、taxonomy 与全部 Unit，检查每课标题和 PASS 内容、技能/课程图、课程顺序、时长、练习、tutorial topic 与最终 Capstone。

## 长期维护约定

- 新视频拆解：按上面的流程产出后，把 `lesson.md` + `evidence/` 放进 `lessons/<视频名>/`；Curriculum 模式还必须加入 `curriculum.md`、`course/`、`curriculum.yaml` 与 `units/`。
- 技能更新：改 `SKILL.md`、`scripts/`、`references/` 后跑 `quick_validate.py` 与脚本实测再提交。
- 推送到 GitHub 一律走分支 + Pull Request，不直接推 `main`；合入 `main` 需仓库维护者确认。
- 教程播放量只是检索日快照，引用前请打开确认内容。

## License

代码、脚本和本仓库原创文本采用 MIT License，详情见 [LICENSE](LICENSE)。第三方视频内容、品牌、画面角色以及从参考视频抽取的证据帧不因本仓库的 MIT License 获得授权，相关权利仍属于各自权利人。
