import re
from get_wallstreat_news import get_wallstreetcn_news

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


if __name__ == '__main__':
    try:
        test_fetch_and_datetime_format()
        print('test_fetch_and_datetime_format: OK')
        test_cache_behavior()
        print('test_cache_behavior: OK')
    except AssertionError as e:
        print('Test failed:', e)
        raise
