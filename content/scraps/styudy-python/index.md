+++
date = '2025-09-03T07:52:57+09:00'
draft = false
title = '勉強メモ：Python'
tags = ["python","勉強メモ"]
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

## 関連ライブラリ・ツール

Python関連のスクラップへリンクを下記にまとめます。

### [Numpy]({{< ref "scraps/study-numpy/" >}})
Pythonで科学技術計算を効率的に行うためのコアライブラリ

### [pyenv]({{< ref "scraps/study-pyenv/" >}})
Pythonのバージョン管理を簡単にするツール

### [venv]({{< ref "scraps/study-venv/" >}})
仮想環境を管理するためのツール

### [virtualenv]({{< ref "scraps/study-virtualenv/" >}})
仮想環境を管理するためのツール（venvと類似している）

### [pipコマンド]({{< ref "scraps/study-pip/" >}})
pipはPythonの公式パッケージ管理ツール

### [requirements.txt]({{< ref "scraps/study-requirements/" >}})
Pythonプロジェクトで使用しているパッケージ名とバージョンを記述したテキストファイル

## 入門レベルのハンズオン

### 文字の連結

<details>
  <summary>名前と挨拶を結合して「Hello, Taro!」と出力してください</summary>

```python
name = "Taro"
greeting = "Hello, " + name + "!"
print(greeting)
```

</details>

### 変数

<details>
  <summary>りんごの数が3個、みかんの数が5個あるとき、合計を変数に代入して表示してください。</summary>

```python
apples = 3
oranges = 5
total = apples + oranges
print(total)

```

</details>

### print() 関数

<details>
  <summary> 「Pythonを学習中」と表示してください。</summary>

```python
print("Pythonを学習中")

```

</details>

### input() 関数

<details>
  <summary>名前を入力すると「こんにちは ○○ さん」と表示するプログラムを作ってください。</summary>

```python
name = input("あなたの名前は？: ")
print("こんにちは " + name + " さん")

```

</details>

### 論理演算子

<details>
  <summary>年齢を入力し、20歳以上かつ30歳未満なら「20代です」と表示、それ以外は「20代ではありません」と表示してください。</summary>

```python
age = int(input("年齢を入力してください: "))
if age >= 20 and age < 30:
    print("20代です")
else:
    print("20代ではありません")
```

</details>


### if文

<details>
  <summary>点数を入力し、60点以上なら「合格」、それ未満なら「不合格」と表示してください。</summary>

```python
score = int(input("点数を入力してください: "))
if score >= 60:
    print("合格")
else:
    print("不合格")
```

</details>

### 配列（リスト）

<details>
  <summary>配列の「10, 20, 30, 40」平均値を計算して表示してください。</summary>

```python
numbers = [10, 20, 30, 40]
average = sum(numbers) / len(numbers)
print("平均:", average)
```

</details>

### 繰り返し（for）

<details>
  <summary>1から5までの数をすべて出力してください。</summary>

```python
for i in range(1, 6):
    print(i)
```

</details>

### 繰り返し（while）

<details>
  <summary>入力された数が0になるまで、その数を表示し続けるプログラムを作ってください。</summary>

```python
num = int(input("数を入力してください(0で終了): "))
while num != 0:
    print("入力された数:", num)
    num = int(input("数を入力してください(0で終了): "))
```

</details>