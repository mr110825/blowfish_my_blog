+++
id = "251129112924"
date = '2025-11-29T11:29:24+09:00'
draft = false
title = 'VSCode_マルチカーソル編集'
tags = ["ツール", "VSCode", "メモ", "実践"]
+++
## VSCode マルチカーソル編集とは？

複数箇所を同時編集できる便利機能。
変数名の一括変更やインデント調整など、繰り返し作業を大幅に効率化できる。

## ショートカット一覧

| 操作 | Windows | Mac |
|------|---------|-----|
| 任意の位置にカーソル追加 | `Alt + クリック` | `Option + クリック` |
| 上下に連続カーソル追加 | `Ctrl + Alt + ↑/↓` | `Cmd + Option + ↑/↓` |
| 矩形（ボックス）選択 | `Alt + Shift + ドラッグ` | `Option + Shift + ドラッグ` |
| 行頭へ移動 | `Home` | `Cmd + ←` |
| 同じ単語を全選択 | `Ctrl + Shift + L` | `Cmd + Shift + L` |

## 使い分け

| シーン | 推奨操作 |
|--------|----------|
| 飛び飛びの行を編集 | `Alt + クリック` |
| 連続した行を編集 | `Ctrl + Alt + ↓` で一気に追加 |
| 縦に揃った範囲を編集 | 矩形選択 |

## 実践例

**連続行の先頭にコメント追加**
1. 最初の行の先頭にカーソルを置く
2. `Ctrl + Alt + ↓` で下方向にカーソルを増やす
3. `//` を入力 → 全行に一括挿入

---

## 練習用テキスト

下記のテキストでマルチカーソル編集を試してみよう：

**例1: 行頭に `const ` を追加してみよう**
```
name = "Alice"
age = 25
city = "Tokyo"
email = "alice@example.com"
```

**例2: 行末に `;` を追加してみよう**
```
import React from 'react'
import useState from 'react'
import useEffect from 'react'
```

**例3: 各行を `console.log()` で囲んでみよう**
```
user.name
user.age
user.email
```
