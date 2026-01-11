"""
统一的新闻源接口
支持从多个新闻源获取新闻，返回统一的数据格式
"""
from typing import List, Dict, Any, Optional
from get_wallstreat_news import get_wallstreetcn_news
from get_reuters_news import get_reuters_news
from datetime import datetime
from zoneinfo import ZoneInfo


class NewsSource:
    """新闻源的基类"""
    
    @staticmethod
    def fetch(use_cache: bool = True, cache_ttl: int = 60) -> List[Dict[str, Any]]:
        """
        获取新闻
        返回格式: [{'title': str, 'datetime': str, 'link': str, 'source': str, 'type': str}]
        """
        raise NotImplementedError


class WallStreetCNSource(NewsSource):
    """华尔街见闻新闻源"""
    
    @staticmethod
    def fetch(use_cache: bool = True, cache_ttl: int = 60) -> List[Dict[str, Any]]:
        items = get_wallstreetcn_news(use_cache=use_cache, cache_ttl=cache_ttl)
        # 确保所有项都有 source 字段
        for item in items:
            if 'source' not in item:
                item['source'] = 'wallstreetcn'
        return items


class ReutersSource(NewsSource):
    """路透社新闻源"""
    
    @staticmethod
    def fetch(use_cache: bool = True, cache_ttl: int = 60) -> List[Dict[str, Any]]:
        return get_reuters_news(use_cache=use_cache, cache_ttl=cache_ttl)


class NewsAggregator:
    """新闻聚合器 - 从多个来源获取新闻"""
    
    def __init__(self, sources: Optional[List[NewsSource]] = None):
        """
        初始化聚合器
        Args:
            sources: 新闻源列表，默认使用所有可用来源
        """
        if sources is None:
            # 默认使用所有来源
            self.sources = {
                'wallstreetcn': WallStreetCNSource(),
                'reuters': ReutersSource(),
            }
        else:
            self.sources = {source.__class__.__name__.lower(): source for source in sources}
    
    def fetch_all(self, use_cache: bool = True, cache_ttl: int = 60) -> List[Dict[str, Any]]:
        """
        从所有来源获取新闻，合并后按时间倒序排列
        
        Args:
            use_cache: 是否使用缓存
            cache_ttl: 缓存有效期（秒）
        
        Returns:
            按时间倒序排列的新闻列表
        """
        all_items = []
        
        for source_name, source in self.sources.items():
            try:
                items = source.fetch(use_cache=use_cache, cache_ttl=cache_ttl)
                all_items.extend(items)
            except Exception as e:
                print(f"从 {source_name} 获取新闻时出错: {e}")
        
        # 按时间倒序排列（最新的在前）
        try:
            all_items.sort(
                key=lambda x: datetime.strptime(x.get('datetime', '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S'),
                reverse=True
            )
        except Exception as e:
            print(f"排序新闻时出错: {e}")
        
        return all_items
    
    def fetch_by_source(self, source_name: str, use_cache: bool = True, cache_ttl: int = 60) -> List[Dict[str, Any]]:
        """
        从指定来源获取新闻
        
        Args:
            source_name: 来源名称 ('wallstreetcn', 'reuters' 等)
            use_cache: 是否使用缓存
            cache_ttl: 缓存有效期（秒）
        
        Returns:
            新闻列表
        """
        if source_name not in self.sources:
            raise ValueError(f"未知的新闻源: {source_name}")
        
        return self.sources[source_name].fetch(use_cache=use_cache, cache_ttl=cache_ttl)


# 全局聚合器实例
_global_aggregator = None


def get_aggregator() -> NewsAggregator:
    """获取全局新闻聚合器实例"""
    global _global_aggregator
    if _global_aggregator is None:
        _global_aggregator = NewsAggregator()
    return _global_aggregator


def fetch_all_news(use_cache: bool = True, cache_ttl: int = 60) -> List[Dict[str, Any]]:
    """
    便利函数 - 从所有来源获取新闻
    """
    return get_aggregator().fetch_all(use_cache=use_cache, cache_ttl=cache_ttl)


def fetch_news_by_source(source: str, use_cache: bool = True, cache_ttl: int = 60) -> List[Dict[str, Any]]:
    """
    便利函数 - 从指定来源获取新闻
    """
    return get_aggregator().fetch_by_source(source, use_cache=use_cache, cache_ttl=cache_ttl)


if __name__ == '__main__':
    # 测试
    print("从所有来源获取新闻...")
    items = fetch_all_news(use_cache=False)
    print(f"共找到 {len(items)} 条新闻")
    
    # 按来源分类显示
    sources = {}
    for item in items:
        source = item.get('source', 'unknown')
        if source not in sources:
            sources[source] = 0
        sources[source] += 1
    
    print("\n来源统计:")
    for source, count in sources.items():
        print(f"  {source}: {count} 条")
    
    print("\n最新 5 条新闻:")
    for item in items[:5]:
        print(f"  [{item['source']}] {item['title'][:60]}...")
        print(f"  时间: {item['datetime']}")
        print()
