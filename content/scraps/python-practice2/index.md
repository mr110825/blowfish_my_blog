+++
date = '2025-09-07T15:38:49+09:00'
draft = false
title = 'Python基礎レベルハンズオン'
tags = ["python"]
+++
## はじめに

Pythonの基本文法を習得した後は、より実践的なプログラミング技術を身につけることが重要です。アルゴリズムの理解、複雑な条件分岐、ループの応用など、実際の開発現場で使われる技術を段階的に学習できます。

以下に、Python基礎レベルの実践的な練習問題をハンズオン形式で説明します。

## 練習問題

### 九九の段を出力
1×1 ～ 9×9 の九九の段を出力するプログラムを書いてください。  
各行の末尾に「○の段です」と表示しましょう。

```bash
1 2 3 4 5 6 7 8 9 「1」の段です
2 4 6 8 10 12 14 16 18 「2」の段です
...
9 18 27 36 45 54 63 72 81 「9」の段です
```

`for` ループを2つ使う（二重ループ）ことで、九九のような表を作成できます。内側のループが列、外側のループが行を処理します。

<details>
  <summary>回答</summary>

```python
for i in range(1, 10):
    for j in range(1, 10):
        print(i * j, end=" ")
    print("「{}」の段です".format(i))
```

</details>

## 3の倍数ならfoo、そうでなければnoo
ユーザーから1つ数字を入力し、それが「3の倍数」であれば `foo`、そうでなければ `noo` と出力してください。

```bash
数字を入力してください: 9
foo
```

`%` 演算子は、割り算の余りを求めます。`num % 3 == 0` のように、3で割った余りが0になるかどうかで、3の倍数を判定できます。

<details>
  <summary>回答</summary>

```python
num = int(input("数字を入力してください: "))

if num % 3 == 0:
    print("foo")
else:
    print("noo")
```

</details>

## 2つの数字の和を計算しよう

ユーザーから2つの数字を受け取り、その和を出力してください。

```bash
1つ目の数字: 3
2つ目の数字: 5
合計: 8
```

`input()` で受け取った文字列を `int()` で整数に変換してから、足し算を行います。

<details>
  <summary>回答</summary>

```python
x = int(input("1つ目の数字: "))
y = int(input("2つ目の数字: "))

print("合計:", x + y)
```

</details>

## 値を入れ替えてみよう
ユーザーから数字を2つ入力し、入れ替えて表示しましょう。  
出力の書式は `print("i =", i, ", j =", j)` を必ず使ってください。

```bash
i = 1 , j = 2
i = 2 , j = 1
```

Pythonでは `i, j = j, i` のように、1行で複数の変数の値を簡単に入れ替えることができます。

<details>
  <summary>回答</summary>

```python
i = input("iを入力: ")
j = input("jを入力: ")

print("i =", i, ", j =", j)
i, j = j, i
print("i =", i, ", j =", j)
```
</details>

## 三角形を描いてみよう
ユーザーから高さを入力し、その高さの直角三角形を「*」で描いてください。

```
# 出力例（高さ=5）
*
**
***
****
*****
```

文字列に `*` 演算子を使うと、その文字列を指定した回数だけ繰り返します。`"*" * 5` は `*****` となります。

<details>
  <summary>回答</summary>

```python
h = int(input("高さを入力してください: "))

for i in range(1, h+1):
    print("*" * i)
```
</details>

## 素数の和を求めよう
20000 以下の素数をすべて足し算してください。
```
21171191
```

素数とは、1とその数自身以外に約数を持たない自然数のことです。ある数 `i` が素数かどうかは、2から `i` の平方根までの数で割り切れるかどうかで判定できます。

<details>
  <summary>回答</summary>

```python
sum_num = 0
for i in range(2, 20001):
    for j in range(2, int(i ** 0.5) + 1):
        if i % j == 0:
            break
    else:
        sum_num += i

print(sum_num)
```
</details>

## 数字を連続で入力してカウントしよう
ユーザーから10回数を入力し、同じ数が連続で入力された回数をカウントしてください。  
10回連続なら `perfect!!` と表示しましょう。

```bash
数字を入力してください: 1
連続なし
数字を入力してください: 1
2回連続
数字を入力してください: 1
3回連続
...
```

