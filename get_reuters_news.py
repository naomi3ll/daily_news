import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
import time
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import re
import json

def get_reuters_news(use_cache: bool = True, cache_ttl: int = 60, retries: int = 3):
    """
    从路透社获取当天的新闻链接清单
    返回数据格式为[{'title': 标题, 'datetime': '日期', 'link': '链接', 'source': 'reuters'}]
    """
    urls = [
        "https://www.reuters.com/world",
        "https://www.reuters.com/business",
        "https://www.reuters.com/markets",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
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
            return cached[1]

    # Prepare a requests session with retries/backoff
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    news_items = []
    
    for url in urls:
        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try different article selection strategies
            # Strategy 1: Look for article links with specific patterns
            article_links = soup.find_all('a', href=re.compile(r'/article/|/world/|/business/|/markets/'))
            
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
            print(f"获取路透社 {url} 时出错: {e}")
            continue
    
    # Remove duplicates while preserving order
    seen_titles = set()
    unique_items = []
    for item in news_items:
        if item['title'] not in seen_titles:
            seen_titles.add(item['title'])
            unique_items.append(item)
    
    # If we got articles, cache them
    if unique_items:
        _REUTERS_CACHE['articles'] = (time.time(), unique_items)
    
    return unique_items


if __name__ == '__main__':
    # Test the function
    print("Fetching Reuters news...")
    items = get_reuters_news(use_cache=False)
    print(f"Found {len(items)} articles")
    for item in items[:5]:
        print(f"  - {item['title'][:60]}... ({item['datetime']})")
        print(f"    Link: {item['link']}")

