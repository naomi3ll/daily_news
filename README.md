# daily_news — 财经新闻聚合平台

这个项目自动抓取多个财经新闻源，生成一个美观的网页展示每日最新新闻。

## 功能特性

- **多源聚合**：支持从多个新闻源（华尔街见闻、路透社等）抓取新闻
- **统一格式**：所有新闻统一为标准数据格式 `{'title', 'datetime', 'link', 'source', 'type'}`
- **实时搜索**：前端支持实时搜索和按来源筛选
- **深色主题**：支持浅色/深色主题切换，自动保存用户偏好
- **响应式设计**：完全适配移动设备
- **自动更新**：GitHub Actions 定时更新新闻

## 工作原理

```
1. get_wallstreat_news.py     -- 华尔街见闻爬虫
   get_reuters_news.py         -- 路透社爬虫
   
2. news_aggregator.py          -- 聚合多个来源的新闻
   
3. scripts/generate_news_page.py -- 生成 HTML 页面
   
4. docs/index.html             -- 发布到 GitHub Pages
```

### 核心模块

- **`get_wallstreat_news.py`**: 从华尔街见闻 API 获取新闻
- **`get_reuters_news.py`**: 从路透社网站爬取新闻
- **`news_aggregator.py`**: 
  - `NewsSource` 基类 - 定义爬虫接口
  - `WallStreetCNSource` - 华尔街见闻实现
  - `ReutersSource` - 路透社实现
  - `NewsAggregator` - 聚合多个来源
  - `fetch_all_news()` - 获取所有新闻的便利函数
  - `fetch_news_by_source()` - 按来源获取新闻

### 数据格式

所有新闻统一为以下格式：

```python
{
    'title': str,      # 新闻标题
    'datetime': str,   # 发布时间，格式：'YYYY-MM-DD HH:MM:SS' (北京时间)
    'link': str,       # 新闻链接（绝对URL）
    'source': str,     # 来源，如 'wallstreetcn'、'reuters'
    'type': str        # 类型，如 'article'、'live'、'theme'
}
```

## 使用方法

### 安装依赖

```bash
pip install -r requirements.txt
```

### 本地测试

```bash
# 测试聚合器
python news_aggregator.py

# 测试生成页面
python scripts/generate_news_page.py

# 运行完整测试
python test_news_aggregator.py
```

### 扩展 - 添加新的新闻源

1. 创建一个新的爬虫脚本，比如 `get_xxx_news.py`：

```python
def get_xxx_news(use_cache=True, cache_ttl=60):
    """获取 XXX 新闻"""
    return [
        {
            'title': '标题',
            'datetime': '2026-01-11 20:00:00',
            'link': 'https://xxx.com/article/123',
            'source': 'xxx',
            'type': 'article'
        },
        # ... 更多新闻
    ]
```

2. 在 `news_aggregator.py` 中添加新的 Source 类：

```python
from get_xxx_news import get_xxx_news

class XxxSource(NewsSource):
    @staticmethod
    def fetch(use_cache=True, cache_ttl=60):
        return get_xxx_news(use_cache=use_cache, cache_ttl=cache_ttl)
```

3. 在 `NewsAggregator.__init__` 中注册新来源：

```python
self.sources = {
    'wallstreetcn': WallStreetCNSource(),
    'reuters': ReutersSource(),
    'xxx': XxxSource(),  # 添加新来源
}
```

## 前端功能

### 搜索与筛选

- **搜索框**：实时搜索新闻标题
- **来源筛选**：可按华尔街见闻、路透社等筛选
- **统计信息**：显示总新闻数量

### 主题切换

- 浅色/深色主题自动切换
- 用户偏好自动保存到 LocalStorage

### 响应式设计

- 桌面版：3列网格布局
- 移动版：1列布局

## GitHub Actions 自动化部署

项目完全支持 GitHub Actions 自动化工作流。

### 快速开始

#### 方式 1：自动部署（推荐）

1. **推送代码到 GitHub**
   ```bash
   git push origin main
   ```

2. **启用 GitHub Actions**
   - 打开仓库 → Settings → Pages
   - Source 选择 "GitHub Actions"

3. **工作流会自动**
   - 定时更新新闻（每天 UTC 8:00）
   - 自动生成和部署页面
   - 更新的文件自动提交回仓库

