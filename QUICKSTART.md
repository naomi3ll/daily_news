# 快速入门指南

## 项目概述

这是一个**多源财经新闻聚合平台**，自动从华尔街见闻和路透社获取每日新闻，生成美观的网页展示。

## 5分钟快速开始

### 1. 安装

```bash
cd /Users/naomi/Projects/daily_news

# 使用虚拟环境（推荐）
python3.11 -m venv venv
source venv/bin/activate

# 或直接使用 pyenv 环境
source ~/.pyenv/versions/3.11.12/envs/daily_news/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 测试爬虫

```bash
# 测试华尔街见闻爬虫
python get_wallstreat_news.py

# 测试路透社爬虫
python get_reuters_news.py

# 测试聚合器
python news_aggregator.py
```

### 3. 生成页面

```bash
# 生成 HTML 页面
python scripts/generate_news_page.py

# 输出：Wrote docs/index.html
```

### 4. 查看结果

```bash
# 本地查看
open docs/index.html

# 或用浏览器打开
# 文件位置: /Users/naomi/Projects/daily_news/docs/index.html
```

## 主要文件说明

| 文件 | 说明 |
|------|------|
| `get_wallstreat_news.py` | 华尔街见闻爬虫 |
| `get_reuters_news.py` | 路透社爬虫（新增） |
| `news_aggregator.py` | 新闻聚合器（新增） |
| `scripts/generate_news_page.py` | HTML 生成脚本 |
| `test_news_aggregator.py` | 单元测试（新增） |
| `test_integration.py` | 集成测试（新增） |
| `docs/index.html` | 生成的网页 |
| `README.md` | 详细文档 |
| `IMPLEMENTATION_SUMMARY.md` | 实现总结（新增） |

## 常见命令

```bash
# 从头获取新闻（不使用缓存）
python -c "from news_aggregator import fetch_all_news; print(f'Found {len(fetch_all_news(use_cache=False))} articles')"

# 按来源获取
python -c "from news_aggregator import fetch_news_by_source; print(f'Reuters: {len(fetch_news_by_source(\"reuters\"))}'); print(f'WallStreetCN: {len(fetch_news_by_source(\"wallstreetcn\"))}')"

# 运行所有测试
python test_news_aggregator.py
python test_integration.py
```

## 核心特性

### ✅ 多源聚合
- 华尔街见闻（72+ 条）
- 路透社（64+ 条）
- 可轻松扩展到其他来源

### ✅ 前端功能
- 🔍 搜索：实时搜索新闻标题
- 🏷️ 筛选：按来源筛选
- 🌙 主题：深色/浅色切换
- 📱 响应式：桌面/平板/手机适配

### ✅ 数据统一
所有新闻统一为：
```python
{
    'title': '标题',
    'datetime': '2026-01-11 20:00:00',  # 北京时间
    'link': 'https://...',              # 绝对URL
    'source': 'wallstreetcn' 或 'reuters',
    'type': 'article'/'live'/'theme'
}
```

## 扩展新闻源

### 第1步：创建爬虫模块

创建 `get_xxx_news.py`：

```python
def get_xxx_news(use_cache=True, cache_ttl=60):
    """从 XXX 获取新闻"""
    # 实现爬虫逻辑
    return [
        {
            'title': '标题',
            'datetime': '2026-01-11 20:00:00',
            'link': 'https://xxx.com/article/123',
            'source': 'xxx',
            'type': 'article'
        },
        # ...
    ]
```

### 第2步：添加 Source 类

在 `news_aggregator.py` 中：

```python
from get_xxx_news import get_xxx_news

class XxxSource(NewsSource):
    @staticmethod
    def fetch(use_cache=True, cache_ttl=60):
        return get_xxx_news(use_cache, cache_ttl)
```

### 第3步：注册来源

在 `NewsAggregator.__init__` 中：

```python
self.sources = {
    'wallstreetcn': WallStreetCNSource(),
    'reuters': ReutersSource(),
    'xxx': XxxSource(),  # 添加这行
}
```

### 第4步：更新配置

在 `generate_news_page.py` 的 `source_config` 中：

```python
source_config = {
    'wallstreetcn': {'name': '华尔街见闻', 'color': '#1478F0', 'icon': 'W'},
    'reuters': {'name': '路透社', 'color': '#FF8000', 'icon': 'R'},
    'xxx': {'name': 'XXX', 'color': '#00AA00', 'icon': 'X'},  # 添加这行
}
```

完成！新来源会自动出现在页面中。

## 故障排除

### 爬虫返回 0 条新闻

**原因**：网站结构改变或被屏蔽

**解决**：
```bash
# 1. 检查网络
ping www.example.com

# 2. 查看爬虫日志
python get_xxx_news.py

# 3. 检查 User-Agent
# 更新 headers 中的 User-Agent

# 4. 手动验证 URL
curl -H "User-Agent: Mozilla/5.0..." https://www.example.com
```

### 页面不更新

**原因**：缓存问题或生成失败

**解决**：
```bash
# 清除缓存，强制重新获取
python -c "from news_aggregator import _global_aggregator; _global_aggregator = None"

# 检查错误
python scripts/generate_news_page.py 2>&1 | tail -20
```

### 日期时间不对

**原因**：时区设置

**解决**：
确保系统时区是 Asia/Shanghai
```bash
# 检查时区
date

# 或强制使用北京时间（代码中已处理）
from zoneinfo import ZoneInfo
from datetime import datetime
datetime.now(ZoneInfo('Asia/Shanghai'))
```

## 性能优化建议

1. **缓存优化**
   - 增加 `cache_ttl` 参数（默认 60秒）
   - 避免频繁的重复请求

2. **爬虫优化**
   - 并发爬取多个来源（使用 `asyncio`）
   - 使用更智能的选择器
   - 实现增量更新

3. **页面优化**
   - 分页加载大量新闻
   - 虚拟滚动
   - 压缩 HTML/CSS/JS

## 相关资源

- 项目 GitHub：[naomi3ll/daily_news](https://github.com/naomi3ll/daily_news)
- 详细文档：[README.md](./README.md)
- 实现细节：[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)

## 许可证

MIT

## 支持

遇到问题？
1. 查看 [README.md](./README.md) 详细文档
2. 运行测试：`python test_integration.py`
3. 检查 GitHub Issues
4. 提交新的 Issue 描述问题

---

**祝你使用愉快！** 📰
