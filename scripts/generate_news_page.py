#!/usr/bin/env python3
"""Fetch news from multiple sources and render a simple HTML page to docs/index.html"""
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import sys
import html as _html

# Ensure project root is on sys.path so imports work when script is executed from scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from news_aggregator import fetch_all_news


def calculate_hotness(item):
    """
    计算新闻热度
    基于：标题长度、关键词出现频率等因素
    """
    title = item.get('title', '').lower()
    hotness = 0
    
    # 财经关键词增加热度
    financial_keywords = {
        '暴涨': 10, '暴跌': 10, '新高': 8, '大涨': 8, '大跌': 8,
        '突破': 7, '崩盘': 9, '获批': 8, '制裁': 8, '调查': 7,
        '创纪录': 9, '牛市': 8, '熊市': 8, '反弹': 6, '下跌': 5,
        '增长': 4, '下降': 4, '上涨': 5, '跌停': 9, '涨停': 9,
        '飙升': 8, '飙低': 8, '风险': 5, '预期': 3, '预测': 3,
    }
    
    for keyword, weight in financial_keywords.items():
        hotness += title.count(keyword.lower()) * weight
    
    return hotness


def parse_datetime(dt_str):
    """解析日期时间字符串，用于排序"""
    if not dt_str:
        return datetime.min
    try:
        # 尝试解析常见格式
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']:
            try:
                return datetime.strptime(dt_str.strip(), fmt)
            except ValueError:
                continue
        return datetime.min
    except:
        return datetime.min


def render_html(items):
    now = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
    
    # Source configuration with display names and icons
    source_config = {
        'wallstreetcn': {'name': '华尔街见闻', 'color': '#1478F0', 'icon': 'W'},
        'reuters': {'name': '路透社', 'color': '#FF8000', 'icon': 'R'},
    }
    
    # 为每条新闻添加热度分数
    for item in items:
        item['hotness'] = calculate_hotness(item)
        item['datetime_obj'] = parse_datetime(item.get('datetime', ''))
    
    # 按时间倒序排列（第一优先级），热度相同则按热度降序排列（第二优先级）
    sorted_items = sorted(
        items,
        key=lambda x: (-x['datetime_obj'].timestamp(), -x['hotness']),
        reverse=False
    )
    
    rows = []
    rows.append(f"<ul class='cards'>")
    
    # Render all items in merged timeline
    for it in sorted_items:
        title = it.get('title', '')
        link = it.get('link', '#')
        dt = it.get('datetime', '')
        rtype = it.get('type', '')
        source = it.get('source', 'unknown')
        
        # Get source badge
        config = source_config.get(source, {'name': source.upper(), 'color': '#6b7280', 'icon': source[0].upper()})
        color = config['color']
        icon = config['icon']
        config_name = config['name']
        source_badge = f"<span class='source-badge' style='background-color: {color}' title='{config_name}'>{icon}</span>"
        
        badge = f"<span class='badge'>{rtype}</span>" if rtype else ''
        # escape title to avoid HTML injection
        safe_title = _html.escape(title)
        rows.append(
            f"  <li class='card' data-source='{source}'><a href='{link}' target='_blank' rel='noopener noreferrer' class='title'>{safe_title}</a> <div class='meta'>{source_badge}{badge}<time>{dt}</time></div></li>"
        )
    
    rows.append(f"</ul>")
    
    rows_html = "\n      ".join(rows)
    # Inline SVG logo
    logo_svg = """<svg xmlns='http://www.w3.org/2000/svg' width='36' height='36' viewBox='0 0 64 64' aria-hidden='true'><rect rx='8' ry='8' width='64' height='64' fill='#1478F0'/><text x='50%' y='54%' text-anchor='middle' font-family='Arial, sans-serif' font-size='28' fill='#fff' font-weight='700'>📰</text></svg>"""
    # Inline GitHub icon (monochrome; uses currentColor)
    github_svg = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='20' height='20' aria-hidden='true' fill='currentColor'><path d='M12 .5C5.73.5.5 5.73.5 12c0 5.08 3.29 9.39 7.86 10.91.57.1.78-.25.78-.55 0-.27-.01-1-0.02-1.97-3.2.7-3.88-1.37-3.88-1.37-.52-1.33-1.26-1.69-1.26-1.69-1.03-.7.08-.69.08-.69 1.14.08 1.74 1.17 1.74 1.17 1.01 1.73 2.65 1.23 3.3.94.1-.74.4-1.23.73-1.52-2.56-.29-5.26-1.28-5.26-5.72 0-1.26.45-2.29 1.18-3.1-.12-.29-.51-1.45.11-3.02 0 0 .96-.31 3.15 1.18.92-.26 1.9-.39 2.88-.39.98 0 1.96.13 2.88.39 2.19-1.49 3.15-1.18 3.15-1.18.62 1.57.23 2.73.11 3.02.73.81 1.18 1.84 1.18 3.1 0 4.45-2.7 5.43-5.28 5.71.41.35.78 1.04.78 2.1 0 1.52-.01 2.75-.01 3.13 0 .3.21.65.79.54C20.71 21.39 24 17.08 24 12c0-6.27-5.23-11.5-12-11.5z'/></svg>"""

    body = f"""
