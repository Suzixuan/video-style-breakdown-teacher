# Video Style Breakdown Teacher

把任意视频的剪辑风格拆解成一份可教学的 Premiere Pro 教案。先产出视觉与音频证据，再逐转场推理，最后按固定模板写课，并用校验脚本守住质量底线。

本仓库是一个**长期学习与更新**的仓库：技能脚本、教案模板、已拆解的课程都会持续沉淀在这里。

## 特性

- **证据先行**：场景检测、事件表拼图、音频波形、节拍候选全部由脚本自动生成（`analysis_manifest.json` 统一定义）。
- **三种分析模式**：`quick`（约10k–25k tokens）、`teacher`（默认，约30k–70k tokens）、`forensic`（逐源帧，>80k tokens）。
- **教程检索**：自动收集 YouTube/Bilibili 教程并按相关度＋播放量排名；B 站遇 HTTP 412 时如实标注 `unverified`，绝不编造播放量。
- **质量校验**：`validate_lesson.py` 检查教案结构完整性（13 项子节闭环）与负面守卫（不声称还原原作者精确预设）。
- **诚实边界**：明确区分 PR-native / PR-approximation / AE-preferred / 3D-source-required，不把 PR 描述成"一键 3D 特效"。

## 目录结构

```
video-style-breakdown-teacher/
├── SKILL.md                  # 技能入口（可直接作为 Codex 技能安装）
├── HANDOFF.md                # 内部交接文档（换电脑继续工作的说明）
├── agents/openai.yaml        # 技能 UI 元数据
├── scripts/                  # 三个可执行脚本
│   ├── analyze_video.py      # 证据包生成（场景/概览/事件/波形/节拍/manifest）
│   ├── collect_tutorials.py  # YouTube/Bilibili 教程检索、排名、快照
│   └── validate_lesson.py    # 教案结构与负面守卫校验
├── references/
│   └── lesson-template.md    # 教案模板（写作必读）
├── examples/                 # 样例产出（teacher 模式 + quick 模式）
└── lessons/                  # 已拆解的课程（长期累积）
    └── pS_L7x9PaY1vXXSh/     # 示例：黑白金科幻产品广告 前30秒拆解
```

## 快速开始

### 环境要求

- Python 3.10+，建议 Pillow（拼图与波形）
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
```

校验通过（exit 0）才算完成。

## 已收录课程

| 课程 | 视频 | 内容 |
|---|---|---|
| [pS_L7x9PaY1vXXSh](lessons/pS_L7x9PaY1vXXSh/lesson.md) | 黑白金科幻产品广告（1080×1920, 25fps, 前30秒），源视频见 [source.mp4](lessons/pS_L7x9PaY1vXXSh/source.mp4) | 6 节逐转场教学：闪帧组接、中心轴匹配、眼睛→机械虹膜、HUD负片故障、正负片→X光线稿、表芯穿行→英雄镜头 |

> 源视频为学习/拆解参考而收录，版权归原作者所有；请勿用于公开分发或商业用途。

## 脚本说明

- **analyze_video.py**：`ffprobe` 读取源参数 → 场景检测（归一化像素差，0.3 阈值，0.5s 内聚簇）→ 概览/事件拼图 → 波形 → 能量 onset 自相关的节拍候选 → 写 `analysis_manifest.json`（schema 1.0）。
- **collect_tutorials.py**：按主题分组；YouTube 用 yt-dlp 拉实时元数据，B 站从网页搜索 JSON 取候选再尝试补充；评分 = 标题相关度 ×0.7 + 对数播放量 ×0.3。
- **validate_lesson.py**：检查 9 个顶层章节、每节转场课的 13 个子节、负面守卫（"原片参数/原作者预设/exact preset"断言）、manifest 一致性。

## 长期维护约定

- 新视频拆解：按上面的流程产出后，把 `lesson.md` + `evidence/` 放进 `lessons/<视频名>/` 再提交。
- 技能更新：改 `SKILL.md`、`scripts/`、`references/` 后跑 `quick_validate.py` 与脚本实测再提交。
- 推送到 GitHub 一律走分支 + Pull Request，不直接推 `main`；合入 `main` 需仓库维护者确认。
- 教程播放量只是检索日快照，引用前请打开确认内容。

## License

MIT License，详情见 [LICENSE](LICENSE)。
