import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
import time
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import re
import json
import sys
import os

def get_reuters_news(use_cache: bool = True, cache_ttl: int = 60, retries: int = 5):
    """
    从路透社获取当天的新闻链接清单
    返回数据格式为[{'title': 标题, 'datetime': '日期', 'link': '链接', 'source': 'reuters'}]
    """
    # 支持多个备用 URL（如果某个 URL 无法访问）
    urls = [
        "https://www.reuters.com/world",
        "https://www.reuters.com/business",
        "https://www.reuters.com/markets",
        # 备用 URL
        "https://www.reuters.com/finance",
        "https://www.reuters.com/technology",
    ]
    
    # 多个 User-Agent 轮询，避免被检测为爬虫
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    
    headers = {
        'User-Agent': user_agents[0],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }
    
    # Simple in-memory cache
    global _REUTERS_CACHE
    try:
        _REUTERS_CACHE
    except NameError:
        _REUTERS_CACHE = {}

    if use_cache:
        cached = _REUTERS_CACHE.get('articles')
        if cached and (time.time() - cached[0]) < cache_ttl:
            print("[Reuters] 使用缓存数据", file=sys.stderr)
            return cached[1]

    # Prepare a requests session with retries/backoff
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=1.5,  # 增加退避因子
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    news_items = []
    failed_urls = []
    
    for url in urls:
        try:
            print(f"[Reuters] 获取 {url}", file=sys.stderr)
            response = session.get(url, headers=headers, timeout=20)  # 增加到 20 秒
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            print(f"[Reuters] 状态码: {response.status_code}, 内容长度: {len(response.content)}", file=sys.stderr)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try different article selection strategies
            # Strategy 1: Look for article links with specific patterns
            article_links = soup.find_all('a', href=re.compile(r'/article/|/world/|/business/|/markets/|/finance/|/technology/'))
            
            # 如果没有找到，尝试找所有链接
            if not article_links:
                print(f"[Reuters] {url} 未找到标准文章链接，尝试其他方式...", file=sys.stderr)
                article_links = soup.find_all('a', href=re.compile(r'^/[a-z]+/'))
            
            print(f"[Reuters] {url} 找到 {len(article_links)} 个链接", file=sys.stderr)
            
            seen = set()
            
            for link in article_links:
                try:
                    href = link.get('href', '').strip()
                    
                    if not href or href in seen:
                        continue
                    
                    seen.add(href)
                    
                    # Find title - try different approaches
                    title = None
                    
                    # Try to get text from the link itself
                    title_text = link.get_text(strip=True)
                    if title_text and len(title_text) > 10:
                        title = title_text
                    
                    # Or try to find a heading inside
                    if not title:
                        heading = link.find(['h2', 'h3', 'h4'])
                        if heading:
                            title = heading.get_text(strip=True)
                    
                    # Or look for span with text
                    if not title:
                        for span in link.find_all('span'):
                            text = span.get_text(strip=True)
                            if text and len(text) > 10:
                                title = text
                                break
                    
                    if not title or len(title) < 5:
                        continue
                    
                    # Build absolute URL
                    if href.startswith('/'):
                        link_url = 'https://www.reuters.com' + href
                    elif href.startswith('http'):
                        link_url = href
                    else:
                        continue
                    
                    # Try to find datetime
                    datetime_str = datetime.now(ZoneInfo('UTC')).astimezone(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Look for time element in nearby elements
                    parent = link.find_parent('article') or link.find_parent('div', recursive=True)
                    if parent:
                        time_elem = parent.find('time')
                        if time_elem and time_elem.get('datetime'):
                            try:
                                dt = datetime.fromisoformat(time_elem.get('datetime').replace('Z', '+00:00'))
                                datetime_str = dt.astimezone(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
                            except Exception:
                                pass
                    
                    if title and link_url:
                        item = {
                            'title': title,
                            'datetime': datetime_str,
                            'link': link_url,
                            'source': 'reuters',
                            'type': 'article'
                        }
                        news_items.append(item)
                        
                except Exception as e:
                    continue
                    
        except requests.exceptions.RequestException as e:
            print(f"[Reuters] 获取 {url} 时出错: {type(e).__name__}: {e}", file=sys.stderr)
            failed_urls.append(url)
            continue
        except Exception as e:
            print(f"[Reuters] 解析 {url} 时出错: {type(e).__name__}: {e}", file=sys.stderr)
            failed_urls.append(url)
            continue
    
    # Remove duplicates while preserving order
    seen_titles = set()
    unique_items = []
    for item in news_items:
        if item['title'] not in seen_titles:
            seen_titles.add(item['title'])
            unique_items.append(item)
    
    print(f"[Reuters] 获取完成: 成功 {len(urls) - len(failed_urls)}/{len(urls)}, 共 {len(unique_items)} 条新闻", file=sys.stderr)
    
    # 如果没有获取到任何新闻，记录详细的诊断信息
    if not unique_items:
        print("[Reuters] 错误: 未获取到任何新闻", file=sys.stderr)
        print(f"[Reuters] 失败的 URL: {failed_urls}", file=sys.stderr)
        print("[Reuters] 可能原因:", file=sys.stderr)
        print("[Reuters]   1. IP 地址被限制", file=sys.stderr)
        print("[Reuters]   2. 网站结构改变", file=sys.stderr)
        print("[Reuters]   3. 网络连接问题", file=sys.stderr)
        print("[Reuters] 将尝试返回过期缓存数据...", file=sys.stderr)
    
    # If we got articles, cache them
    if unique_items:
        _REUTERS_CACHE['articles'] = (time.time(), unique_items)
        return unique_items
    else:
        # 如果本次获取失败但有缓存，返回缓存的旧数据（容错）
        if use_cache and 'articles' in _REUTERS_CACHE:
            print("[Reuters] 本次获取失败，返回过期的缓存数据作为备用", file=sys.stderr)
            return _REUTERS_CACHE['articles'][1]
        return unique_items


if __name__ == '__main__':
    # Test the function
    print("Fetching Reuters news...")
    items = get_reuters_news(use_cache=False)
    print(f"Found {len(items)} articles")
    for item in items[:5]:
        print(f"  - {item['title'][:60]}... ({item['datetime']})")
        print(f"    Link: {item['link']}")

