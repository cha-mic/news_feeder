# Tech RSS Reader

テクノロジー系ニュースを複数のRSSフィードから自動取得し、ブラウザで見られるHTMLファイルを生成するPythonスクリプトです。

---

## 動作環境

- Python 3.7 以上
- インターネット接続

---

## セットアップ

### 1. 依存ライブラリのインストール

```bash
pip install feedparser
```

### 2. スクリプトの配置

`rss_reader.py` を任意のディレクトリに置いてください。出力ファイル（`tech_news.html`）はスクリプトと同じ場所に生成されます。

---

## 実行方法

```bash
python rss_reader.py
```

実行すると以下の処理が順に行われます。

1. 設定済みのRSSフィードから記事を取得
2. `tech_news.html` を生成
3. OS に応じてブラウザが自動で開く（macOS / Windows / Linux に対応）

### 実行例（ターミナル出力）

```
==================================================
  Tech RSS Reader
==================================================

フィードを取得中... (5件のソース)

  取得中: Hacker News ... 10件取得
  取得中: TechCrunch ... 10件取得
  取得中: The Verge ... 10件取得
  取得中: Wired ... 10件取得
  取得中: MIT Technology Review ... 10件取得

HTMLを生成中...

✅ 完了！ 50件の記事を取得しました。
📄 出力ファイル: /path/to/tech_news.html

ブラウザで開いてください。
```

---

## 出力ファイル

| ファイル名 | 説明 |
|---|---|
| `tech_news.html` | 取得した記事一覧。ブラウザで開いて使用する |

HTMLは左サイドバーにフィード別ナビゲーション、右側に記事カードのグリッドを表示するダークテーマのレイアウトです。記事タイトルのリンクをクリックすると、元記事を新しいタブで開きます。

---

## ファイル構成

```
.
├── rss_reader.py   # メインスクリプト
├── README.md       # このファイル
└── tech_news.html  # 実行後に生成される出力ファイル
```

---

## 設定項目

スクリプト上部の定数を編集することで動作をカスタマイズできます。

### `FEEDS` — 取得するRSSフィードの一覧

```python
FEEDS = [
    {
        "name": "Hacker News",            # サイドバーやヘッダーに表示される名前
        "url": "https://news.ycombinator.com/rss",  # RSSフィードのURL
        "color": "#ff6600",               # アクセントカラー（CSSカラー値）
    },
    # ... 以下同様に追加
]
```

フィードを追加する場合は、このリストに辞書を追記するだけです。

**日本語テクノロジー系フィードの追加例：**

```python
{"name": "GIGAZINE",          "url": "https://gigazine.net/news/rss_2.0/",                                      "color": "#ff6600"},
{"name": "ITmedia",           "url": "https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml",                       "color": "#c00"},
{"name": "Zenn トレンド",      "url": "https://zenn.dev/feed",                                                   "color": "#3ea8ff"},
{"name": "Qiita 人気記事",     "url": "https://qiita.com/popular-items/feed.atom",                               "color": "#55c500"},
{"name": "はてブ IT",         "url": "https://b.hatena.ne.jp/hotentry/it.rss",                                  "color": "#00a4de"},
{"name": "Apple Japan",       "url": "https://www.apple.com/jp/newsroom/rss-feed.rss",                          "color": "#555"},
{"name": "トヨタ",             "url": "https://global.toyota/export/jp/allnews_rss.xml",                         "color": "#eb0a1e"},
{"name": "パナソニック",       "url": "https://news.panasonic.com/jp/rss/category/products-solutions/iprojects.xml", "color": "#0050a0"},
{"name": "シャープ",           "url": "https://corporate.jp.sharp/news/rss.xml",                                 "color": "#e60012"},
```

### `MAX_ARTICLES_PER_FEED` — 1フィードあたりの最大取得記事数

```python
MAX_ARTICLES_PER_FEED = 10  # デフォルト: 10件
```

### `OUTPUT_FILE` — 出力HTMLファイル名

```python
OUTPUT_FILE = "tech_news.html"  # デフォルト: tech_news.html
```

---

## 関数リファレンス

### `fetch_feed(feed_info: dict) -> list[dict]`

1件のRSSフィードから記事を取得して返す関数です。

**引数**

| パラメータ | 型 | 説明 |
|---|---|---|
| `feed_info` | `dict` | `FEEDS` リストの1要素。`name`, `url`, `color` キーを持つ |

**返り値**

記事情報の辞書のリスト。各辞書は以下のキーを持ちます。

| キー | 型 | 説明 |
|---|---|---|
| `title` | `str` | 記事タイトル（HTMLエスケープ済み） |
| `link` | `str` | 記事URL（HTMLエスケープ済み） |
| `summary` | `str` | 要約テキスト（HTMLタグ除去・200文字以内に整形済み） |
| `published` | `str` | 公開日時（`YYYY-MM-DD HH:MM` 形式、不明な場合は `"日時不明"`） |

取得に失敗した場合はエラーをターミナルに出力し、空リスト `[]` を返します。

---

### `generate_html(feed_data: list[dict]) -> str`

取得済みの記事データをもとにHTMLページ全体を生成して返す関数です。

**引数**

| パラメータ | 型 | 説明 |
|---|---|---|
| `feed_data` | `list[dict]` | `fetch_feed()` の結果に `articles` キーを追加した辞書のリスト |

**返り値**

HTMLページ全体の文字列。CSS・フォント読み込みを含む完全な1ファイル構成です。

**生成するHTML要素**

- 左サイドバー：フィード名・記事件数・更新日時
- メインエリア：フィードごとのセクション、記事カードのグリッド

---

### `main()`

スクリプトのエントリポイントです。以下の処理を順に実行します。

1. `feedparser` がインストールされているか確認（未インストールの場合はエラーメッセージを表示して終了）
2. `FEEDS` の各フィードに対して `fetch_feed()` を呼び出し
3. `generate_html()` でHTMLを生成
4. `OUTPUT_FILE` に書き出し
5. OSに応じたコマンドでブラウザを自動起動

---

## 処理フロー

```
main()
  │
  ├─ feedparser インストール確認
  │
  ├─ FEEDS を順に処理
  │    └─ fetch_feed(feed_info)
  │         ├─ feedparser.parse() でRSSを取得
  │         ├─ 各記事からタイトル・URL・要約・日時を抽出
  │         └─ HTMLエスケープ・整形して返す
  │
  ├─ generate_html(feed_data)
  │    ├─ サイドバーのナビゲーションリンクを生成
  │    ├─ 各フィードのセクション・カードを生成
  │    └─ HTML全体を文字列として返す
  │
  ├─ tech_news.html に書き出し
  │
  └─ ブラウザで自動オープン
```

---

## トラブルシューティング

**`ModuleNotFoundError: No module named 'feedparser'` が出る**

```bash
pip install feedparser
```

**特定のフィードで「エラー」と表示される**

ネットワーク障害やRSSフィードのURL変更が原因の場合があります。ブラウザで直接URLにアクセスして確認してください。エラーが出たフィードはスキップされ、他のフィードの結果は正常に出力されます。

**ブラウザが自動で開かない**

`tech_news.html` を手動でブラウザにドラッグ＆ドロップするか、以下のように開いてください。

```bash
# macOS
open tech_news.html

# Windows（PowerShell）
Start-Process tech_news.html

# Linux
xdg-open tech_news.html
```

**文字化けする**

テキストエディタや一部のビューアで開いた場合に文字化けすることがありますが、ブラウザで開く分には問題ありません。HTMLファイルはUTF-8で保存されています。