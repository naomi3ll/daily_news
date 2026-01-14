# GitHub Actions 路透社新闻获取问题 - 调试指南

## 🔍 快速诊断

### 问题症状
- GitHub Actions 运行后，路透社新闻为空
- 本地开发环境可以正常获取路透社新闻

### 可能的原因排序（按概率）

1. **IP 地址被限制** (50%) 
   - GitHub Actions 使用的 IP 被路透社服务器检测为爬虫
   - 可能被防火墙或 WAF 拦截

2. **JavaScript 动态渲染问题** (30%)
   - 路透社网站可能依赖 JavaScript 加载新闻
   - BeautifulSoup 只能解析静态 HTML

3. **User-Agent 检测** (15%)
   - 旧的 User-Agent 被检测
   - （已通过更新 User-Agent 解决）

4. **网站结构改变** (5%)
   - 路透社网站 HTML 结构可能已更改
   - 选择器可能失效

## 🛠️ 已实施的改进

### ✅ 已完成的修改

1. **改进 User-Agent 轮询**
   ```python
   # 添加了多个现代 User-Agent 字符串
   # 包括 Chrome 120, Firefox 121, Safari 等
   ```

2. **增加诊断日志**
   ```
   [Reuters] 获取 https://www.reuters.com/world
   [Reuters] 状态码: 200, 内容长度: 504737
   [Reuters] 获取完成: 成功 3/3, 共 63 条新闻
   ```

3. **改进错误处理**
   - 增加了详细的异常捕获
   - 失败时返回过期缓存数据作为容错

4. **增加超时时间**
   - 从 10 秒增加到 15 秒
   - 增加退避时间从 0.5 秒到 1.0 秒

5. **增强的 GitHub Actions 工作流**
   - 详细的调试输出
   - 文件内容检查

## 🚀 如何诊断问题

### 方法 1：查看部署工作流日志（简单）

1. 登录 GitHub
2. 打开你的仓库 → **Actions** 标签
3. 点击最新的 "Deploy to GitHub Pages" 工作流
4. 展开 "Generate news page (with debug output)" 步骤
5. 查看输出，找到以下信息：

```
========================================
开始生成新闻页面
==========================================
[聚合] 正在从 reuters 获取新闻...
[Reuters] 获取 https://www.reuters.com/world
[Reuters] 状态码: 200
[Reuters] 获取完成: 成功 3/3, 共 63 条新闻
[聚合] reuters: 成功获取 63 条新闻
```

**解读结果：**
- ✅ 如果显示 "成功获取 XX 条新闻" → 路透社获取正常
- ❌ 如果显示 "成功获取 0 条新闻" → 可能是解析问题
- ❌ 如果显示连接错误 → 是网络问题

### 方法 2：运行诊断工作流（推荐）

1. 打开你的仓库
2. 点击 **Actions** → **Diagnose Reuters News Issue**
3. 点击 **Run workflow** 按钮
4. 等待完成
5. 查看详细的诊断输出：
   - 网络连接测试
   - DNS 解析测试
   - 单独的路透社获取测试
   - 新闻聚合测试
   - 最终生成的页面检查

## 📊 诊断输出解读

### 场景 1：本地正常，GitHub Actions 为空

**原因：IP 被限制**

```
症状：
- 本地: 获取了 63 条路透社新闻 ✓
- GitHub Actions: 获取了 0 条路透社新闻 ✗
```

**解决方案：**
```python
# 方案 A：添加随机延迟避免触发 WAF
import random, time
time.sleep(random.uniform(1, 3))

# 方案 B：使用不同的 User-Agent
user_agents = [...]  # 多个 User-Agent
headers['User-Agent'] = random.choice(user_agents)

# 方案 C：使用代理（需要自行配置）
# 方案 D：使用 Selenium 渲染（见下文）
```

### 场景 2：本地和 GitHub Actions 都为空

**原因：可能是网站结构改变或 JavaScript 渲染问题**

```
症状：
- 本地: 获取了 0 条新闻 ✗
- GitHub Actions: 获取了 0 条新闻 ✗
```

**解决方案：**
```bash
# 1. 手动检查网站
curl -s https://www.reuters.com/world | grep -i "article\|title" | head

# 2. 检查 HTML 结构是否改变
# 更新 get_reuters_news.py 中的选择器

# 3. 考虑使用 JavaScript 渲染
```

### 场景 3：显示连接错误

**原因：网络问题**

```
症状：
[Reuters] 获取 https://www.reuters.com/world 时出错: 
ConnectionError: Connection refused
```

**解决方案：**
- 检查网络连接
- 增加超时时间
- 使用代理

## 💡 进阶解决方案

### 方案 A：添加随机延迟

```python
import random
import time

# 在请求前添加随机延迟
time.sleep(random.uniform(0.5, 2.0))

response = session.get(url, headers=headers, timeout=15)
```

### 方案 B：使用 Selenium 渲染 JavaScript

```python
# 1. 在 requirements.txt 中添加
selenium
webdriver-manager

# 2. 修改 get_reuters_news.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)
driver.get(url)

# 等待元素加载
wait = WebDriverWait(driver, 10)
elements = wait.until(
    lambda d: d.find_elements(By.TAG_NAME, 'article')
)
```

### 方案 C：使用新闻 API

```python
# 方案 1：使用 NewsAPI.org（免费额度有限）
import requests

API_KEY = "your_api_key"
url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"
response = requests.get(url)
data = response.json()

# 方案 2：使用 MediaStack API
# 方案 3：自行联系路透社获取 API 访问
```

### 方案 D：增加重试和备份策略

```python
# 增加重试次数和退避时间
retry_strategy = Retry(
    total=5,  # 增加到 5 次
    backoff_factor=2.0,  # 指数退避：1s, 2s, 4s, 8s, 16s
    status_forcelist=[429, 500, 502, 503, 504],
)

# 或使用 tenacity 库
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def fetch_with_retry(url):
    return requests.get(url, timeout=15)
```

## 📝 修改检查清单

- [x] 更新 User-Agent 到最新版本
- [x] 增加详细的调试日志
- [x] 改进错误处理和异常捕获
- [x] 增加超时时间
- [x] 创建诊断工作流
- [ ] （可选）添加随机延迟
- [ ] （可选）使用 Selenium 渲染
- [ ] （可选）集成新闻 API

## 🔗 相关资源

- GitHub Actions 文档：https://docs.github.com/en/actions
- BeautifulSoup 文档：https://www.crummy.com/software/BeautifulSoup/
- Selenium 文档：https://selenium.dev/documentation/
- 路透社网站：https://www.reuters.com/

## 📞 需要帮助？

### 快速问题排查

| 问题 | 检查项 | 解决方案 |
|------|--------|---------|
| GitHub Actions 中路透社为空 | 1. 查看日志中的状态码<br>2. 检查网络诊断结果 | 如果状态码 200 但解析为 0：网站结构改变<br>如果连接失败：IP 被限制 |
| 本地和 GitHub Actions 都为空 | 1. 手动访问 reuters.com<br>2. 查看 HTML 源码 | 网站 HTML 结构可能已改变，需要更新选择器 |
| 其他问题 | 1. 检查 Python 版本<br>2. 检查依赖版本 | 升级 requirements.txt 中的包 |

## 更新日志

- **2026-01-14**: 
  - ✨ 新增诊断工作流 `diagnose-reuters.yml`
  - 🔧 改进 User-Agent 和超时设置
  - 📝 添加详细的调试日志
  - 📖 创建完整的调试指南