1つ前の入力値を `prev` のような変数に保存しておくことで、現在の入力値と比較して連続しているかどうかを判定できます。

<details>
  <summary>回答</summary>

```python
prev = None
count = 1

for i in range(10):
    num = int(input("数字を入力してください: "))
    if num == prev:
        count += 1
        print("{}回連続".format(count))
        if count == 10:
            print("perfect!!")
    else:
        count = 1
        print("連続なし")
    prev = num
```

</details>

## 数字の中に「5」があるか探そう
入力された数字を1桁ずつ調べて「5」が含まれるかを出力してください。

```bash
12345
5じゃないです
5じゃないです
5じゃないです
5じゃないです
5です!!
```

`input()` で受け取った値は文字列なので、`for` ループで1文字ずつ取り出して調べることができます。

<details>
  <summary>回答</summary>

```python
x = input("数字を入力してください: ")

for i in x:
    if i == "5":
        print("5です!!")
    else:
        print("5じゃないです")
```

</details>

## 足し算と引き算をしてみよう
2つの数字を入力し、足し算と引き算の結果を出力してください。

```bash
1つ目の数字: 4
2つ目の数字: 2
足し算の合計 6
引き算の合計 2
```

`input()` で受け取った文字列を `int()` で整数に変換し、`+` と `-` の演算子を使って計算します。

<details>
  <summary>回答</summary>

```python
x = int(input("1つ目の数字: "))
y = int(input("2つ目の数字: "))

print("足し算の合計", x + y)
print("引き算の合計", x - y)
```

</details>

## 九九の表を作ろう
九九を「式と答え」をセットで表示してください。

```bash
1 x 1 = 1
1 x 2 = 2
...
9 x 9 = 81
```

二重の `for` ループを使い、`print()` 関数で式と答えを整形して出力します。

<details>
  <summary>回答</summary>

```python
for i in range(1, 10):
    for j in range(1, 10):
        print(i, "x", j, "=", i * j)
```

</details>

## 正方形を描こう
入力された大きさの正方形を「*」で描きましょう。  

```bash
# 5の場合
*****
*   *
*   *
*   *
*****
```

`for` ループの中で `if` 文を使い、最初の行と最後の行、それ以外の行で処理を分けることで、中が空洞の図形を描くことができます。

<details>
  <summary>回答</summary>

```python
h = int(input("数字を入力してください: "))

for i in range(h):
    if i == 0 or i == h - 1:
        print("*" * h)
    else:
        print("*" + " " * (h - 2) + "*")
```

</details>

## フィボナッチ数列を出力しよう
10000未満のフィボナッチ数列を出力してください。

```bash
0 1 1 2 3 5 8 ... 6765
```

フィボナッチ数列は、前の2つの項の和が次の項になる数列です。`a, b = b, a + b` のように値を更新していくことで、数列を生成できます。

<details>
  <summary>回答</summary>

```python
a, b = 0, 1
while a < 10000:
    print(a, end=" ")
    a, b = b, a + b
print()
```

</details>

## 2つの素数判定
ユーザーから入力した2つの数字が両方とも素数なら `True`、そうでなければ `False` と出力してください。

```bash
1つ目の数字を入力してください: 7
2つ目の数字を入力してください: 11
True
```

素数判定のロジックを `is_prime` という関数にまとめることで、同じ処理を何度も書く必要がなくなり、コードが読みやすくなります。

<details>
  <summary>回答</summary>

```python
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

num1 = int(input("1つ目の数字を入力してください: "))
num2 = int(input("2つ目の数字を入力してください: "))

print(is_prime(num1) and is_prime(num2))
```

</details>

## バブルソートに挑戦！
整数リストを引数に取り、バブルソートで昇順に並べ替える関数を作りましょう。  
関数にリストを渡して、ソート前とソート後を表示してください。

```bash
[5, 3, 8, 1, 9] => [1, 3, 5, 8, 9]
```

バブルソートは、隣り合う要素を比較して入れ替えながら、リスト全体を整列させるアルゴリズムです。

<details>
  <summary>回答</summary>

```python
def bubble_sort(data):
    for i in range(len(data) - 1):
        for j in range(len(data) - i - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
    return data

data = [5, 3, 8, 1, 9]
print(f"{data} => {bubble_sort(data.copy())}")
```

</details>
