---
name: get-news
description: 指定したジャンルのニュースを取得して表示する
disable-model-invocation: true
---

# 対話のステップ
## STEP1

対話形式で，ユーザーが下のいずれのジャンルのニュースを取得したいのか確認する

1. 日本語ニュース記事
2. 英語ニュース記事
3. 技術系書籍情報
4. 企業のプレスリリース
5. テックブログ

## STEP2

一度，選んだジャンルの確認をとる

## STEP3

ジャンルに応じてスクリプト実行

{
  "日本語ニュース記事"   : uv run ./src/get_technews_jp.py,
  "英語ニュース記事"     : uv run ./src/get_technews_en.py,
  "技術系書籍情報"       : uv run ./src/get_books_news.py,
  "企業のプレスリリース" : uv run ./src/get_corporation_news.py,
  "テックブログ"         : uv run ./src/get_techblog.py 
}


## STEP4

/clear を実行

# 使い方

/get-news で実行
