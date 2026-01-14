# 路透社新闻获取问题 - 快速参考

## 📌 问题现象
GitHub Actions 运行后，路透社新闻为空（显示 0 条）

## ✅ 已完成的修复

### 代码改进
- ✅ 升级 User-Agent（包括 Chrome 120, Firefox 121, Safari 等）
- ✅ 增加超时时间（10秒 → 15秒）
- ✅ 增加退避时间（0.5秒 → 1.0秒）
- ✅ 添加详细日志输出（stderr 标准错误流）
- ✅ 改进错误处理和异常捕获
- ✅ 添加容错机制（失败时返回过期缓存）

### 文件修改
```
✏️  get_reuters_news.py          (改进连接和日志)
✏️  news_aggregator.py           (改进聚合日志)
✏️  scripts/generate_news_page.py (改进输出日志)
✏️  .github/workflows/deploy.yml  (增加调试输出)
➕ .github/workflows/diagnose-reuters.yml (新增诊断工作流)
➕ .github/REUTERS_DEBUG.md       (调试指南)
➕ .github/REUTERS_SOLUTION.md    (完整解决方案)
```

## 🔍 如何诊断

### 方式 1：查看部署日志（简单）
1. GitHub → Actions → Deploy to GitHub Pages
2. 找最新运行 → "Generate news page (with debug output)" 步骤
3. 查看输出中的：
   - `[Reuters] 获取完成: 成功 3/3, 共 XX 条新闻` ✅ 正常
   - `[Reuters] 获取完成: 成功 3/3, 共 0 条新闻` ❌ 解析问题

### 方式 2：运行诊断工作流（推荐）
1. GitHub → Actions → **Diagnose Reuters News Issue**
2. 点击 **Run workflow**
3. 等待完成，查看详细诊断结果

## 🎯 下一步行动

### 立即做
```bash
# 1. 提交改动
git add -A
git commit -m "fix: improve Reuters news fetching with debug logs"
git push origin main

# 2. 运行 GitHub Actions 诊断工作流
# 在 GitHub Actions 页面手动运行 "Diagnose Reuters News Issue"

# 3. 查看诊断结果
# 检查日志中的错误信息
```

### 根据诊断结果

**如果日志显示连接成功但获取 0 条：**
- 问题：网站 HTML 结构可能改变
- 解决：需要更新选择器或考虑使用 Selenium

**如果日志显示连接失败：**
- 问题：IP 被限制或网络问题
- 解决：
  - 方案 A：添加随机延迟和 User-Agent 轮询
  - 方案 B：使用代理服务
  - 方案 C：使用 Selenium 进行 JavaScript 渲染
  - 方案 D：使用新闻 API 服务

## 📊 日志输出示例

### ✅ 正常输出
```
[聚合] 正在从 reuters 获取新闻...
[Reuters] 获取 https://www.reuters.com/world
[Reuters] 状态码: 200, 内容长度: 504737
[Reuters] 获取 https://www.reuters.com/business
[Reuters] 状态码: 200, 内容长度: 391168
[Reuters] 获取 https://www.reuters.com/markets
[Reuters] 状态码: 200, 内容长度: 642119
[Reuters] 获取完成: 成功 3/3, 共 63 条新闻
[聚合] reuters: 成功获取 63 条新闻
```

### ❌ 异常输出
```
[Reuters] 获取 https://www.reuters.com/world 时出错: 
ConnectionError: Connection refused
[Reuters] 获取完成: 成功 0/3, 共 0 条新闻
```

## 🛠️ 进阶解决方案

### 如果上述改进仍不奏效

**选项 1：使用 Selenium（渲染 JavaScript）**
```bash
# 编辑 requirements.txt，添加：
selenium
webdriver-manager
```

**选项 2：使用随机延迟**
```python
import random, time
time.sleep(random.uniform(0.5, 2.0))
```

**选项 3：使用代理**
```python
proxies = {'http': 'http://proxy:port', 'https': 'http://proxy:port'}
response = session.get(url, proxies=proxies)
```

**选项 4：使用新闻 API**
- NewsAPI.org
- MediaStack
- 或联系路透社获取 API 访问

## 💬 相关文档

- 📖 详细指南：`.github/REUTERS_SOLUTION.md`
- 🔍 调试说明：`.github/REUTERS_DEBUG.md`
- 🚀 部署指南：`.github/GITHUB_ACTIONS_GUIDE.md`

## 📞 常见问题

**Q: 本地正常但 GitHub Actions 为空？**
A: 可能是 IP 被限制。查看诊断工作流日志，看状态码是否为 200。

**Q: 如何快速测试修复？**
A: 运行诊断工作流："Diagnose Reuters News Issue"

**Q: 需要多长时间才能看到效果？**
A: 推送代码后，下一次 Actions 运行（push/定时/手动）会应用修改。

**Q: 可以禁用路透社数据吗？**
A: 可以，编辑 `news_aggregator.py` 注释掉 `ReutersSource` 的引入。

---

**最后更新：2026-01-14**