4. **查看结果**
   - 访问 `https://username.github.io/daily_news`
   - 或在 Actions 标签页查看运行日志

#### 方式 2：本地测试

```bash
# 运行配置脚本（会创建虚拟环境并测试生成）
bash .github/setup-deploy.sh

# 或手动执行
python scripts/generate_news_page.py
open docs/index.html
```

### Workflow 配置

工作流配置文件：`.github/workflows/deploy.yml`

**运行条件：**
- ✅ 推送到 main 分支时
- ✅ 每天 UTC 8:00 自动运行（可自定义）
- ✅ 在 Actions 页面手动触发

**执行步骤：**
1. 检出代码
2. 配置 Python 3.11 环境
3. 安装 requirements.txt 依赖
4. 执行 `scripts/generate_news_page.py` 生成页面
5. 提交更新回仓库（可选）
6. 上传到 GitHub Pages

### 常见配置

**修改执行频率：**

编辑 `.github/workflows/deploy.yml`：
```yaml
schedule:
  - cron: '0 8 * * *'    # 默认：每天 UTC 8:00
  - cron: '0 */6 * * *'  # 修改为：每 6 小时运行一次
```

**跳过 CI 运行：**

在提交信息中添加 `[skip ci]`：
```bash
git commit -m "docs: update news [skip ci]"
```

### 详细文档

更多配置和问题排查，请查看 [GitHub Actions 部署指南](.github/GITHUB_ACTIONS_GUIDE.md)

涵盖内容：
- 权限配置
- 环境变量
- 常见问题及解决方案
- 高级配置
- 调试技巧

## GitHub Pages 部署

项目使用 GitHub Actions 自动部署到 GitHub Pages。

**前提要求：**
- 仓库已启用 GitHub Pages（Settings → Pages → Source: GitHub Actions）
- 正确的读写权限（Settings → Actions → General）

**部署流程：**
1. 推送代码到 main 分支
2. GitHub Actions 自动运行
3. 生成 HTML 页面到 docs 目录
4. 自动部署到 GitHub Pages
5. 访问 `https://username.github.io/daily_news` 即可查看

## 本地化

- 所有 UI 文本已本地化为中文
- 时间统一转换为北京时间 (Asia/Shanghai)

## 文件结构

```
.
├── README.md                       # 项目说明文档
├── requirements.txt                # Python 依赖
├── get_wallstreat_news.py         # 华尔街见闻爬虫
├── get_reuters_news.py            # 路透社爬虫
├── news_aggregator.py             # 新闻聚合器
├── test_news_aggregator.py        # 测试脚本
├── scripts/
│   └── generate_news_page.py      # 生成 HTML 页面脚本
└── docs/
    └── index.html                 # 生成的网页（由脚本生成）
```

## 自定义

### 修改样式

编辑 `scripts/generate_news_page.py` 中的 CSS，修改：
- 颜色主题（--accent, --bg 等）
- 布局和间距
- 字体和大小

### 修改更新频率

编辑 `.github/workflows/fetch_news.yml` 中的 cron 表达式。

例如，每小时执行一次：
```yaml
schedule:
  - cron: '0 * * * *'
```

## 故障排除

### 爬虫不工作

- 检查网络连接
- 验证网站是否更改了结构
- 查看爬虫输出的错误信息
- 尝试更新 User-Agent

### 页面未更新

- 检查 GitHub Actions 日志
- 验证 GitHub Pages 是否启用
- 刷新浏览器缓存（Ctrl+Shift+R）

## 技术栈

- **爬虫**：Python, requests, BeautifulSoup
- **聚合器**：Python, 内存缓存
- **前端**：HTML5, CSS3, JavaScript (原生)
- **部署**：GitHub Pages, GitHub Actions

## 许可证

MIT

## 更新日志

### v2.0 (2026-01-11)

- ✅ 支持多源新闻聚合（华尔街见闻 + 路透社）
- ✅ 统一数据格式和接口
- ✅ 改进的前端设计和交互
- ✅ 添加搜索和筛选功能
- ✅ 支持深色主题
- ✅ 完整的测试覆盖
- ✅ 扩展指南文档

### v1.0 (之前版本)

- 单源新闻抓取（仅华尔街见闻）
