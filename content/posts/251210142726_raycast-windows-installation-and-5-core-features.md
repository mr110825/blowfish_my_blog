+++
id = "251210142726"
date = '2025-12-10T14:27:26+09:00'
draft = false
title = 'Raycast Windows版の導入と基本機能5つ'
tags = ["ツール", "Windows", "入門", "ハンズオン・チュートリアル"]
+++
## 今日学んだこと

Raycast Windows版を導入しました。キーボード操作で様々な作業を高速に行えるランチャーアプリで、App Launcher、Clipboard History、Snippets、Quicklinks、Calculatorの5つの基本機能を覚えることで、日常業務の効率化が期待できます。

## 学習内容

### Raycastとは

キーボード操作で様々な作業を高速に行えるランチャーアプリです。Macで人気だったツールがWindows版としてリリースされました。

| 項目 | 内容 |
|------|------|
| 対応OS | Windows 10（21H2以降）、Windows 11 |
| 料金 | 基本機能は無料（Pro/Teamsプランは有料） |
| 現状 | ベータ版（v0.39.1.0） |

### 導入方法

以下のいずれかの方法でインストールします。

**方法1：Microsoft Store**

https://www.raycast.com/windows から「Download on Microsoft Store」をクリック

**方法2：Winget**
```powershell
winget install raycast
```

### 主な機能一覧

| 機能 | 内容 |
|------|------|
| App Launcher | アプリ名を数文字入力するだけで即起動 |
| File Search | ローカルファイルを高速検索 |
| Clipboard History | コピー履歴を保存・検索・再利用 |
| Snippets | 定型文をキーワードで即挿入 |
| Quicklinks | よく使うURLに即アクセス |
| Calculator | 自然言語で計算 |
| Emoji Picker | 絵文字を素早く検索・入力 |
| Quick AI | ブラウザを開かずにAIに質問 |

### まず覚える5つの機能

#### 1. App Launcher（アプリ起動）

1. `Alt + Space`でRaycastを起動
2. アプリ名の一部を入力（例：`chr` → Chrome）
3. `Enter`で起動

完全一致は不要で、`te`でTeams、`ou`でOutlookなど、あいまい検索に対応しています。使用頻度が高いアプリは自動で上位に表示されます。

> 「スタートメニューを開きそうになったらRaycast」と意識すると定着しやすいです。

#### 2. Clipboard History（クリップボード履歴）

1. `Alt + Space` → `clip`と入力 → Enter
2. 過去にコピーした履歴一覧が表示
3. 使いたい項目を選んで`Enter`でペースト

Settings → Extensions → Clipboard Historyにホットキーを設定すると、直接履歴画面を開けます（例：`Ctrl + Shift + V`）。

> 「さっきコピーしたIPどこだっけ」という場面で活躍します。

#### 3. Snippets（定型文登録）

1. `Alt + Space` → `create snippet`と入力 → Enter
2. 登録画面で以下を入力
   - **Name:** 用途がわかる名前（例：「対応完了メール」）
   - **Snippet:** 本文
   - **Keyword:** 呼び出すトリガー（例：`!done`）
3. 保存後、どのアプリでも`!done`と打つと自動展開

**登録例：**

| Keyword | 内容 |
|---------|------|
| `!done` | 対応完了いたしました。ご確認をお願いいたします。 |
| `!ack` | お問い合わせありがとうございます。確認次第ご連絡いたします。 |
| `!sig` | 自分の署名 |

#### 4. Quicklinks（よく使うURLの登録）

1. `Alt + Space` → `create quicklink`と入力 → Enter
2. 登録画面で以下を入力
   - **Name:** わかりやすい名前（例：「監視ダッシュボード」）
   - **Link:** URL
3. 以降は`Alt + Space` → 登録した名前の一部を入力 → Enterで即アクセス

**登録例：**

| Name | Link |
|------|------|
| AWS Console | https://console.aws.amazon.com/ |
| GitHub | https://github.com/ |

> ブラウザを開いてブックマークを探す手間を省略できます。

#### 5. Calculator（計算機）

1. `Alt + Space`でRaycastを起動
2. そのまま計算式を入力（例：`1024 * 8`）
3. 結果が即表示され、Enterでクリップボードにコピー

**対応している計算：**

| 入力例 | 用途 |
|--------|------|
| `100 + 200 * 3` | 四則演算 |
| `100 USD to JPY` | 単位変換 |
| `0xFF to decimal` | 進数変換 |
| `0b11111111` | 2進数→10進数（サブネットマスク確認） |
| `1024 * 1024 * 1024` | GB→バイト変換 |

> 電卓アプリを起動せずにその場で計算できます。

### 拡張機能

ストアから追加可能な拡張機能も用意されています。

- GitHub - PR・Issue・通知確認
- Slack - ステータス変更・未読確認
- Notion - ページ検索・作成
- Todoist - タスク管理

## まとめ

- Raycastはキーボード操作で作業を高速化するランチャーアプリ
- Windows版はベータ版だが、基本機能はすべて無料で使える
- まず覚える5つの機能：App Launcher、Clipboard History、Snippets、Quicklinks、Calculator
- 普段の作業の中で「これってRaycastで効率化できないかな？」と考えながら少しずつ活用範囲を広げていく

## 参考

- [Raycast Windows版 公式サイト](https://www.raycast.com/windows)
- [Raycast 公式マニュアル](https://manual.raycast.com/windows/getting-started)
- [Raycastの使い方（Zenn）](https://zenn.dev/massa/articles/raycast-usage)