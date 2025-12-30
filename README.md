# daily_news — WallStreetCN fetcher

This repository fetches the latest news from WallStreetCN and generates a simple HTML page at `docs/index.html`.

How it works
- `get_wallstreat_news.py` provides `get_wallstreetcn_news()` to fetch items from the public content API, with HTML fallback.
- `scripts/generate_news_page.py` generates `docs/index.html` using that function.
- A GitHub Action (`.github/workflows/fetch_news.yml`) runs on a schedule and updates `docs/index.html` in the repo.

Publishing
- Enable GitHub Pages for this repository and set the source to the `docs/` folder (e.g., branch `main` / folder `docs`). The Action will update `docs/index.html` and the page will be served automatically.

Customization
- Edit `.github/workflows/fetch_news.yml` to change the schedule or other behavior.

Local testing
- Install dependencies: `pip install -r requirements.txt`
- Run: `python scripts/generate_news_page.py` (this writes `docs/index.html`)
