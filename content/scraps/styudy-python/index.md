+++
date = '2025-09-03T07:52:57+09:00'
draft = false
title = 'Python概要とインストールなど'
tags = ["python"]
+++

## はじめに
python用の勉強メモをスクラップとしてまとめます。

## Pythonとは
Pythonは1991年に開発された、シンプルで読みやすい文法が特徴のプログラミング言語です。

- インデント（字下げ）でコードのブロックを表現することが大きな特徴です。
- 文法が比較的シンプルなため、プログラミング初心者でも学習しやすい言語と言われています。
- 近年では、AI開発や機械学習、データ分析などの分野で特に広く活用されています。

## Pythonのインストール方法（Linux/Debian系）

Linux（DebianやUbuntuなど）環境でPython3をインストールする手順です。

```bash
sudo apt update
sudo apt install -y python3
```

**コマンドの解説**
- `sudo apt update`: インストール可能なパッケージのリストを最新の状態に更新します。
- `sudo apt install -y python3`: Python3をインストールします。
    - `-y`オプションは、インストール中の確認メッセージに対して自動的に「Yes」と回答するためのものです。

### インストール後の確認

インストールが正常に完了したかを確認するには、ターミナルで以下のコマンドを実行します。

```bash
python3 --version
```

次のように、インストールされたPythonのバージョンが表示されれば成功です。
```
Python 3.x.x
```
※ `x.x`の部分には、インストールされたバージョン番号が表示されます。

### Pythonの対話モード

Pythonのプログラムを実行するには、主に2つの方法があります。
- **対話モード:** ターミナルで直接コードを一行ずつ入力して実行する方法。
- **スクリプト実行:** `.py`ファイルにコードを記述し、そのファイルを一括で実行する方法。

対話モードは、ターミナルで`python3`コマンドを実行すると開始できます。コードを試したり、簡単な計算をしたりするのに便利です。

```
$ python3
Python 3.x.x (default, ...
Type "help", "copyright", "credits" or "license" for more information.
>>> print("Hello, Python!")
Hello, Python!
>>>
```

対話モードを終了するには、`exit()`と入力するか、`Ctrl + D`を押します。

## 関数 (Functions)

関数は、特定の処理をひとまとめにしたものです。同じ処理を何度も書きたいときに便利です。

```python
def 関数名(引数):
    # ここに処理を書く
    return 戻り
```

- **引数 (argument):** 関数に渡す値。
- **戻り値 (return value):** 関数の処理結果として返される値。

### 例：あいさつする関数

```python
def greet(name):
    """名前を受け取って、あいさつのメッセージを返す関数"""
    message = f"こんにちは、{name}さん！"
    return message

# 関数を呼び出して、戻り値を変数に受け取る
greeting = greet("山田")
print(greeting)
# 出力: こんにちは、山田さん！
```

### 練習問題

2つの数値を受け取り、その積（掛け算の結果）を返す `multiply` という名前の関数を作成してください。
その後、その関数を使って `5` と `8` の積を計算し、結果をコンソールに出力してください。

<details>
<summary>解答例</summary>

```python
# 2つの数値の積を返す関数
def multiply(num1, num2):
    return num1 * num2

# 関数を呼び出して結果を計算
result = multiply(5, 8)
print(f"5と8の積は {result} です。")
# 出力: 5と8の積は 40 です。
```
</details>

## クラス (Classes)

クラスは、オブジェクトの「設計図」です。データ（属性）と処理（メソッド）を一つにまとめることができます。

```python
class クラス名:
    # コンストラクタ (初期化メソッド)
    def __init__(self, 引数):
        self.インスタンス変数 = 引数

    # メソッド
    def メソッド名(self):
        # 処理
        return self.インスタンス変数
```

- **インスタンス:** クラス（設計図）から作られた実体のこと。
- `__init__`: インスタンスが作られるときに最初に呼ばれる特別なメソッド。
- `self`: インスタンス自身を指す特別な変数。

### 例：人物を表すクラス

```python
class Person:
    def __init__(self, name, age):
        self.name = name  # 属性 (インスタンス変数)
        self.age = age

    def introduce(self): # メソッド
        return f"私の名前は{self.name}、{self.age}歳です。"

# Personクラスから「インスタンス」を作成
person1 = Person("鈴木", 25)

# 属性やメソッドを使う
print(person1.name)
print(person1.introduce())
# 出力:
# 鈴木
# 私の名前は鈴木、25歳です。
```

### 練習問題

`Dog` というクラスを作成してください。
- `__init__` メソッドで犬の名前(`name`)を受け取り、インスタンス変数に設定してください。
- `bark` というメソッドを定義し、呼び出されると「(名前)はワン！と鳴いた」という文字列を返すようにしてください。

その後、`Dog` クラスから "ポチ" という名前のインスタンスを作成し、`bark` メソッドを呼び出して結果を出力してください。


<details>
<summary>解答例</summary>

```python
class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        return f"{self.name}はワン！と鳴いた"

# インスタンスを作成
my_dog = Dog("ポチ")

# メソッドを呼び出し
message = my_dog.bark()
print(message)
# 出力: ポチはワン！と鳴いた
```
</details>

## モジュールとインポート (Modules & Import)

モジュールは、関数やクラスをまとめたPythonファイル（`.py`ファイル）のことです。他のファイルから再利用できます。

### モジュールの作成

例えば、`utils.py` という名前で以下のファイルを作成したとします。

```python:utils.py
PI = 3.14159

def circle_area(radius):
    """円の面積を計算する"""
    return PI * (radius ** 2)
```

### モジュールの利用 (インポート)

同じディレクトリにある別のファイル (`main.py`など) から、`utils.py` の中身をインポートして使えます。

```python:main.py
import utils

# utilsモジュールの中の変数や関数を使う
radius = 5
area = utils.circle_area(radius)

print(f"半径{radius}の円の面積は {area} です。")
print(f"円周率は {utils.PI} です。")
```

### 練習問題

`string_utils.py` というモジュールがあると仮定します。このモジュールには、文字列を逆にする `reverse` という関数が定義されています。

```python:string_utils.py
def reverse(text):
    return text[::-1]
```

`from ... import ...` 構文を使って `string_utils` モジュールから `reverse` 関数だけをインポートし、`"hello"` という文字列を逆にして出力してください。

<details>
<summary>解答例</summary>

```python
# string_utils から reverse 関数だけをインポート
from string_utils import reverse

# インポートした関数を直接使える
reversed_text = reverse("hello")
print(reversed_text)
# 出力: olleh
```
</details>

## 参考リンク
- [ゼロからのPython入門講座](https://www.python.jp/train/index.html)
- [Python チュートリアル](https://docs.python.org/ja/3.13/tutorial/index.html)