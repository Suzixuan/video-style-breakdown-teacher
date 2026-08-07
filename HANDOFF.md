# HANDOFF — 内部交接文档（v0.1.0）

目标读者：**在另一台电脑继续这份工作的人**（人或 AI 助手）。读完本文档 + `README.md` 后，应当能在新机器上独立复现整个拆解流程并继续更新仓库。

## 1. 这是什么

`video-style-breakdown-teacher`：把任意视频前 30 秒的剪辑风格拆解成 Premiere 教学课。核心资产是三个 Python 脚本 + 教案模板 + 已沉淀的课程。

## 2. 关键路径

| 项目 | 路径 |
|---|---|
| 本仓库（本地） | `C:\Users\suzix\repos\video-style-breakdown-teacher` |
| GitHub 公开仓库 | https://github.com/Suzixuan/video-style-breakdown-teacher（公开，默认分支 main，2026-08-07 建立） |
| 已安装的 Codex 技能 | `C:\Users\suzix\.codex\skills\video-style-breakdown-teacher` |
| 技能开发脚手架 | `C:\Users\suzix\.codex\skills\.system\skill-creator`（init_skill.py / quick_validate.py） |
| 源样片 | 本机曾使用：`C:\Users\suzix\Downloads\pS_L7x9PaY1vXXSh.mp4`（1080×1920, 25fps, AAC 44.1kHz, 32.14s，SHA-256 `c712dc89c57fbfd7405688b976cf1d04fb97dd9087784dc82434b698eb387104`）；公开仓库不再分发源视频，复现者需自行提供有权使用的本地素材 |
| 交付包原始副本 | `C:\Users\suzix\Downloads\video-style-breakdown-teacher\...\v0.1.0`（含 HANDOFF/SHA256SUMS/检索 JSON） |

## 3. 环境清单（本机已装，新机器照此装）

- 2026-08-07现场读回：Python 3.13.14（`C:\Users\suzix\AppData\Local\Programs\Python\Python313\python.exe`），PyYAML 6.0.2；当前解释器未安装 Pillow/yt-dlp Python 包，但独立 `yt-dlp.exe` 可用
- 当前终端的 PATH 中没有系统 `ffmpeg`；现有样例曾用临时 `imageio-ffmpeg` 运行。新机器应按 `README.md` 安装正式 FFmpeg 与 Pillow，并用`ffmpeg -version`、`python -m pip show pillow`读回确认
- git 2.54（本仓库分支约定见第 8 节）
- 中文 Windows 注意：**跑任何 Python 脚本加 `PYTHONUTF8=1`**，否则 UTF-8 中文会按 GBK 读取报错

## 4. 技能安装与更新

安装到 `~/.codex/skills/` 后 Codex 会自动发现（触发词：视频拆解、剪辑风格分析、转场拆解、Premiere 教学）。

```bash
# 重新生成骨架（已存在则跳过）
python "C:\Users\suzix\.codex\skills\.system\skill-creator\scripts\init_skill.py" \
  video-style-breakdown-teacher --path "C:\Users\suzix\.codex\skills" \
  --resources scripts,references

# 结构校验（yaml 依赖 pyyaml）
$env:PYTHONUTF8=1; python "C:\Users\suzix\.codex\skills\.system\skill-creator\scripts\quick_validate.py" \
  "C:\Users\suzix\.codex\skills\video-style-breakdown-teacher"
```

更新技能后，同步把改动拷回本仓库（scripts/、SKILL.md、references/、agents/、examples/）。

## 5. 完整工作流（5 步）

1. **定范围**：确认视频路径与分析区间（默认前 30 秒），列出用户关注瞬间（`--user-focus`）。
2. **生成证据包**：`analyze_video.py --mode teacher` → `evidence/`（manifest + 概览 + 事件表 + 波形）。
3. **读证据推理**：先读 manifest，再看概览/事件表；场景检测只是候选，闪帧不独立成镜头；节拍是候选不是乐谱。
4. **收集教程**：`collect_tutorials.py`，B 站候选从网页搜索 JSON 喂入（分组 `{"queries": {topic: [...]}}`）；YouTube 用 yt-dlp。
5. **写教案并校验**：按 `references/lesson-template.md` 写 `lesson.md`，`validate_lesson.py` 通过（exit 0）才算完成。

