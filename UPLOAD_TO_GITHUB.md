# 上传 GitHub：最短流程

## 1. 解压本整理包

不要在原始资料目录上操作，直接对本整理版文件夹初始化 Git。

## 2. 初始化

```bash
git init
git add .
git commit -m "Initial MineSim project archive"
git branch -M main
```

## 3. 在 GitHub 新建一个空仓库

建议先设为 **Private**，确认没有账号、密钥、token、隐私数据或不应公开的论文/版权资料后再决定是否公开。

## 4. 关联并上传

```bash
git remote add origin <你的GitHub仓库地址>
git push -u origin main
```

## 5. AI 使用建议

让 AI 首先读取 `PROJECT_CONTEXT.md` 与最新交接文档，再按需读取历史资料；不要一开始全仓库无差别扫描。
