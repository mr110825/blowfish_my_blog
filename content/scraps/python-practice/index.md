+++
date = '2025-09-07T14:25:43+09:00'
draft = false
title = 'Python入門ハンズオン'
tags = ["python"]
+++

## はじめに

Pythonは、初心者にも学びやすく、かつ実用性の高いプログラミング言語です。データ分析、Web開発、機械学習など幅広い分野で活用されており、プログラミングの基礎を身につける最初の言語として最適です。

以下に、Python基本文法の実践的な練習問題をハンズオン形式で説明します。

### 文字の連結

`+` 演算子を使用して、文字列同士を連結することができます。

<details>
  <summary>名前と挨拶を結合して「Hello, Taro!」と出力してください</summary>

```python
name = "Taro"
greeting = "Hello, " + name + "!"
print(greeting)
```

</details>

### 変数

変数に値を代入し、その変数を使って計算を行うことができます。

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

`print()` 関数は、括弧内の値や文字列を画面に出力します。

<details>
  <summary> 「Pythonを学習中」と表示してください。</summary>

```python
print("Pythonを学習中")

```

</details>

### input() 関数

`input()` 関数は、ユーザーからのキーボード入力を受け取り、その値を返します。

<details>
  <summary>名前を入力すると「こんにちは ○○ さん」と表示するプログラムを作ってください。</summary>

```python
name = input("あなたの名前は？: ")
print("こんにちは " + name + " さん")

```

</details>

### 論理演算子

`and` や `or` などの論理演算子を使って、複数の条件を組み合わせることができます。

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

`if` 文を使うと、条件が真の場合に特定の処理を実行できます。`else` を使うと、条件が偽の場合の処理も記述できます。

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

リスト（配列）は、複数の値をまとめて格納できるデータ型です。`sum()` で合計、`len()` で要素数を取得できます。

<details>
  <summary>配列の「10, 20, 30, 40」平均値を計算して表示してください。</summary>

```python
numbers = [10, 20, 30, 40]
average = sum(numbers) / len(numbers)
print("平均:", average)
```

</details>

### 繰り返し（for）

`for` ループは、指定した回数だけ処理を繰り返します。`range()` 関数と組み合わせて使うことが多いです。

<details>
  <summary>1から5までの数をすべて出力してください。</summary>

```python
for i in range(1, 6):
    print(i)
```

</details>

### 繰り返し（while）

`while` ループは、指定した条件が真である間、処理を繰り返します。

<details>
  <summary>入力された数が0になるまで、その数を表示し続けるプログラムを作ってください。</summary>

```python
num = int(input("数を入力してください(0で終了): "))
while num != 0:
    print("入力された数:", num)
    num = int(input("数を入力してください(0で終了): "))
```

</details>