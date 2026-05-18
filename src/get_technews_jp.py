#!/usr/bin/env python3
"""
Tech RSS Reader
テクノロジー系ニュースを取得して、ブラウザで見られるHTMLファイルを生成します。

使い方:
  python rss_reader.py

必要なライブラリのインストール:
  pip install feedparser requests
"""

import datetime
import html
import os
import platform
import re
import subprocess
import sys

import feedparser

# ============================================================
# 取得するRSSフィードの設定（自由に追加・変更できます）
# ============================================================

FEEDS: list[dict] = [
    {
        "name": "GIGAZINE",
        "url": "https://gigazine.net/news/rss_2.0/",
        "color": "#ff6600"
    },
    {
        "name": "ITmedia",
        "url": "https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml",
        "color": "#c00"
    },
    {
        "name": "日経クロステック",
        "url": "https://xtech.nikkei.com/rss/index.rdf",
        "color": "#003580"
    },
    {
        "name": "Gizmodo Japan",
        "url": "https://www.gizmodo.jp/index.xml",
        "color": "#e5185b"
    },
    {
        "name": "WIRED Japan",
        "url": "https://wired.jp/feed/",
        "color": "#111"
    },
    {
        "name": "Code Zine",
        "url": "https://codezine.jp/rss/new/20/index.xml",
        "color": "#d3002d"
    },
    {
        "name": "Zenn トレンド",
        "url": "https://zenn.dev/feed",
        "color": "#3ea8ff"
    },
    {
        "name": "Qiita 人気記事",
        "url": "https://qiita.com/popular-items/feed.atom",
        "color": "#55c500"
    },
    {
        "name": "はてブ IT",
        "url": "https://b.hatena.ne.jp/hotentry/it.rss",
        "color": "#00a4de"
    },
]

MAX_ARTICLES_PER_FEED: int = 10

OUTPUT_FILE: str = "..\\output\\tech_news.html"


# ============================================================
# RSSフィード取得
# ============================================================
def fetch_feed(feed_info: dict) -> list[dict]:
    """RSSフィードを取得して記事リストを返す

    指定されたフィード情報からRSSを取得し、記事データのリストを返す。
    取得に失敗した場合は空リストを返す。

    Args:
        feed_info (dict): フィード情報（name, url, colorを含む辞書）

    Returns:
        list[dict]: 記事データのリスト（title, link, summary, publishedを含む辞書）
    """
    print(f"  取得中: {feed_info['name']} ...", end=" ", flush=True)
    try:
        parsed = feedparser.parse(feed_info["url"])
        articles: list[dict] = []
        for entry in parsed.entries[:MAX_ARTICLES_PER_FEED]:
            title:   str = entry.get("title", "（タイトルなし）")
            link:    str = entry.get("link", "#")
            summary: str = entry.get("summary", entry.get("description", ""))
            summary = re.sub(r"<[^>]+>", "", summary)
            summary = summary[:200] + "..." if len(summary) > 200 else summary

            pub: tuple | None = entry.get("published_parsed") or entry.get("updated_parsed")
            pub_str: str
            if pub:
                pub_dt: datetime.datetime = datetime.datetime(*pub[:6])
                pub_str = pub_dt.strftime("%Y-%m-%d %H:%M")
            else:
                pub_str = "日時不明"

            articles.append({
                "title": html.escape(title),
                "link": html.escape(link),
                "summary": html.escape(summary),
                "published": pub_str,
            })
        print(f"{len(articles)}件取得")
        return articles
    except Exception as e:
        print(f"エラー: {e}")
        return []


