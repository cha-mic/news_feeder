# コーディング規約

## 命名規則

### 変数・関数名は `snake_case` を使う

#### 例
```python
user_name = "山田"

def fetch_article_list():
    pass
```

### クラス名は `PascalCase` を使う

#### 例
```python
class FeedParser:
    pass
```

### クラスのメンバ変数は末尾にアンダーバーをつける

```python
class FeedParser:
    title_: str = "None"
```

### 定数は `UPPER_SNAKE_CASE` を使う

#### 例
```python
MAX_ARTICLES_PER_FEED = 10
OUTPUT_FILE = "output/tech_news.html"
```

### 意味のわかる名前をつける（`tmp`, `data`, `x` などは避ける）

#### 例
```python
# Bad
tmp = fetch_feed(url)

# Good
articles = fetch_feed(url)
```

## 関数

### 1つの関数は1つの責務だけを持つ

#### 例
```python
# Bad: 取得と保存を同時にやっている
def fetch_and_save(url):
    data = feedparser.parse(url)
    with open("out.html", "w") as f:
        f.write(generate_html(data))

# Good: 分離する
def fetch_feed(url): ...
def save_html(content, path): ...
```

### 戻り値の型アノテーションを必ず付ける

#### 例
```python
def fetch_feed(feed_info: dict) -> list[dict]:
    ...

def generate_html(feed_data: list[dict]) -> str:
    ...
```

## 変数

### Pythonで書かれたプログラムに対しては，変数に型ヒントをつける

#### 例
```python
name: str        = "山田"
age: int         = 30
height: float    = 1.75
is_student: bool = False
phone_number: str  # 代入せずに型ヒントだけ定義することもできます
```

## コメント

### コードを読めばわかることはコメントしない

#### 例
```python
# Bad
i = i + 1  # iに1を足す

# Good（コメント不要）
i = i + 1
```

### 「なぜそうしているか」が自明でない場合だけコメントを書く

#### 例
```python
# feedparser はタイムゾーンを UTC で返すため、表示前にローカル時刻へ変換する
pub_dt = datetime.utcfromtimestamp(time.mktime(pub)).astimezone()
```

### 関数ごとに以下の例に倣ったdocstringをつける

#### 例
```python
def func(arg1, arg2):
    """概要

    詳細説明

    Args:
        引数(arg1)の名前 (引数(arg1)の型): 引数(arg1)の説明
        引数(arg2)の名前 (:obj:`引数(arg2)の型`, optional): 引数(arg2)の説明

    Returns:
        戻り値の型: 戻り値の説明

    Raises:
        例外の名前: 例外の説明

    Yields:
        戻り値の型: 戻り値についての説明

    Examples:

        関数の使い方

        >>> func(5, 6)
        11

    Note:
        注意事項や注釈など

    """
   value = arg1 + arg2
   return value
```

## インポート

### 標準ライブラリ → サードパーティ → 自作モジュールの順で並べる

#### 例
```python
import datetime
import os

import feedparser

from myapp.utils import format_date
```

### 各グループの間に空行を1行入れる

#### 例
```python
import os        # 標準ライブラリ
import sys

import feedparser  # サードパーティ（1行空ける）
```

### ワイルドカードインポート（`from x import *`）は禁止

#### 例
```python
# Bad
from feedparser import *

# Good
from feedparser import parse
```

## その他

### マジックナンバーは定数として定義する

#### 例
```python
# Bad
for entry in parsed.entries[:10]:

# Good
MAX_ARTICLES_PER_FEED = 10
for entry in parsed.entries[:MAX_ARTICLES_PER_FEED]:
```

### ネストは3段階までにする

#### 例
```python
# Bad（4段ネスト）
for feed in feeds:
    for entry in feed.entries:
        if entry.title:
            if entry.link:
                process(entry)

# Good（早期リターンで浅くする）
for feed in feeds:
    for entry in feed.entries:
        if not entry.title or not entry.link:
            continue
        process(entry)
```

### 1行は120文字以内にする

#### 例
```python
# Bad
result = some_very_long_function_name(argument_one, argument_two, argument_three, argument_four, argument_five)

# Good
result = some_very_long_function_name(
    argument_one, argument_two, argument_three,
    argument_four, argument_five,
)
```

### 連続する行については，等号(=)の縦の位置を揃える

#### 例
```python
name:    str   = "山田"
age:     int   = 30
height:  float = 1.75
```

### 中括弧前で改行する

#### 例
```python
    # bad
    data: dict = {"key": value}

    # good
    data: dict = {
        "key": value
    }

```