+++
id = "251219202830"
date = '2025-12-19T20:28:30+09:00'
draft = false
title = 'VSCode Dev Containersでコンテナ内開発環境を構築する'
tags = ["ツール", "Docker", "VSCode", "実践"]
+++

## 今日学んだこと

VSCode Dev Containersを使うと、Dockerコンテナ内でVSCodeを直接開いて編集できることを学びました。ホスト側とコンテナ側の権限問題を回避でき、コンテナ内の環境でそのまま作業できます。

## 学習内容

### Dev Containersとは

Dockerコンテナ内でVSCodeを直接開き、コンテナ内のファイルを編集できるVSCode拡張機能です。

### Step 1: インストール

1. VSCodeの拡張機能で「Dev Containers」を検索
2. Microsoft製の拡張機能をインストール

拡張機能ID: `ms-vscode-remote.remote-containers`

### Step 2: 実行中のコンテナにアタッチ

1. コンテナを起動しておく（`docker compose up -d` など）
2. VSCodeで `Ctrl + Shift + P`（コマンドパレット）
3. `Dev Containers: Attach to Running Container...` を選択
4. 対象のコンテナを選択

新しいVSCodeウィンドウが開き、コンテナ内で直接編集できます。

### Step 3: フォルダを開く

アタッチ後、以下の手順でコンテナ内のフォルダを開きます。

1. `ファイル > フォルダを開く`
2. コンテナ内のパス（例：`/workspace/`）を指定

### Dev Containersのメリット

| メリット | 説明 |
|----------|------|
| 権限問題の解消 | rootで作成したファイルも編集可能 |
| 環境の一致 | コンテナ内の環境でそのまま作業 |
| 拡張機能の分離 | コンテナごとに拡張機能を管理可能 |

### 関連拡張機能

| 拡張機能 | 用途 |
|----------|------|
| Dev Containers | コンテナ内でVSCodeを開く |
| Docker | コンテナの管理・ログ確認 |

## まとめ

- Dev ContainersはDockerコンテナ内でVSCodeを直接開ける拡張機能
- `Attach to Running Container`で実行中のコンテナにアタッチ
- ホスト側とコンテナ側の権限問題を回避できる
- コンテナごとに拡張機能を分離して管理可能

## 参考

- [Developing inside a Container - VSCode公式ドキュメント](https://code.visualstudio.com/docs/devcontainers/containers)