<html>
  <head>
    <meta charset='utf-8'/>
    <meta name='description' content='多源财经新闻聚合 — 自动抓取并更新华尔街见闻、路透社等新闻源，展示最新财经资讯。' />
    <meta property='og:title' content='每日新闻 - 财经资讯聚合' />
    <meta property='og:description' content='多源财经新闻聚合 — 自动抓取并更新，展示最新财经资讯。' />
    <meta property='og:type' content='website' />
    <meta property='og:url' content='https://naomi3ll.github.io/daily_news' />
    <meta name='theme-color' content='#1478F0' />
    <link rel='icon' href='data:image/svg+xml;utf8,{_html.escape(logo_svg)}' />
    <meta name='viewport' content='width=device-width,initial-scale=1' />
    <title>每日新闻 - 财经资讯聚合</title>
    <style>
      :root{{--bg:#f6f8fb;--card:#fff;--muted:#6b7280;--accent:#1478F0;--fg:#111;--title-color:#0f172a;--card-border:rgba(16,24,40,0.04);--shadow:0 1px 3px rgba(16,24,40,0.06);--badge-bg:#eef2ff}}
      [data-theme='dark']{{--bg:#0f1724;--card:#0b1220;--muted:#9fb0c2;--accent:#60a5fa;--fg:#eaf4ff;--title-color:#ffffff;--card-border:rgba(255,255,255,0.06);--shadow:0 2px 8px rgba(0,0,0,0.6);--badge-bg:rgba(96,165,250,0.12)}}
      body{{font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; background:var(--bg); margin:0; padding:40px; color:var(--fg)}}
      .container{{max-width:1200px;margin:0 auto}}
      header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:30px;flex-wrap:wrap;gap:20px}}
      .brand{{display:flex;align-items:center;gap:12px}}
      .brand .logo{{width:40;height:40;display:inline-flex;align-items:center;justify-content:center;font-size:24px}}
      .theme-toggle{{background:transparent;border:1px solid rgba(16,24,40,0.06);padding:6px 10px;border-radius:8px;cursor:pointer;color:var(--fg);font-size:13px}}
      .theme-toggle:hover{{background:rgba(16,24,40,0.02)}}
      h1{{font-size:24px;margin:0;font-weight:700}}
      .subtitle{{color:var(--muted);font-size:14px;margin-top:4px}}
      .generated{{color:var(--muted);font-size:13px}}
      .stats{{display:flex;gap:20px;margin-top:10px;font-size:13px}}
      .stat-item{{display:flex;align-items:center;gap:6px}}
      .stat-value{{font-weight:600;color:var(--accent)}}
      ul.cards{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px;margin:0}}
      li.card{{background:var(--card);padding:16px;border-radius:8px;box-shadow:var(--shadow);border:1px solid var(--card-border);transition:all 0.2s ease}}
      li.card:hover{{transform:translateY(-2px);box-shadow:0 4px 12px rgba(16,24,40,0.12)}}
      a.title{{font-weight:600;color:var(--title-color);text-decoration:none;display:block;margin-bottom:8px;font-size:15px;line-height:1.4;word-break:break-word}}
      a.title:hover{{color:var(--accent)}}
      .meta{{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:12px}}
      .badge{{background:var(--badge-bg);color:var(--accent);padding:3px 8px;border-radius:999px;font-size:11px;font-weight:500}}
      footer{{margin-top:40px;padding-top:20px;border-top:1px solid var(--card-border);color:var(--muted);font-size:13px;text-align:center}}
      .github-banner{{background:linear-gradient(90deg, rgba(20,120,240,0.06), rgba(20,120,240,0.02));padding:12px;border-radius:8px;margin-bottom:24px;display:flex;align-items:center;gap:10px}}
      .github-banner a{{text-decoration:none;color:var(--accent);font-weight:600}}
      .github-link svg{{display:inline-block;vertical-align:middle;color:var(--accent)}}
      .github-link{{display:inline-block;padding:4px;border-radius:6px;transition:all 0.2s}}
      .github-link:hover{{background:rgba(16,24,40,0.04)}}
      @media(max-width:640px){{
        body{{padding:20px}}
        header{{flex-direction:column;align-items:flex-start}}
        h1{{font-size:20px}}
        ul.cards{{grid-template-columns:1fr}}
      }}
      .filters{{display:flex;gap:8px;margin:16px 0;flex-wrap:wrap}}
      .filter-btn{{padding:6px 12px;border:1px solid var(--card-border);background:var(--card);border-radius:6px;cursor:pointer;transition:all 0.2s;color:var(--fg);font-size:13px}}
      .filter-btn:hover{{background:rgba(20,120,240,0.06)}}
      .filter-btn.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}
      .icon-btn{{width:40px;height:36px;padding:6px;display:inline-flex;align-items:center;justify-content:center;border-radius:8px;border:none;background:transparent;color:var(--fg);cursor:pointer;transition:all 0.2s;}}
      .icon-btn:hover{{background:rgba(20,120,240,0.06)}}
      .icon-btn svg{{width:18px;height:18px;display:block}}
      .visually-hidden{{position:absolute!important;height:1px;width:1px;overflow:hidden;clip:rect(1px,1px,1px,1px);white-space:nowrap;border:0;padding:0;margin:-1px}}
      .search-box{{margin:16px 0}}
      .search-input{{width:100%;max-width:400px;padding:8px 12px;border:1px solid var(--card-border);border-radius:6px;background:var(--card);color:var(--fg);font-size:14px}}
      .search-input::placeholder{{color:var(--muted)}}
      .empty-state{{text-align:center;padding:40px 20px;color:var(--muted)}}
      .empty-state-icon{{font-size:48px;margin-bottom:16px}}
      /* Back to top button */
      .back-to-top{{position:fixed;bottom:30px;right:30px;width:44px;height:44px;background:var(--accent);color:#fff;border:none;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 4px 12px rgba(20,120,240,0.3);transition:all 0.3s ease;opacity:0;pointer-events:none;z-index:999}}
      .back-to-top.visible{{opacity:1;pointer-events:auto}}
      .back-to-top:hover{{transform:translateY(-2px);box-shadow:0 6px 16px rgba(20,120,240,0.4)}}
      .back-to-top:active{{transform:translateY(0)}}
      @media(max-width:640px){{.back-to-top{{width:40px;height:40px;bottom:20px;right:20px;font-size:18px}}}}
      /* List / Compact view styles */
      ul.cards.list-view {{ display: block; }}
      ul.cards.list-view li.card {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        padding: 10px 16px;
        border-radius: 6px;
        border: none;
        background: transparent;
        box-shadow: none;
      }}
      ul.cards.list-view .title {{ margin-bottom: 0; flex: 1; }}
      ul.cards.list-view .meta {{ margin-left: 20px; white-space: nowrap; }}
    </style>
  </head>
  <body>
    <div class='container'>
      <div class='github-banner'>
        <div style='display:flex;align-items:center;gap:10px'>
          <div class='logo' aria-hidden='true' style='font-size:24px'>📰</div>
          <div>Automatically generated by <a href='https://github.com/naomi3ll/daily_news' target='_blank' rel='noopener noreferrer'>daily_news</a>. Enable <strong>GitHub Pages</strong> to publish this page.</div>
        </div>
        <div style='margin-left:auto'><a class='github-link' href='https://github.com/naomi3ll/daily_news' target='_blank' rel='noopener noreferrer' aria-label='View on GitHub' title='View on GitHub'>{github_svg}</a></div>
      </div>

      <header>
        <div>
          <div class='brand'><div class='logo' style='font-size:32px'>📰</div><div><h1>每日新闻</h1><p class='subtitle'>财经资讯聚合平台</p></div></div>
        </div>
        <div style='text-align:right'>
          <div class='generated'>更新时间： {now}</div>
          <button class='theme-toggle' id='themeToggle'>🌙 切换主题</button>
        </div>
      </header>
      
      <div class='stats'>
        <div class='stat-item'><span>📊 共</span><span class='stat-value'>{len(items)}</span><span>条新闻</span></div>
      </div>

      <div class='search-box'>
        <input type='text' class='search-input' id='searchInput' placeholder='🔍 搜索新闻标题...'>
      </div>

      <div class='filters'>
        <button class='filter-btn active' data-filter='all'>全部</button>
        <button class='filter-btn' data-filter='wallstreetcn'>华尔街见闻</button>
        <button class='filter-btn' data-filter='reuters'>路透社</button>
        <button class='icon-btn' id='viewToggle' data-view='card' aria-pressed='false' aria-label='切换到列表视图' title='当前：卡片视图（点击切换到列表视图）' style='margin-left:auto'><svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor' stroke='none'><rect x='4' y='4' width='7' height='7' rx='1'/><rect x='13' y='4' width='7' height='7' rx='1'/><rect x='4' y='13' width='7' height='7' rx='1'/><rect x='13' y='13' width='7' height='7' rx='1'/></svg><span class='visually-hidden'>切换视图</span></button>
      </div>

      <div id='newsContainer' style='margin-top:24px'>
      {rows_html}
      </div>
      
      <footer><p>Made with ❤️ by Daily News Aggregator | Source: wallstreetcn.com, reuters.com</p></footer>
    </div>
    <button class='back-to-top' id='backToTop' title='回到顶部' aria-label='回到顶部'>↑</button>
    <script>
      // Theme toggle: default to LIGHT unless user previously saved a preference
      const toggle = document.getElementById('themeToggle');
      const root = document.documentElement;
      function setTheme(t){{
        root.setAttribute('data-theme', t);
        localStorage.setItem('theme', t);
        if(toggle) toggle.textContent = t === 'dark' ? '☀️ 切换浅色' : '🌙 切换深色';
      }}
      const saved = localStorage.getItem('theme');
      if(saved) setTheme(saved);
      else setTheme('light');
      toggle.addEventListener('click', ()=>{{
        const cur = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        setTheme(cur);
      }});

      // Search and filter functionality
      const searchInput = document.getElementById('searchInput');
      const filterBtns = document.querySelectorAll('.filter-btn');
      const container = document.getElementById('newsContainer');
      
      let currentFilter = 'all';
      let searchTerm = '';
      
      function filterNews() {{
        const items = container.querySelectorAll('li.card');
        let visibleCount = 0;
        
        items.forEach(item => {{
          const title = item.querySelector('.title').textContent.toLowerCase();
          const source = item.getAttribute('data-source');
          
          const matchesSearch = searchTerm === '' || title.includes(searchTerm.toLowerCase());
          const matchesFilter = currentFilter === 'all' || source === currentFilter;
          
          if (matchesSearch && matchesFilter) {{
            item.style.display = '';
            visibleCount++;
          }} else {{
            item.style.display = 'none';
          }}
        }});
        
        // Show empty state if no results
        if (visibleCount === 0) {{
          if (!container.querySelector('.empty-state')) {{
            const empty = document.createElement('div');
            empty.className = 'empty-state';
            empty.innerHTML = '<div class=\"empty-state-icon\">😔</div><p>未找到匹配的新闻</p>';
            container.appendChild(empty);
          }}
        }} else {{
          const empty = container.querySelector('.empty-state');
          if (empty) empty.remove();
        }}
      }}
      
      searchInput.addEventListener('input', (e) => {{
        searchTerm = e.target.value;
        filterNews();
      }});
      
      filterBtns.forEach(btn => {{
        btn.addEventListener('click', () => {{
          filterBtns.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          currentFilter = btn.dataset.filter;
          filterNews();
        }});
      }});

      // View toggle: card <-> list
      (function(){{
        const viewToggle = document.getElementById('viewToggle');
        const VIEW_KEY = 'daily_news_view_mode';
        const ICONS = {{ 
          list: '<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"currentColor\"><rect x=\"3\" y=\"4\" width=\"18\" height=\"2\" rx=\"1\"/><rect x=\"3\" y=\"9\" width=\"18\" height=\"2\" rx=\"1\"/><rect x=\"3\" y=\"14\" width=\"18\" height=\"2\" rx=\"1\"/><rect x=\"3\" y=\"19\" width=\"18\" height=\"2\" rx=\"1\"/></svg>',
          card: '<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"currentColor\" stroke=\"none\"><rect x=\"4\" y=\"4\" width=\"7\" height=\"7\" rx=\"1\"/><rect x=\"13\" y=\"4\" width=\"7\" height=\"7\" rx=\"1\"/><rect x=\"4\" y=\"13\" width=\"7\" height=\"7\" rx=\"1\"/><rect x=\"13\" y=\"13\" width=\"7\" height=\"7\" rx=\"1\"/></svg>'
        }};
        
        function applyView(mode) {{
          if(mode === 'list'){{
            document.querySelectorAll('ul.cards').forEach(u=>u.classList.add('list-view'));
            viewToggle.innerHTML = ICONS.card + \"<span class='visually-hidden'>切换视图</span>\";
            viewToggle.setAttribute('data-view','list');
            viewToggle.setAttribute('aria-pressed','true');
            viewToggle.setAttribute('aria-label','切换到卡片视图');
            viewToggle.title = '当前：列表视图（点击切换到卡片视图）';
          }} else {{
            document.querySelectorAll('ul.cards').forEach(u=>u.classList.remove('list-view'));
            viewToggle.innerHTML = ICONS.list + \"<span class='visually-hidden'>切换视图</span>\";
            viewToggle.setAttribute('data-view','card');
            viewToggle.setAttribute('aria-pressed','false');
            viewToggle.setAttribute('aria-label','切换到列表视图');
            viewToggle.title = '当前：卡片视图（点击切换到列表视图）';
          }}
          try{{ localStorage.setItem(VIEW_KEY, mode); }}catch(e){{}}
        }}

        try{{
          const saved = localStorage.getItem(VIEW_KEY);
          applyView(saved === 'list' ? 'list' : 'card');
        }}catch(e){{ applyView('card'); }}

        if(viewToggle){{
          viewToggle.addEventListener('click', function(){{
            const current = document.querySelectorAll('ul.cards')[0] && document.querySelectorAll('ul.cards')[0].classList.contains('list-view') ? 'list' : 'card';
            applyView(current === 'list' ? 'card' : 'list');
          }});
        }}
      }})();

      // Back to top button functionality
      (function(){{
        const backToTopBtn = document.getElementById('backToTop');
        if(!backToTopBtn) return;
        
        window.addEventListener('scroll', function(){{
          if(window.scrollY > 300){{
            backToTopBtn.classList.add('visible');
          }} else {{
            backToTopBtn.classList.remove('visible');
          }}
        }});
        
        backToTopBtn.addEventListener('click', function(){{
          window.scrollTo({{top: 0, behavior: 'smooth'}});
        }});
      }})();

      // Sentiment highlighting: highlight keywords in titles with colors
      (function(){{
        const bullishWords = ['暴涨', '新高', '大涨', '突破', '获批', '增长', '牛市', '飙升', '高歌', '反弹', '创纪录', '刷新', '激增', '狂涨', '飞升', 'Surge', 'Jump', 'Record', 'Bull', 'Gain', 'Rally', 'Soar', 'Boom', 'surge', 'jump', 'record', 'bull', 'gain', 'rally', 'soar', 'boom'];
        const bearishWords = ['暴跌', '崩盘', '调查', '制裁', '警告', '衰退', '下跌', '跌停', '腰斩', '暴降', '崩溃', '风险', '亏损', 'Plunge', 'Crash', 'Probe', 'Sanction', 'Warn', 'Recession', 'Decline', 'Fall', 'Slump', 'Loss', 'Risk', 'plunge', 'crash', 'probe', 'sanction', 'warn', 'recession', 'decline', 'fall', 'slump', 'loss', 'risk'];
        
        document.querySelectorAll('.title').forEach(link => {{
          let html = link.innerHTML;
          
          bullishWords.forEach(word => {{
            html = html.replace(new RegExp(word, 'gi'), `<span style="color:#ef4444;font-weight:800">${{word}}</span>`);
          }});
          
          bearishWords.forEach(word => {{
            html = html.replace(new RegExp(word, 'gi'), `<span style="color:#10b981;font-weight:800">${{word}}</span>`);
          }});
          
          link.innerHTML = html;
        }});
      }})();
    </script>
  </body>
</html>
"""
    return body


def main():
    items = fetch_all_news(use_cache=False)
    html = render_html(items)
    os.makedirs('docs', exist_ok=True)
    path = os.path.join('docs', 'index.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Wrote', path)
    print(f'Generated HTML with {len(items)} articles from multiple sources')


if __name__ == '__main__':
    main()
