+++
id = "251212231019"
date = '2025-12-12T23:10:19+09:00'
draft = false
title = 'Raycast for Windows + Toggl Track拡張でホットキーから時間計測'
tags = ["ツール", "Raycast", "実践"]
+++
## 今日学んだこと

Raycast for WindowsにToggl Track拡張を導入し、ホットキー一発で時間計測の開始・停止ができるようになりました。ブラウザを開く手間がなくなり、計測開始のハードルが下がりました。

## 学習内容

### 背景

Toggl Trackで学習時間を記録していたが、毎回ブラウザを開いて操作するのが面倒だった。ショートカットキーで計測を開始・停止できる環境を作りたいと考えた。

### セットアップ手順

#### Step 1: Toggl Track拡張のインストール

1. Raycastを開き「Store」と入力
2. 「Toggl Track」を検索してインストール

#### Step 2: APIトークンの設定

1. https://track.toggl.com/profile にアクセス
2. ページ下部の「API Token」をコピー
3. Raycast → 拡張機能の設定 → Toggl Track → APIトークンを貼り付け

![Raycast StoreのToggl Track拡張機能ページ](/img/raycast_toggle.png)
*「Configure Extension」を選択するとAPIトークンの設定画面に進めます*

#### Step 3: ホットキーの設定

Raycast Settings → Extensions → Toggl Track → Commands で設定。

| コマンド | 設定例 |
|---------|--------|
| Start/Stop Time Entry | `Ctrl+Shift+T` |

![ホットキーの設定](/img/hotkey_20251212.png)

### 使い方

**計測開始:**

1. `Ctrl+Shift+T` を押す
2. 過去のエントリー一覧が表示される
3. 再開したいエントリーを選択、または「Create a new time entry」で新規作成

**計測停止:**

1. `Ctrl+Shift+T` を押す
2. 一番上に表示される実行中エントリーを選択してEnter

## まとめ

- Raycast for WindowsはToggl Track拡張に対応している
- APIトークンを設定するだけで連携可能
- ホットキー設定で、任意のキーから計測開始・停止ができる

## 参考

- [Raycast Store: Toggl Track](https://www.raycast.com/franzwilhelm/toggl-track)