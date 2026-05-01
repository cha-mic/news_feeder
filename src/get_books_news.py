#!/usr/bin/env python3

import datetime
import html
import os
import platform
import re
import subprocess
import sys

import feedparser

# ============================================================
# 取得する出版社の設定
# genre: 書籍のジャンル（サイドバーのグループ分けに使用）
# url: 出版社の新刊RSSフィードURL
# ============================================================
PUBLISHERS: list[dict] = [
    # --- 技術書 ---
    {
        "name":  "技術評論社",
        "genre": "技術書",
        "url":   "https://gihyo.jp/book/feed/rss2",
        "color": "#e0321c",
    },
    {
        "name":  "O'Reilly Japan",
        "genre": "技術書",
        "url":   "https://www.oreilly.co.jp/catalog/soon.xml",
        "color":    "#0041a0",
    }
]

GENRES: list[str] = ["技術書", "社会科学"]

MAX_BOOKS_PER_PUBLISHER: int = 10

OUTPUT_FILE: str = "..\\output\\books_news.html"


def fetch_book_feed(publisher: dict) -> list[dict]:
    """出版社のRSSフィードから新刊情報を取得する

    Args:
        publisher (dict): 出版社情報（name, genre, url, colorを含む辞書）

    Returns:
        list[dict]: 書籍データのリスト（title, link, summary, publishedを含む辞書）
    """
    print(f"  取得中: {publisher['name']} ...", end=" ", flush=True)
    try:
        parsed = feedparser.parse(publisher["url"])
        books: list[dict] = []
        for entry in parsed.entries[:MAX_BOOKS_PER_PUBLISHER]:
            title:   str = entry.get("title", "（タイトルなし）")
            link:    str = entry.get("link", "#")
            summary: str = entry.get("summary", entry.get("description", ""))
            summary = re.sub(r"<[^>]+>", "", summary)
            summary = summary[:200] + "..." if len(summary) > 200 else summary

            pub: tuple | None = entry.get("published_parsed") or entry.get("updated_parsed")
            pub_str: str
            if pub:
                pub_dt: datetime.datetime = datetime.datetime(*pub[:6])
                pub_str = pub_dt.strftime("%Y-%m-%d")
            else:
                pub_str = "日時不明"

            books.append({
                "title":     html.escape(title),
                "link":      html.escape(link),
                "summary":   html.escape(summary),
                "published": pub_str,
            })
        print(f"{len(books)}件取得")
        return books
    except Exception as e:
        print(f"エラー: {e}")
        return []


def generate_html(feed_data: list[dict]) -> str:
    """ジャンル別に書籍新刊情報をまとめたHTMLを生成する

    Args:
        feed_data (list[dict]): 出版社ごとの書籍データ（name, genre, color, booksを含む辞書）

    Returns:
        str: 生成されたHTMLコンテンツ
    """
    now:   str = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M")
    total: int = sum(len(p["books"]) for p in feed_data)

    nav_links: str = ""
    for genre in GENRES:
        nav_links += f'<div class="nav-section-label">{genre}</div>'
        for p in feed_data:
            if p["genre"] != genre:
                continue
            anchor: str = p["name"].replace(" ", "_")
            count:  int = len(p["books"])
            nav_links += f"""
        <a href="#{anchor}" class="nav-link" style="--accent: {p['color']}">
          <span class="nav-dot" style="background:{p['color']}"></span>
          {p['name']}
          <span class="nav-count">{count}</span>
        </a>"""

    genre_sections: str = ""
    for genre in GENRES:
        publishers_in_genre: list[dict] = [
            p for p in feed_data if p["genre"] == genre
        ]
        publisher_sections: str = ""
        for p in publishers_in_genre:
            anchor: str = p["name"].replace(" ", "_")
            if not p["books"]:
                publisher_sections += f"""
        <section class="feed-section" id="{anchor}">
          <div class="feed-header" style="--accent: {p['color']}">
            <div class="feed-dot" style="background:{p['color']}"></div>
            <h3>{p['name']}</h3>
            <span class="feed-badge">0件</span>
          </div>
          <p class="empty-msg">書籍情報を取得できませんでした。</p>
        </section>"""
                continue

            cards: str = ""
            for i, book in enumerate(p["books"]):
                cards += f"""
          <article class="card" style="animation-delay:{i * 0.04}s">
            <div class="card-meta">{book['published']}</div>
            <h4 class="card-title">
              <a href="{book['link']}" target="_blank" rel="noopener">{book['title']}</a>
            </h4>
            {"<p class='card-summary'>" + book['summary'] + "</p>" if book['summary'] else ""}
          </article>"""

            publisher_sections += f"""
        <section class="feed-section" id="{anchor}">
          <div class="feed-header" style="--accent: {p['color']}">
            <div class="feed-dot" style="background:{p['color']}"></div>
            <h3>{p['name']}</h3>
            <span class="feed-badge">{len(p['books'])}件</span>
          </div>
          <div class="cards-grid">{cards}</div>
        </section>"""

        genre_sections += f"""
      <div class="genre-group">
        <h2 class="genre-heading">{genre}</h2>
        {publisher_sections}
      </div>"""

    html_content: str = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>書籍新刊情報 — {now}</title>
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
      padding: 0.8rem 1.4rem 0.4rem;
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

    .genre-group {{ margin-bottom: 4rem; }}

    .genre-heading {{
      font-family: 'Syne', sans-serif;
      font-weight: 800;
      font-size: 1.1rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--muted);
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.6rem;
      margin-bottom: 2rem;
    }}

    .feed-section {{ margin-bottom: 2.5rem; }}

    .feed-header {{
      display: flex;
      align-items: center;
      gap: 0.8rem;
      margin-bottom: 1.2rem;
    }}
    .feed-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
    .feed-header h3 {{
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

    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
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
    <div class="sidebar-logo">New Books<span>書籍新刊情報</span></div>
    {nav_links}
    <div class="sidebar-footer">
      更新: {now}<br>
      合計 {total} 件
    </div>
  </nav>

  <main class="main">
    <div class="page-header">
      <div>
        <div class="page-title">書籍新刊情報</div>
        <div class="page-meta">取得日時: {now}</div>
      </div>
      <div class="page-total">合計 {total} 件</div>
    </div>
    {genre_sections}
  </main>

</body>
</html>"""
    return html_content


def main() -> None:
    """メイン処理

    出版社のRSSフィードから新刊情報を取得してHTMLファイルを生成し、ブラウザで開く。

    Raises:
        SystemExit: feedparserがインストールされていない場合
    """
    print("=" * 50)
    print("  Books News Reader")
    print("=" * 50)

    try:
        import feedparser  # noqa: F401
    except ImportError:
        print("\n[エラー] feedparser がインストールされていません。")
        print("以下のコマンドを実行してインストールしてください:\n")
        print("  pip install feedparser\n")
        sys.exit(1)

    print(f"\n新刊情報を取得中... ({len(PUBLISHERS)}社)\n")

    feed_data: list[dict] = []
    for publisher in PUBLISHERS:
        books: list[dict] = fetch_book_feed(publisher)
        feed_data.append({
            **publisher,
            "books": books,
        })

    print("\nHTMLを生成中...")
    html_content: str = generate_html(feed_data)

    output_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    total: int = sum(len(p["books"]) for p in feed_data)
    print(f"\n✅ 完了！ {total}件の書籍情報を取得しました。")
    print(f"📄 出力ファイル: {output_path}")
    print("\nブラウザで開いてください。")

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