产出放 `lessons/<视频名>/` 提交入库。

## 6. 脚本行为细节与已知坑

- **场景检测**：5fps 灰度采样，归一化像素差 >0.3 记事件，0.5s 内聚簇；静态素材会产生 0 事件（此时必须靠 `--user-focus` 指定事件）。
- **节拍候选**：能量 onset 自相关；对纯音/密集打击乐可能给出偏高的候选（实测样例 252.1 BPM 而早期版本为 142.9）。教案里一律标注"候选非乐谱"，节奏判断以帧数为准。
- **B 站 412**：yt-dlp 补充元数据遇 HTTP 412 时保留网页搜索条目并标 `unverified`，禁止编造播放量。
- **主题分组**：搜索 JSON 推荐用 `{"queries": {topic: [...]}}`；平铺 `results` 会让所有候选进入每个主题，造成跨主题污染（已在脚本中修正为支持分组）。
- **`quick_validate.py` 在中文 Windows**：必须 `PYTHONUTF8=1`。
- **视觉复核**：2026-08-07 PM已逐张核对6张事件表；课程主要观察与画面一致。以后改时间码或参数时仍须重新逐张核对。

## 7. 已完成工作（v0.1.0）

- 技能骨架 + SKILL.md + agents/openai.yaml + references/lesson-template.md，`quick_validate` 通过
- 三个脚本全部实测：analyze_video 在合成测试视频与本样片跑通（manifest schema 1.0）；collect_tutorials 三主题实时检索跑通；validate_lesson 对样例与本课均 PASS
- 样例产出：`examples/sample-first-30s`（teacher）、`examples/verification-quick`（quick）
- 正式课程：`lessons/pS_L7x9PaY1vXXSh/`（6 节逐转场教学，校验 PASS，教程含YouTube/B站推荐；当前分支已移除第三方源视频，仅保留课程与证据包）

### 2026-08-07 PM审稿

- 视觉审查：逐张核对6张事件表，课程的对象、时序和能力边界与画面基本一致。
- 重要修正：252.1 BPM只保留为已知不可靠的算法候选；课程改为人工听拍、波形瞬态与帧数三重核对，不再据此自动铺标记。
- 教程审查：实时读回YouTube/B站标题、播放量和时长；移除偏题的超长合集与180播放候选，补入聚焦且高播放量的匹配剪辑、RGB Split和Speed Ramp教程。
- 交付安全：从当前分支移除第三方`source.mp4`并加入忽略规则；MIT只覆盖本仓库原创代码与文本，不覆盖第三方画面或证据帧。
- 验证状态：Python编译通过；课程严格校验与manifest一致性PASS；BPM守卫坏例/否定例回归通过；新增YouTube/B站候选已实时读回标题、播放量和时长。合并前仍须以最终提交重新验证。

## 8. GitHub 协作约定（用户规则，必须遵守）

- 每次推送一律走**分支**（默认 `codex/` 前缀），禁止直接推送/合并 `main`
- 推送前向用户确认；合入 `main` 需用户或 PM 明确指示
- 新建/更新仓库内容都走分支 + Pull Request
- 首版内容通过 `codex/initial-setup` 分支建立后由 GitHub 官方"分支重命名"接口转为 `main`（全新仓库无历史，重命名非推送/合并，符合上述约定）

## 9. 下一步建议（TODO）

- [x] 创建 GitHub 公开仓库并推送首版（分支 `codex/initial-setup` → 重命名为 `main`）
- [x] 完成本地 `codex/update-handoff` 分支的仓库状态更新与首课PM审稿；远端同步和合并状态以GitHub PR #1为准
- [ ] 用真实第二台电脑走一遍"克隆 → 装环境 → 跑拆解"验证交接文档完整性
- [ ] 扩充更多 Premiere 技法（速度重映射、时间 remap 参数课等）
- [ ] 改进 onset/节拍检测（降低对密集打击乐的误判）
- [ ] 为教程收集器接入网页搜索（B 站候选自动化），减少手工喂 JSON
- [ ] 公开仓库首个提交的Git历史中仍含第三方`source.mp4`对象；若要从历史彻底移除，需要用户另行授权历史重写或重建仓库
