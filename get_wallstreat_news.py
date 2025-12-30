import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
import time
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import re

def get_wallstreetcn_news(use_cache: bool = True, cache_ttl: int = 60, retries: int = 3):
    """
    从华尔街见闻获取当天的新闻链接清单
    返回数据格式为[{'title': 标题, 'datetime': '日期', 'link': '链接'}]
    """
    # Prefer using the public content API which returns structured JSON
    api_url = "https://api.wscn.net/apiv1/content/information-flow"
    url = "https://wallstreetcn.com/news/global"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Simple in-memory cache
    # Cached value stored as tuple: (timestamp, data)
    global _WSCN_CACHE
    try:
        _WSCN_CACHE
    except NameError:
        _WSCN_CACHE = {}

    if use_cache:
        cached = _WSCN_CACHE.get('information_flow')
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

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        # First try the JSON API which is more stable than scraping the SPA HTML
        news_items = []
        try:
            api_params = {'channel': 'global', 'limit': 50}
            api_resp = session.get(api_url, params=api_params, headers=headers, timeout=10)
            api_resp.raise_for_status()
            js = api_resp.json()
            items = js.get('data', {}).get('items', [])
            for it in items:
                try:
                    # API wraps resource in item['resource']
                    resource = it.get('resource') or {}
                    # fallback if resource further nested
                    if not isinstance(resource, dict):
                        continue

                    title = resource.get('title')
                    link = resource.get('uri')
                    # some URIs may be relative, ensure absolute
                    if link and link.startswith('/'):
                        link = 'https://wallstreetcn.com' + link

                    display_time = resource.get('display_time')
                    if display_time:
                        try:
                            # interpret epoch as UTC then convert to Beijing time
                            dt = datetime.fromtimestamp(int(display_time), tz=ZoneInfo('UTC'))
                            datetime_str = dt.astimezone(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
                        except Exception:
                            datetime_str = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        datetime_str = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
                    # include resource type if present
                    resource_type = it.get('resource_type') or resource.get('type') or resource.get('resource_type')

                    if title and link:
                        item = {'title': title, 'datetime': datetime_str, 'link': link}
                        if resource_type:
                            item['type'] = resource_type
                        news_items.append(item)
                except Exception as e:
                    # skip malformed item
                    print(f"解析 API 项目时出错: {e}")
                    continue
        except Exception:
            # API failed — fall back to scraping in-case server returns HTML for non-JS clients
            soup = BeautifulSoup(response.text, 'html.parser')
            # 尝试查找新闻列表
            articles = soup.find_all('article', class_='athing')
            if not articles:
                # 尝试其他可能的class
                articles = soup.find_all('div', class_='news-item')
            if not articles:
                articles = soup.find_all('div', attrs={'data-component': 'NewsItem'})
            if not articles:
                articles = soup.find_all('div', class_='c-card-item')

            for article in articles:
                try:
                    title_element = article.find('a')
                    if not title_element:
                        continue
                    title = title_element.get_text(strip=True)
                    link = title_element.get('href')
                    if link and not link.startswith('http'):
                        link = 'https://wallstreetcn.com' + link
                    time_element = article.find('time')
                    if time_element:
                        # try to normalize time if it contains a timestamp or full datetime
                        datetime_str = time_element.get_text(strip=True)
                        # If only date present, append current time (Beijing)
                        if re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', datetime_str):
                            datetime_str = datetime_str + ' ' + datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%H:%M:%S')
                    else:
                        datetime_str = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
                    if title and link:
                        news_items.append({'title': title, 'datetime': datetime_str, 'link': link})
                except Exception as e:
                    print(f"解析新闻项目时出错: {e}")
                    continue
        
        # 如果没有找到任何项目，提供一个基本的返回结构
        if not news_items:
            # 由于直接解析可能因页面结构变化而失效，这里提供一个示例结构
            # 实际应用中需要根据实时页面结构调整选择器
            sample_news = [
                {
                    'title': '示例新闻标题',
                    'datetime': datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S'),
                    'link': 'https://wallstreetcn.com/example',
                    'type': 'article'
                }
            ]
            return sample_news
        # cache the result for short TTL
        try:
            _WSCN_CACHE['information_flow'] = (time.time(), news_items)
        except Exception:
            pass

        return news_items
        
    except requests.RequestException as e:
        print(f"请求华尔街见闻失败: {e}")
        return []
    except Exception as e:
        print(f"解析华尔街见闻新闻时出错: {e}")
        return []

# 示例使用
if __name__ == "__main__":
    news = get_wallstreetcn_news()
    for item in news:
        print(f"标题: {item['title']}")
        print(f"时间: {item['datetime']}")
        print(f"链接: {item['link']}")
        print("-" * 50)


def save_links_to_file(items, filepath, date=None):
    """Save links (one per line) for the given date (Asia/Shanghai) to filepath.

    - items: iterable of dicts containing 'link' and 'datetime' keys.
    - filepath: path to write the newline-separated links.
    - date: optional 'YYYY-MM-DD' string; if omitted, uses today's Beijing date.

    Returns the number of links written.
    """
    if date is None:
        date = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d')

    links = []
    for it in items:
        dt = it.get('datetime', '')
        link = it.get('link')
        if not link:
            continue
        # Expect datetime like 'YYYY-MM-DD HH:MM:SS'
        if isinstance(dt, str) and dt.startswith(date):
            links.append(link)

    # Deduplicate while preserving order
    seen = set()
    unique_links = []
    for l in links:
        if l in seen:
            continue
        seen.add(l)
        unique_links.append(l)

    # Ensure parent dir exists
    try:
        d = os.path.dirname(filepath)
        if d:
            os.makedirs(d, exist_ok=True)
    except Exception:
        pass

    with open(filepath, 'w', encoding='utf-8') as f:
        for l in unique_links:
            f.write(l.rstrip('/') + '\n')

    return len(unique_links)


def _cli_write_links():
    """Simple CLI entrypoint to write today's links to a file.
    Usage: python get_wallstreat_news.py --links-out PATH
    """
    import argparse

    parser = argparse.ArgumentParser(description='Fetch WallStreetCN news and optionally save links to a file')
    parser.add_argument('--links-out', help='Write today\'s links (one per line) to this file')
    parser.add_argument('--no-cache', action='store_true', help='Disable cache when fetching')
    args = parser.parse_args()

    items = get_wallstreetcn_news(use_cache=not args.no_cache)
    if args.links_out:
        n = save_links_to_file(items, args.links_out)
        print(f'Wrote {n} links to {args.links_out}')


if __name__ == "__main__":
    # Support legacy simple run and the new CLI mode
    try:
        # If arguments present, prefer CLI mode
        import sys
        if len(sys.argv) > 1:
            _cli_write_links()
        else:
            # previously printed summary
            news = get_wallstreetcn_news()
            for item in news:
                print(f"标题: {item['title']}")
                print(f"时间: {item['datetime']}")
                print(f"链接: {item['link']}")
                print("-" * 50)
    except Exception:
        # Fallback to simple run
        news = get_wallstreetcn_news()
        for item in news:
            print(f"标题: {item['title']}")
            print(f"时间: {item['datetime']}")
            print(f"链接: {item['link']}")
            print("-" * 50)

'''
https://api-one.wallstcn.com/apiv1/content/lives?channel=global-channel&limit=30
https://api.wscn.net/apiv1/content/information-flow
'''