# ============================================================
# HTML生成
# ============================================================
def generate_html(feed_data: list[dict]) -> str:
    """フィードデータからHTMLコンテンツを生成する

    取得したフィードデータを元に、サイドバーとカードグリッドを持つHTMLを生成する。

    Args:
        feed_data (list[dict]): フィードデータのリスト（name, color, articlesを含む辞書）

    Returns:
        str: 生成されたHTMLコンテンツ
    """
    now:   str = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M")
    total: int = sum(len(f["articles"]) for f in feed_data)

    nav_links: str = ""
    for f in feed_data:
        anchor: str = f["name"].replace(" ", "_")
        count:  int = len(f["articles"])
        nav_links += f"""
        <a href="#{anchor}" class="nav-link" style="--accent: {f['color']}">
          <span class="nav-dot" style="background:{f['color']}"></span>
          {f['name']}
          <span class="nav-count">{count}</span>
        </a>"""

    feed_sections: str = ""
    for f in feed_data:
        anchor: str = f["name"].replace(" ", "_")
        if not f["articles"]:
            feed_sections += f"""
        <section class="feed-section" id="{anchor}">
          <div class="feed-header" style="--accent: {f['color']}">
            <div class="feed-dot" style="background:{f['color']}"></div>
            <h2>{f['name']}</h2>
            <span class="feed-badge">0件</span>
          </div>
          <p class="empty-msg">記事を取得できませんでした。</p>
        </section>"""
            continue

        cards: str = ""
        for i, article in enumerate(f["articles"]):
            cards += f"""
          <article class="card" style="animation-delay:{i * 0.04}s">
            <div class="card-meta">{article['published']}</div>
            <h3 class="card-title">
              <a href="{article['link']}" target="_blank" rel="noopener">{article['title']}</a>
            </h3>
            {"<p class='card-summary'>" + article['summary'] + "</p>" if article['summary'] else ""}
          </article>"""

        feed_sections += f"""
        <section class="feed-section" id="{anchor}">
          <div class="feed-header" style="--accent: {f['color']}">
            <div class="feed-dot" style="background:{f['color']}"></div>
            <h2>{f['name']}</h2>
            <span class="feed-badge">{len(f['articles'])}件</span>
          </div>
          <div class="cards-grid">
            {cards}
          </div>
        </section>"""

    html_content: str = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tech News — {now}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg: #0c0c0f;
      --bg2: #111116;
      --bg3: #17171f;
      --border: rgba(255,255,255,0.07);
      --text: #e8e8f0;
      --muted: #6b6b80;
      --sidebar-w: 220px;
    }}

    html {{ scroll-behavior: smooth; }}

    body {{
      font-family: 'DM Sans', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
    }}

    /* ---- Sidebar ---- */
    .sidebar {{
      width: var(--sidebar-w);
      min-height: 100vh;
      background: var(--bg2);
      border-right: 1px solid var(--border);
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
      padding: 2rem 0;
      flex-shrink: 0;
    }}

    .sidebar-logo {{
      font-family: 'Syne', sans-serif;
      font-weight: 800;
      font-size: 1.1rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 0 1.4rem 2rem;
      color: var(--text);
    }}
    .sidebar-logo span {{ display: block; font-size: 0.65rem; font-weight: 400; color: var(--muted); letter-spacing: 0.15em; margin-top: 2px; }}

    .nav-section-label {{
      font-size: 0.65rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--muted);
      padding: 0 1.4rem 0.6rem;
    }}

    .nav-link {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      padding: 0.55rem 1.4rem;
      font-size: 0.82rem;
      color: var(--muted);
      text-decoration: none;
      transition: color 0.15s, background 0.15s;
      position: relative;
    }}
    .nav-link:hover {{
      color: var(--text);
      background: rgba(255,255,255,0.04);
    }}
    .nav-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
    .nav-count {{ margin-left: auto; font-size: 0.7rem; background: rgba(255,255,255,0.08); border-radius: 10px; padding: 1px 7px; }}

    .sidebar-footer {{
      padding: 2rem 1.4rem 0;
      font-size: 0.7rem;
      color: var(--muted);
      line-height: 1.6;
    }}

    /* ---- Main ---- */
    .main {{
      flex: 1;
      min-width: 0;
      padding: 2.5rem 3rem;
    }}

    .page-header {{
      display: flex;
      align-items: baseline;
      gap: 1.5rem;
      margin-bottom: 3rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 1.5rem;
    }}
    .page-title {{
      font-family: 'Syne', sans-serif;
      font-weight: 800;
      font-size: 1.8rem;
      letter-spacing: -0.02em;
    }}
    .page-meta {{ font-size: 0.8rem; color: var(--muted); }}
    .page-total {{ margin-left: auto; font-size: 0.8rem; color: var(--muted); }}

    /* ---- Feed section ---- */
    .feed-section {{ margin-bottom: 3.5rem; }}

    .feed-header {{
      display: flex;
      align-items: center;
      gap: 0.8rem;
      margin-bottom: 1.2rem;
    }}
    .feed-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
    .feed-header h2 {{
      font-family: 'Syne', sans-serif;
      font-weight: 700;
      font-size: 1rem;
      letter-spacing: 0.03em;
    }}
    .feed-badge {{
      font-size: 0.7rem;
      background: rgba(255,255,255,0.08);
      border-radius: 10px;
      padding: 2px 8px;
      color: var(--muted);
    }}

    /* ---- Cards ---- */
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1px;
      background: var(--border);
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
    }}

    .card {{
      background: var(--bg3);
      padding: 1.2rem 1.4rem;
      transition: background 0.15s;
      animation: fadeUp 0.4s ease both;
    }}
    .card:hover {{ background: #1e1e28; }}

    @keyframes fadeUp {{
      from {{ opacity: 0; transform: translateY(8px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}

    .card-meta {{ font-size: 0.68rem; color: var(--muted); margin-bottom: 0.5rem; }}

    .card-title {{
      font-family: 'Syne', sans-serif;
      font-weight: 600;
      font-size: 0.9rem;
      line-height: 1.45;
      margin-bottom: 0.5rem;
    }}
    .card-title a {{
      color: var(--text);
      text-decoration: none;
    }}
    .card-title a:hover {{ text-decoration: underline; text-underline-offset: 3px; }}

    .card-summary {{
      font-size: 0.78rem;
      color: var(--muted);
      line-height: 1.6;
    }}

    .empty-msg {{ color: var(--muted); font-size: 0.85rem; padding: 1rem 0; }}

    /* scrollbar */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.12); border-radius: 3px; }}

    @media (max-width: 700px) {{
      .sidebar {{ display: none; }}
      .main {{ padding: 1.5rem; }}
    }}
  </style>
</head>
<body>

  <nav class="sidebar">
    <div class="sidebar-logo">Tech News<span>RSS Reader</span></div>
    <div class="nav-section-label">フィード</div>
    {nav_links}
    <div class="sidebar-footer">
      更新: {now}<br>
      合計 {total} 件の記事
    </div>
  </nav>

  <main class="main">
    <div class="page-header">
      <div>
        <div class="page-title">Tech News</div>
        <div class="page-meta">取得日時: {now}</div>
      </div>
      <div class="page-total">合計 {total} 件</div>
    </div>

    {feed_sections}
  </main>

</body>
</html>"""
    return html_content


# ============================================================
# メイン処理
# ============================================================
def main() -> None:
    """メイン処理

    RSSフィードを取得してHTMLファイルを生成し、ブラウザで開く。

    Raises:
        SystemExit: feedparserがインストールされていない場合
    """
    print("=" * 50)
    print("  Tech RSS Reader")
    print("=" * 50)

    try:
        import feedparser  # noqa: F401
    except ImportError:
        print("\n[エラー] feedparser がインストールされていません。")
        print("以下のコマンドを実行してインストールしてください:\n")
        print("  pip install feedparser\n")
        sys.exit(1)

    print(f"\nフィードを取得中... ({len(FEEDS)}件のソース)\n")

    feed_data: list[dict] = []
    for feed_info in FEEDS:
        articles: list[dict] = fetch_feed(feed_info)
        feed_data.append({
            **feed_info,
            "articles": articles,
        })

    print(f"\nHTMLを生成中...")
    html_content: str = generate_html(feed_data)

    output_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    total: int = sum(len(f["articles"]) for f in feed_data)
    print(f"\n完了！ {total}件の記事を取得しました。")
    print(f"出力ファイル: {output_path}")
    print(f"\nブラウザで開いてください。")

    try:
        if platform.system() == "Darwin":
            subprocess.run(["open", output_path])
        elif platform.system() == "Windows":
            os.startfile(output_path)
        else:
            subprocess.run(["xdg-open", output_path])
    except Exception:
        pass


if __name__ == "__main__":
    main()
