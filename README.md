# News Feeder

RSSフィードから記事・書籍情報を自動取得し、ブラウザで閲覧できるHTMLファイルを生成するPythonスクリプト群です。

---

## 動作環境

- Python 3.10 以上
- インターネット接続
- [uv](https://github.com/astral-sh/uv)

---

## セットアップ

```bash
uv sync
```

---

## スクリプト一覧

| スクリプト | 用途 | 出力ファイル |
|---|---|---|
| `src/main.py` | テクノロジーニュース全般 | `output/tech_news.html` |
| `src/get_corporation_news.py` | 企業（製造業・IT）ニュース | `output/corporation_news.html` |
| `src/get_books_news.py` | 書籍新刊情報 | `output/books_news.html` |

---

## 実行方法

```bash
# テクノロジーニュース全般
uv run src/main.py

# 企業ニュース（製造業・IT）
uv run src/get_corporation_news.py

# 書籍新刊情報
uv run src/get_books_news.py
```

実行すると、RSSフィードを取得 → HTMLを生成 → ブラウザが自動で開きます（macOS / Windows / Linux 対応）。

---

## ファイル構成

```
news_feeder/
├── src/
│   ├── main.py                  # テクノロジーニュース
│   ├── get_corporation_news.py  # 企業ニュース
│   └── get_books_news.py        # 書籍新刊情報
├── output/
│   ├── tech_news.html
│   ├── corporation_news.html
│   └── books_news.html
├── pyproject.toml
└── uv.lock
```

---

## カスタマイズ

各スクリプトの先頭にある定数を編集するだけで動作を変更できます。

### `src/main.py` — `FEEDS`

テクノロジーニュースの取得先を管理するリストです。

```python
FEEDS: list[dict] = [
    {
        "name":  "GIGAZINE",
        "url":   "https://gigazine.net/news/rss_2.0/",
        "color": "#ff6600",
    },
    # 以下同様に追加
]
```

現在の取得先: GIGAZINE / ITmedia / 日経クロステック / Gizmodo Japan / WIRED Japan / CodeZine / Zenn トレンド / Qiita 人気記事 / はてブ IT

---

### `src/get_corporation_news.py` — `COMPANIES` / `INDUSTRIES`

企業ニュースの取得先を管理するリストです。`industry` に業界を指定するとサイドバーでグループ分けされます。

```python
COMPANIES: list[dict] = [
    {
        "name":     "トヨタ自動車",
        "industry": "製造業",          # INDUSTRIES に含まれる文字列
        "url":      "https://...",
        "color":    "#eb0a1e",
    },
]

INDUSTRIES: list[str] = ["製造業", "IT"]  # 表示順を制御
```

---

### `src/get_books_news.py` — `PUBLISHERS` / `GENRES`

書籍情報の取得先を管理するリストです。`genre` にジャンルを指定するとサイドバーでグループ分けされます。

```python
PUBLISHERS: list[dict] = [
    {
        "name":  "技術評論社",
        "genre": "技術書",             # GENRES に含まれる文字列
        "url":   "https://gihyo.jp/book/feed/rss2",
        "color": "#e0321c",
    },
]

GENRES: list[str] = ["技術書", "社会科学"]  # 表示順を制御
```

---

## トラブルシューティング

**`ModuleNotFoundError: No module named 'feedparser'` が出る**

```bash
uv sync
```

**特定のフィードで「エラー」と表示される**

RSSフィードのURLが変更された可能性があります。ブラウザで直接URLにアクセスして確認してください。エラーが出たフィードはスキップされ、他のフィードの結果は正常に出力されます。

**ブラウザが自動で開かない**

`output/` 以下の HTMLファイルを手動でブラウザにドラッグ＆ドロップするか、以下のコマンドで開いてください。

```powershell
# Windows（PowerShell）
Start-Process output\tech_news.html
```
