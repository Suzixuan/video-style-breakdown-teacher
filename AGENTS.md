# Video Style Breakdown Teacher 项目约定

## 当前范围

- 当前版本为 v0.2.0 Interactive Curriculum。
- 保留 v0.1 的 `lesson.md`、证据生成、教程收集与 `validate_lesson.py` 工作流。
- v0.2 只负责课程编排和校验，不连接 Premiere MCP，不读取或修改用户工程，也不声称已检查 PR 时间线。
- Premiere MCP、Progress、Demo/Rescue 和视觉验收属于后续阶段；未经明确任务不要提前实现。

## 教学与数据边界

- 证据、推断和 PR 复刻起点必须分开；不得把猜测写成原作者精确插件、预设或参数。
- 必须标明 `PR-native`、`PR-approximation`、`AE-preferred` 或 `3D-source-required`。
- Curriculum 的 skill ID 和依赖以 `references/skill-taxonomy.md` 为权威来源。
- 普通 Unit 只设一个主要目标、最多三个新 skill，并包含实际作品、结构/参数/视觉三类 PASS checkpoint 和 tutorial topic。
- 不得把未核实 BPM 转成自动标记命令；教程片段时间未人工核实时不得编造 timestamp。

## 素材与安全

- 不提交第三方源视频、凭证、Token、`.env` 或本地配置。
- 第三方证据帧只用于评论、教学与复核；仓库 MIT License 只覆盖原创代码和文本。
- `.coach/`、本地练习工程和生成缓存保持未跟踪。

## 修改后验收

在仓库根目录运行：

```powershell
$env:PYTHONUTF8='1'
python -m unittest scripts.test_validate_lesson scripts.test_validate_curriculum
python scripts/validate_curriculum.py lessons/pS_L7x9PaY1vXXSh/curriculum.yaml --strict
python scripts/validate_lesson.py lessons/pS_L7x9PaY1vXXSh/lesson.md --manifest lessons/pS_L7x9PaY1vXXSh/evidence/analysis_manifest.json --strict
python "C:\Users\suzix\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
git diff --check
```

## GitHub 协作

- 所有更新使用 `codex/` 分支和 Pull Request；不直接推送或合并 `main`。
- 未经明确授权不 force-push、改仓库可见性、tag、release 或 deploy。
- 合并前复核真实 diff、测试结果、远端分支 SHA 和 PR 状态。
