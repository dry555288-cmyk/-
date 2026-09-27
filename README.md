# MineSim Git 整理版（2026-09-27）

这是把本轮提供的 MineSim 项目资料自动展开并整理后的 **Git / AI 友好版本**。你可以直接解压整个文件夹，然后在该目录执行 Git 初始化。

## 处理规则

- 所有顶层 ZIP 已展开为普通目录。
- 可正常读取的嵌套 ZIP 已继续展开；若与顶层包 SHA256 完全一致，则做精确去重并留下引用说明。
- 所有 `.docx` 均保留原文件，同时在同目录生成对应 `.md`，便于 ChatGPT / Codex / Claude Code / Cursor 等直接读取。
- Word 中的嵌入图片如能被 Pandoc 提取，会保存在文档同目录的 `.assets/<文档名>/` 下。
- `.json`、`.jsonl`、`.txt`、`.csv`、`.py`、`.geojson`、`.md` 等文本/代码文件保持原样。
- PDF、PNG、MP4 等二进制资料保持原样。
- `.7z` 文件未二次展开：当前运行环境没有可用的 7z 解包器，因此原样保留，避免破坏数据。
- 历史损坏大包 `.part001/.part002/.part003` 按证据文件原样保留，不自动重组或声称可解析。

## 推荐首先给 AI 阅读

1. `PROJECT_CONTEXT.md`
2. `00_最新交接与研究流程/MineSim_G1_交接文档_20260926.md`
3. `00_最新交接与研究流程/MineSim_神经网络辅助MCTS_严谨研究流程_V1.md`
4. `DOCX_CONVERSION_REPORT.csv`
5. `ARCHIVE_EXPANSION_REPORT.csv`

## 目录说明

- `00_最新交接与研究流程`：本轮单独上传的最新交接、G1 冻结报告和研究流程。
- `01_当前接手核心与最新证据`：当前接手核心与证据包。
- `02_地图与原项目复现`：地图、GeoJSON、原项目论文/复现资料。
- `03_历史交接文档`：历史阶段交接 Word；已批量生成 Markdown。
- `04_参考论文`：参考论文归档；其中 `.7z` 原样保留。
- `05_接下来方向与效果对比`：后续方向与效果对比归档；其中 `.7z` 原样保留。
- `06_专项证据与论文资料`：专项证据、代码、记录和文档。
- `07_历史损坏大包分片A` / `08_历史损坏大包分片B`：历史损坏大包的原始分片证据。
- `09_AI接手文档集合`：AI 接手资料集合；其中可读 ZIP 已递归展开并转换 Word。

## Git 初始化

在解压后的根目录打开 PowerShell / Git Bash：

```bash
git init
git add .
git commit -m "Initial MineSim project archive"
git branch -M main
```

随后创建 GitHub 仓库，再添加远程地址并 push。

> 注意：这是本地资料快照，不等同于 `/root/MineSim-Dynamic` 云端仓库的实时状态。继续科研执行前仍应先核对 live Git HEAD、git status 与冻结 SHA。
