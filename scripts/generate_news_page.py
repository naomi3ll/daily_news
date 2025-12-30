#!/usr/bin/env python3
"""Fetch WallStreetCN news and render a simple HTML page to docs/index.html"""
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import sys
import html as _html

# Ensure project root is on sys.path so imports work when script is executed from scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from get_wallstreat_news import get_wallstreetcn_news


def render_html(items):
    now = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
    rows = []
    for it in items:
        title = it.get('title', '')
        link = it.get('link', '#')
        dt = it.get('datetime', '')
        rtype = it.get('type', '')
        badge = f"<span class='badge'>{rtype}</span>" if rtype else ''
        # escape title to avoid HTML injection
        safe_title = _html.escape(title)
        rows.append(
            f"<li class='card'><a href='{link}' target='_blank' rel='noopener noreferrer' class='title'>{safe_title}</a> <div class='meta'>{badge}<time>{dt}</time></div></li>"
        )
    rows_html = "\n      ".join(rows)
    # Inline SVG logo
    logo_svg = """<svg xmlns='http://www.w3.org/2000/svg' width='36' height='36' viewBox='0 0 64 64' aria-hidden='true'><rect rx='8' ry='8' width='64' height='64' fill='#1478F0'/><text x='50%' y='54%' text-anchor='middle' font-family='Arial, sans-serif' font-size='28' fill='#fff' font-weight='700'>W</text></svg>"""
    # Inline GitHub icon (monochrome; uses currentColor)
    github_svg = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='20' height='20' aria-hidden='true' fill='currentColor'><path d='M12 .5C5.73.5.5 5.73.5 12c0 5.08 3.29 9.39 7.86 10.91.57.1.78-.25.78-.55 0-.27-.01-1-0.02-1.97-3.2.7-3.88-1.37-3.88-1.37-.52-1.33-1.26-1.69-1.26-1.69-1.03-.7.08-.69.08-.69 1.14.08 1.74 1.17 1.74 1.17 1.01 1.73 2.65 1.23 3.3.94.1-.74.4-1.23.73-1.52-2.56-.29-5.26-1.28-5.26-5.72 0-1.26.45-2.29 1.18-3.1-.12-.29-.51-1.45.11-3.02 0 0 .96-.31 3.15 1.18.92-.26 1.9-.39 2.88-.39.98 0 1.96.13 2.88.39 2.19-1.49 3.15-1.18 3.15-1.18.62 1.57.23 2.73.11 3.02.73.81 1.18 1.84 1.18 3.1 0 4.45-2.7 5.43-5.28 5.71.41.35.78 1.04.78 2.1 0 1.52-.01 2.75-.01 3.13 0 .3.21.65.79.54C20.71 21.39 24 17.08 24 12c0-6.27-5.23-11.5-12-11.5z'/></svg>"""

    body = f"""
