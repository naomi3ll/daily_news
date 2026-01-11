# GitHub Actions 部署指南

本项目使用 GitHub Actions 自动化生成和部署新闻页面。

## 工作流说明

### 触发条件

Workflow 在以下情况下自动运行：

1. **推送到 main 分支**
   - 当代码推送到 main 分支时自动触发
   - 会生成最新的新闻页面并部署到 GitHub Pages

2. **定时运行**
   - 每天 UTC 8:00 运行（北京时间 16:00）
   - 自动抓取最新新闻并更新页面
   - 生成的页面自动提交回仓库

3. **手动触发**
   - 可在 GitHub Actions 标签页手动运行 workflow
   - 按 "Run workflow" 按钮即可

## 工作流步骤

```
1. 检出代码
   ↓
2. 配置 Python 环境 (3.11)
   ↓
3. 安装依赖 (requirements.txt)
   ↓
4. 执行生成脚本 (scripts/generate_news_page.py)
   ↓
5. 提交更新 (仅限定时和手动触发)
   ↓
6. 上传构建产物到 GitHub Pages
   ↓
7. 部署到 GitHub Pages
```

## 配置要求

### 1. 启用 GitHub Pages

在仓库设置中启用 GitHub Pages：

```
Settings → Pages → Source → Deploy from a branch
Build and deployment → Branch: gh-pages (自动创建) → / (root)
```

或者使用 GitHub Actions 自动部署（推荐）：

```
Settings → Pages → Source → GitHub Actions
```

### 2. 权限配置

确保 GitHub Actions 有正确的权限：

```
Settings → Actions → General → Workflow permissions
→ Read and write permissions
→ Allow GitHub Actions to create and approve pull requests
```

### 3. 依赖文件

确保项目包含以下文件：

```
requirements.txt      # Python 依赖
scripts/              # 生成脚本目录
  └─ generate_news_page.py
docs/                 # 输出目录
  └─ index.html       # 生成的网页
```

## 使用方法

### 自动部署

1. 将代码推送到 GitHub 主分支
2. GitHub Actions 自动运行 workflow
3. 生成的页面自动部署到 GitHub Pages
4. 访问 `https://<username>.github.io/daily_news` 查看

### 手动触发更新

1. 打开 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择 "Deploy to GitHub Pages" workflow
4. 点击 "Run workflow" → "Run workflow"
5. 等待完成后查看结果

### 查看部署状态

1. 点击 "Actions" 标签
2. 查看最近的 workflow 运行记录
3. 点击具体的 run 查看详细日志

## 工作流配置详解

### 触发条件

```yaml
on:
  push:
    branches:
      - main              # 推送到 main 分支时触发
  schedule:
    - cron: '0 8 * * *'  # 每天 UTC 8:00 运行
  workflow_dispatch:      # 支持手动触发
```

### Python 环境

```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.11'  # Python 版本
    cache: 'pip'            # 缓存 pip 包
```

### 依赖安装

```yaml
- run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

### 生成新闻页面

```yaml
- run: python scripts/generate_news_page.py
```

自动爬取新闻源并生成 `docs/index.html`

### 提交更新（可选）

```yaml
- run: |
    git add docs/index.html
    git commit -m "docs: update news page [skip ci]"
    git push
```

- 仅在定时和手动触发时执行
- 自动提交生成的文件到仓库
- `[skip ci]` 标记防止再次触发 workflow

### 部署到 GitHub Pages

```yaml
- uses: actions/upload-pages-artifact@v2
  with:
    path: 'docs'              # 上传 docs 目录

- uses: actions/deploy-pages@v2
```

## 环境变量（可选）

如果需要在 workflow 中使用环境变量，可以在 secrets 中配置：

```
Settings → Secrets and variables → Actions → New repository secret
```

例如：

```
PYTHON_VERSION=3.11
SCHEDULE_TIME=0 8 * * *
```

在 workflow 中使用：

```yaml
python-version: ${{ secrets.PYTHON_VERSION }}
```

## 常见问题

### 1. Workflow 运行失败

**原因：** 依赖缺失或 Python 版本不兼容

**解决：**
- 检查 `requirements.txt` 是否完整
- 确认 Python 版本支持（推荐 3.10+）
- 查看 workflow 日志获取详细错误信息

### 2. 页面未更新

**原因：** GitHub Pages 未启用或缓存问题

**解决：**
- 确认 GitHub Pages 已启用
- 清除浏览器缓存或使用无痕模式
- 检查 workflow 是否成功完成

### 3. 提交失败

**原因：** Git 权限问题

**解决：**
- 确认仓库权限设置正确
- 检查 `GITHUB_TOKEN` 是否有效
- 确认分支保护规则不冲突

### 4. 定时任务未运行

**原因：** 仓库未启用 Actions 或分支条件不符

**解决：**
- 确认 Actions 已启用
- 确认 workflow 文件在 main 分支
- 等待 GitHub Actions runner 可用

## 监控和日志

### 查看构建日志

1. 点击 Actions → 具体的 run
2. 点击 "build-and-deploy" job
3. 展开各个步骤查看详细日志

### 常见日志关键词

```
✓ Checkout code         # 代码检出成功
✓ Set up Python        # Python 环境就绪
✓ Install dependencies # 依赖安装完成
✓ Generate news page   # 页面生成成功
✓ Deploy to GitHub Pages # 部署成功
```

## 成本说明

GitHub Actions 提供免费额度：
- **Public 仓库**：无限制
- **Private 仓库**：每月 2000 分钟（足够每天一次的定时任务）

本项目每天一次的定时任务消耗约 30-60 秒，成本很低。

## 高级配置

### 自定义 Cron 表达式

修改 `cron` 值来改变执行时间：

```yaml
schedule:
  - cron: '30 * * * *'    # 每小时 30 分运行
  - cron: '0 0 * * 0'     # 每周日 UTC 0:00 运行
  - cron: '0 8 * * 1-5'   # 工作日 UTC 8:00 运行
```

### 条件执行

根据文件变更触发 workflow：

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'scripts/**'      # 仅当脚本改变时
      - 'requirements.txt'
```

### 并发控制

防止多个 workflow 同时运行：

```yaml
concurrency:
  group: "pages"
  cancel-in-progress: true  # 取消进行中的 workflow
```

## 调试技巧

### 启用调试日志

在 workflow 中添加 debug 模式：

```yaml
env:
  RUNNER_DEBUG: 1
```

### 查看环境信息

```yaml
- name: Debug Info
  run: |
    python --version
    pip list
    ls -la docs/
```

## 支持和反馈

如遇到问题，请：

1. 查看 workflow 日志获取错误信息
2. 检查此指南的"常见问题"部分
3. 在 GitHub Issues 提交问题报告

---

**最后更新：2026-01-11**
