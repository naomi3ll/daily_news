# 路透社新闻获取问题诊断

## 问题描述
在 GitHub Actions 运行时，路透社新闻为空，但本地开发环境正常。

## 可能的原因

### 1. **IP 地址被限制**
- GitHub Actions 使用的 IP 地址可能被路透社服务器限制或检测为爬虫
- 路透社可能有防爬虫机制

### 2. **User-Agent 检测**
- 旧的 User-Agent 字符串可能被检测
- 需要使用最新的浏览器 User-Agent

### 3. **JavaScript 动态渲染**
- 路透社网站可能依赖 JavaScript 动态加载内容
- BeautifulSoup 只能解析静态 HTML，无法执行 JavaScript

### 4. **网络限制**
- GitHub Actions 的网络环境可能有特殊限制
- 可能无法访问某些外部资源

### 5. **网站结构改变**
- 路透社网站 HTML 结构可能已经改变
- 选择器可能不再有效

## 解决方案

### 已实施的改进
✅ 升级 User-Agent 到最新版本（Chrome 120）
✅ 增加多个备用 User-Agent（轮询使用）
✅ 增加超时时间从 10 秒到 15 秒
✅ 增加详细的调试日志输出
✅ 添加容错机制：失败时返回过期缓存数据
✅ 改进错误处理和异常捕获

### 进一步的改进方向

#### 选项 A：使用代理池
```python
# 使用免费代理服务
proxies = {
    'http': 'http://proxy.ip:port',
    'https': 'http://proxy.ip:port',
}
response = session.get(url, proxies=proxies, timeout=15)
```

#### 选项 B：使用 Selenium 或 Playwright（JavaScript 渲染）
```python
# 需要在 requirements.txt 中添加
selenium
playwright
```

#### 选项 C：使用新闻 API
```python
# 使用专门的新闻 API 服务
# NewsAPI, MediaStack 等
```

#### 选项 D：重试机制优化
```python
# 增加重试次数和退避时间
retry_strategy = Retry(
    total=5,  # 增加重试次数
    backoff_factor=2.0,  # 指数退避
    status_forcelist=[429, 500, 502, 503, 504],
)
```

## 诊断步骤

### 1. 查看 GitHub Actions 日志
登录 GitHub → 打开你的仓库 → Actions 页面 → 查看最新的 Workflow 运行 → 展开"Generate news page"步骤

查看输出中的以下信息：
- `[Reuters] 获取 https://www.reuters.com/...` - 显示正在尝试的 URL
- `[Reuters] 状态码: XXX` - HTTP 响应状态码
- `[Reuters] 获取了 X 条路透社新闻` - 最终成功获取的新闻数

### 2. 本地测试
```bash
# 清除缓存，强制重新获取
python3 -c "
from get_reuters_news import get_reuters_news
items = get_reuters_news(use_cache=False)
print(f'获取了 {len(items)} 条新闻')
"
```

### 3. 测试连接
```bash
# 测试网络连接
curl -I -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  https://www.reuters.com/world

# 查看响应头
curl -v -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  https://www.reuters.com/world 2>&1 | head -30
```

## 推荐的后续步骤

### 立即尝试的
1. ✅ 已完成：改进 User-Agent 和超时时间
2. ✅ 已完成：添加详细日志
3. 🔄 下一步：运行 GitHub Actions，查看详细日志
4. 🔄 分析日志中的错误信息

### 如果上述方案仍不奏效
1. 考虑使用代理服务或 VPN
2. 考虑使用 Selenium/Playwright 进行 JavaScript 渲染
3. 考虑使用专门的新闻 API 服务
4. 考虑联系路透社获取 API 访问权限

## 常见状态码说明

| 状态码 | 含义 | 解决方案 |
|--------|------|---------|
| 200 | 请求成功 | ✅ 正常 |
| 403 | 禁止访问 | 可能 IP 被限制或需要登录 |
| 429 | 请求过于频繁 | 添加延迟，使用代理 |
| 500, 502, 503 | 服务器错误 | 稍后重试 |
| 超时 | 连接超时 | 检查网络，增加超时时间 |

## 更新日志

- **2026-01-14**: 添加详细的日志输出和错误处理机制
- 待更新...
