import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from get_wallstreat_news import get_wallstreetcn_news, save_links_to_file

def test_fetch_and_datetime_format():
    news = get_wallstreetcn_news(use_cache=False)
    assert isinstance(news, list)
    assert len(news) > 0
    # check datetime format YYYY-MM-DD HH:MM:SS
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
    for item in news[:5]:
        assert 'title' in item and 'datetime' in item and 'link' in item
        assert pattern.match(item['datetime'])


def test_cache_behavior():
    # fetch with cache enabled
    a = get_wallstreetcn_news(use_cache=True, cache_ttl=60)
    b = get_wallstreetcn_news(use_cache=True, cache_ttl=60)
    assert isinstance(a, list) and isinstance(b, list)
    assert len(a) == len(b)
    # now force no-cache
    c = get_wallstreetcn_news(use_cache=False)
    assert isinstance(c, list)


def test_save_links_to_file(tmp_path):
    today = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d')
    yesterday = (datetime.now(ZoneInfo('Asia/Shanghai')) - timedelta(days=1)).strftime('%Y-%m-%d')
    items = [
        {'title': 'A', 'datetime': f'{today} 10:00:00', 'link': 'https://wallstreetcn.com/a'},
        {'title': 'B', 'datetime': f'{today} 11:00:00', 'link': 'https://wallstreetcn.com/b'},
        {'title': 'C', 'datetime': f'{yesterday} 09:00:00', 'link': 'https://wallstreetcn.com/old'},
        # duplicate link
        {'title': 'B duplicate', 'datetime': f'{today} 11:00:00', 'link': 'https://wallstreetcn.com/b'},
    ]
    out = tmp_path / 'links.txt'
    n = save_links_to_file(items, str(out), date=today)
    assert n == 2
    text = out.read_text(encoding='utf-8').strip().splitlines()
    assert text == ['https://wallstreetcn.com/a', 'https://wallstreetcn.com/b']


if __name__ == '__main__':
    try:
        test_fetch_and_datetime_format()
        print('test_fetch_and_datetime_format: OK')
        test_cache_behavior()
        print('test_cache_behavior: OK')
    except AssertionError as e:
        print('Test failed:', e)
        raise