<html>
  <head>
    <meta charset='utf-8'/>
    <meta name='description' content='每日华尔街见闻要闻 — 自动抓取并更新，展示最新财经新闻。' />
    <meta property='og:title' content='WallStreetCN - 最新要闻' />
    <meta property='og:description' content='每日华尔街见闻要闻 — 自动抓取并更新，展示最新财经新闻。' />
    <meta property='og:type' content='website' />
    <meta property='og:url' content='https://naomi3ll.github.io/daily_news' />
    <meta name='theme-color' content='#1478F0' />
    <link rel='icon' href='data:image/svg+xml;utf8,{_html.escape(logo_svg)}' />
    <meta name='viewport' content='width=device-width,initial-scale=1' />
    <title>WallStreetCN - Latest</title>
    <style>
      :root{{--bg:#f6f8fb;--card:#fff;--muted:#6b7280;--accent:#1478F0;--fg:#111;--title-color:#0f172a;--card-border:rgba(16,24,40,0.04);--shadow:0 1px 3px rgba(16,24,40,0.06);--badge-bg:#eef2ff}}
      [data-theme='dark']{{--bg:#0f1724;--card:#0b1220;--muted:#9fb0c2;--accent:#60a5fa;--fg:#eaf4ff;--title-color:#ffffff;--card-border:rgba(255,255,255,0.06);--shadow:0 2px 8px rgba(0,0,0,0.6);--badge-bg:rgba(96,165,250,0.12)}}
      body{{font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; background:var(--bg); margin:0; padding:40px; color:var(--fg)}}
      .container{{max-width:980px;margin:0 auto}}
      header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}}
      .brand{{display:flex;align-items:center;gap:12px}}
      .brand .logo{{width:36;height:36;display:inline-block}}
      .theme-toggle{{background:transparent;border:1px solid rgba(16,24,40,0.06);padding:6px 8px;border-radius:8px;cursor:pointer}}
      h1{{font-size:20px;margin:0}}
      .generated{{color:var(--muted);font-size:13px}}
      ul.cards{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}}
      li.card{{background:var(--card);padding:16px;border-radius:8px;box-shadow:var(--shadow);border:1px solid var(--card-border)}}
      a.title{{font-weight:600;color:var(--title-color);text-decoration:none;display:block;margin-bottom:8px;font-size:16px;line-height:1.3}}
      a.title:hover{{color:var(--accent)}}
      .meta{{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:13px}}
      .badge{{background:var(--badge-bg);color:var(--accent);padding:3px 8px;border-radius:999px;font-size:12px}}
      footer{{margin-top:36px;color:var(--muted);font-size:13px}}
      .github-banner{{background:linear-gradient(90deg, rgba(20,120,240,0.06), rgba(20,120,240,0.02));padding:10px;border-radius:8px;margin-bottom:18px;display:flex;align-items:center;gap:10px}}
      .github-banner a{{text-decoration:none;color:var(--accent);font-weight:600}}
        .github-link svg{{display:inline-block;vertical-align:middle;color:var(--accent)}}
        .github-link{{display:inline-block;padding:4px;border-radius:6px}}
        .github-link:hover{{background:rgba(16,24,40,0.04)}}
    </style>
  </head>
  <body>
    <div class='container'>
      <div class='github-banner'>
        <div style='display:flex;align-items:center;gap:10px'>
          <div class='logo' aria-hidden='true'>{logo_svg}</div>
          <div>Automatically generated by <a href='https://github.com/naomi3ll/daily_news' target='_blank' rel='noopener noreferrer'>daily_news</a>. Enable <strong>GitHub Pages</strong> to publish this page.</div>
        </div>
        <div style='margin-left:auto'><a class='github-link' href='https://github.com/naomi3ll/daily_news' target='_blank' rel='noopener noreferrer' aria-label='View on GitHub' title='View on GitHub'>{github_svg}</a></div>
      </div>

      <header>
        <div class='brand'><div class='logo' aria-hidden='true'>{logo_svg}</div><h1>WallStreetCN · 最新</h1></div>
        <div style='text-align:right'>
          <div class='generated'>生成时间： 北京时间 {now}</div>
          <button class='theme-toggle' id='themeToggle'>切换深色/浅色</button>
        </div>
      </header>
      <ul class='cards'>
      {rows_html}
      </ul>
      <footer><p>Generated by GitHub Action &middot; Source: wallstreetcn.com</p></footer>
    </div>
    <script>
      // Theme toggle: default to LIGHT unless user previously saved a preference
      const toggle = document.getElementById('themeToggle');
      const root = document.documentElement;
      function setTheme(t){{
        root.setAttribute('data-theme', t);
        localStorage.setItem('theme', t);
        if(toggle) toggle.textContent = t === 'dark' ? '切换浅色' : '切换深色';
      }}
      const saved = localStorage.getItem('theme');
      if(saved) setTheme(saved);
      else setTheme('light');
      toggle.addEventListener('click', ()=>{{
        const cur = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        setTheme(cur);
      }});
    </script>
  </body>
</html>
"""
    return body


def main():
    items = get_wallstreetcn_news(use_cache=False)
    html = render_html(items)
    os.makedirs('docs', exist_ok=True)
    path = os.path.join('docs', 'index.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Wrote', path)


if __name__ == '__main__':
    main()
