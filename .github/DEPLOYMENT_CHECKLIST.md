# GitHub Actions 部署检查清单

## ✅ 本地验证

- [ ] Python 3.10+ 已安装
- [ ] 所有依赖已安装 (`pip install -r requirements.txt`)
- [ ] 页面可本地生成 (`python scripts/generate_news_page.py`)
- [ ] 生成的 `docs/index.html` 正确
- [ ] Git 仓库已初始化 (`git status` 正常)

## ✅ GitHub 仓库准备

- [ ] 代码已推送到 GitHub
- [ ] 仓库为 Public（GitHub Pages 支持）
- [ ] 主分支为 `main`（或已在 workflow 中配置）
- [ ] `.github/workflows/deploy.yml` 文件已提交
- [ ] `requirements.txt` 文件已提交

## ✅ GitHub 权限配置

### Pages 设置
- [ ] Settings → Pages 已访问
- [ ] Source 选择 "GitHub Actions"
- [ ] 如未显示，勾选 "Allow GitHub Actions to create and approve pull requests"

### Actions 权限
- [ ] Settings → Actions → General 已访问
- [ ] Workflow permissions: "Read and write permissions" ✓
- [ ] "Allow GitHub Actions to create and approve pull requests" ✓

## ✅ Workflow 验证

在 GitHub 仓库中：

1. **检查 workflow 文件**
   - [ ] 打开 Code 标签
   - [ ] 确认 `.github/workflows/deploy.yml` 存在
   - [ ] 文件内容正确

2. **运行 workflow**
   - [ ] 点击 "Actions" 标签
   - [ ] 选择 "Deploy to GitHub Pages"
   - [ ] 点击 "Run workflow" → "Run workflow"
   - [ ] 等待完成（通常 2-5 分钟）

3. **检查运行结果**
   - [ ] Workflow 状态：✅ Completed
   - [ ] Job 状态：✅ build-and-deploy
   - [ ] 查看日志确认所有步骤成功

## ✅ 部署验证

### GitHub Pages 地址
- [ ] 在 Settings → Pages 中查看部署 URL
- [ ] 格式：`https://username.github.io/daily_news`
- [ ] 访问并验证页面正确加载

### 页面内容验证
- [ ] 能看到新闻列表
- [ ] 文章数量 > 0
- [ ] 有来源徽章 (W 和 R)
- [ ] 能进行搜索
- [ ] 能切换主题
- [ ] 能筛选来源

## ✅ 定时任务验证

- [ ] Actions 页面显示定时任务已启用
- [ ] Cron 表达式正确：`0 8 * * *`（每天 UTC 8:00）
- [ ] 等待下次定时运行或手动触发查看效果

## 🔧 故障排查

### Workflow 运行失败

检查项：
- [ ] `requirements.txt` 是否完整
- [ ] Python 版本是否兼容
- [ ] 脚本是否有语法错误
- [ ] 网络连接是否正常

**查看日志：**
1. Actions 页面 → 选择失败的 run
2. 点击 "build-and-deploy" job
3. 展开具体的 step 查看详细错误

### 页面未部署

检查项：
- [ ] GitHub Pages 是否启用（Settings → Pages）
- [ ] Source 是否设置为 "GitHub Actions"
- [ ] Workflow 是否成功完成（✅ Completed）
- [ ] URL 是否正确

### 页面未更新

检查项：
- [ ] 是否已提交 `docs/index.html` 到仓库
- [ ] 浏览器缓存（尝试无痕模式或 Ctrl+Shift+R 硬刷新）
- [ ] GitHub Pages 缓存（等待 5-10 分钟）

## 📞 获取帮助

遇到问题？

1. 查看 [GitHub Actions 部署指南](.github/GITHUB_ACTIONS_GUIDE.md)
2. 检查 workflow 日志获取具体错误信息
3. 在 GitHub Issues 中报告问题

## ✨ 成功标志

完成以下所有项即表示部署成功：

- ✅ Workflow 在 Actions 页面显示为绿色（Completed）
- ✅ 网页可访问且内容正确
- ✅ 定时任务按预期运行
- ✅ 新闻每天自动更新

---

**检查完成时间：** _______________

**部署状态：** □ 成功  □ 进行中  □ 需要排查

**备注：**
```
_____________________________________________________

_____________________________________________________

_____________________________________________________
```
