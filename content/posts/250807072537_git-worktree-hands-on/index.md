+++
id = "250807072537"
date = '2025-08-07T07:25:37+09:00'
draft = false
title = 'git worktree ハンズオン'
tags = ["Git"]
+++

## はじめに

**Git worktree**は、1つのGitリポジトリに対して複数のワーキングツリー（作業ディレクトリ）を同時に作成・管理するための強力な機能です。この記事では、git worktreeの基本的な使い方を実践的なハンズオンで学びます。

### 解決する課題
- ブランチ切り替え時の作業内容の退避・復元の手間
- 複数機能を並行開発する際の効率性の問題
- 緊急バグ修正と通常開発作業の両立

### この記事で学べること
- git worktreeの基本概念と仕組み
- 複数ワーキングツリーの作成・管理方法
- 実際の開発現場での活用パターン

### 対象読者
- Gitの基本操作（add, commit, merge）を理解している方
- 複数ブランチでの並行作業を効率化したい方
- git worktreeを初めて使用する開発者

## 前提条件

- **Git**: v2.5以降（git worktreeコマンド対応版）
- **OS**: Windows, macOS, Linux
- **必要な知識**: Gitの基本操作（clone, checkout, merge等）

## ハンズオン

### Step 0: 準備

ハンズオン用のリポジトリを準備します：

```bash
# 作業用ディレクトリの作成と初期化
mkdir git-worktree-handson-tutorial
cd git-worktree-handson-tutorial

# Gitリポジトリの初期化
git init

# 初期ファイルの作成とコミット
echo "Hello World" > main.txt
git add main.txt
git commit -m "first commit"
```

{{< alert icon="lightbulb" cardColor="#d9ff00be" iconColor="#1d3557" textColor="#000000ff" >}}
このハンズオンではローカルリポジトリを使用しますが、実際の開発ではリモートリポジトリをクローンした環境でも同様に利用できます。
{{< /alert >}}

### Step 1: 新機能開発用ワークツリーの作成

`main`ブランチとは独立した場所で新機能`feature-A`の開発を行うため、専用ワークツリーを作成します：

```bash
# feature-A用のワークツリーとブランチを同時作成
git worktree add ./feature-a-worktree -b feature-A
```

**パラメータ説明:**
- `./feature-a-worktree`: 新規作成するディレクトリのパス
- `-b feature-A`: 新規作成するブランチ名

作成されたワークツリーの確認：

```bash
git worktree list
```

**実行結果例:**
```bash
/path/to/git-worktree-handson-tutorial        7a8b9c1 [main]
/path/to/git-worktree-handson-tutorial/feature-a-worktree  7a8b9c1 [feature-A]
```

この出力から、2つのワークツリーが並存していることが確認できます。

### Step 2: feature-Aワークツリーでの開発作業

作成したワークツリーで実際の機能開発を行います：

```bash
# feature-Aワークツリーに移動
cd feature-a-worktree

# 現在のブランチ確認
git branch
# 出力: * feature-A

# 新機能のファイルを作成
echo "Feature A implementation" > feature-A.txt
git add feature-A.txt
git commit -m "feat: Add feature-A implementation"
```

**検証**: 同時に元のディレクトリでも作業が可能であることを確認：

```bash
# 別のターミナルまたは後で元のディレクトリに戻って確認
cd .. # 元のディレクトリに戻る
git branch
# 出力: * main
ls # main.txtのみが存在（feature-A.txtは存在しない）
```

### Step 3: 開発完了後のマージ作業

feature-Aの開発が完了したため、mainブランチにマージします：

```bash
# mainブランチ（元のワークツリー）にいることを確認
pwd # /path/to/git-worktree-handson-tutorial
git branch
# 出力: * main

# feature-Aブランチをmainにマージ
git merge feature-A
```

マージ結果の確認：

```bash
# マージ履歴をグラフで確認
git log --graph --oneline --all

# ファイルが統合されていることを確認
ls
# 出力: main.txt  feature-A.txt
```

### Step 4: ワークツリーのクリーンアップ

開発完了後は不要になったワークツリーを削除してリポジトリを整理します：

```bash
# 現在のワークツリー一覧を確認
git worktree list

# feature-Aワークツリーを削除
git worktree remove feature-a-worktree
```

{{< alert icon="lightbulb" cardColor="#d9ff00be" iconColor="#1d3557" textColor="#000000ff" >}}
**注意**: ワークツリー内に未コミットの変更がある場合、削除は失敗します。その場合は`--force`オプションで強制削除するか、事前に変更をコミットまたは破棄してください。
{{< /alert >}}

**クリーンアップ完了の確認:**

```bash
# ワークツリー一覧を再確認（mainのみ残っていることを確認）
git worktree list

# 万が一、ディレクトリが残っている場合は手動削除
rm -rf feature-a-worktree
```

## 実践的な活用パターン

### パターン1: 緊急バグ修正と機能開発の並行作業

```bash
# 通常の機能開発中（feature-loginブランチで作業中）
git worktree add ../hotfix-worktree -b hotfix/critical-bug

# hotfix作業完了後
cd ../hotfix-worktree
# バグ修正作業...
git add . && git commit -m "fix: critical security issue"

# mainにマージ
cd ../main-worktree
git merge hotfix/critical-bug

# 元の機能開発に戻る
cd ../feature-login-worktree
# 作業を継続...
```

### パターン2: 複数バージョンの同時保守

```bash
# v1.0系の保守用ワークツリー
git worktree add ../v1-maintenance origin/release-1.0

# v2.0系の保守用ワークツリー
git worktree add ../v2-maintenance origin/release-2.0

# 各バージョンで独立してバグ修正が可能
```

## トラブルシューティング

### よくある問題と解決法

**問題1: ワークツリーの削除ができない**
```bash
# エラー例: "worktree contains modified or untracked files"
# 解決法1: 変更を確認して必要に応じてコミット
cd problem-worktree
git status
git add . && git commit -m "save changes"

# 解決法2: 強制削除
git worktree remove --force problem-worktree
```

**問題2: 同じブランチを複数のワークツリーで使用しようとしてエラー**
```bash
# エラー例: "branch 'feature-x' is already checked out"
# git worktreeでは同じブランチを複数箇所で同時にチェックアウトできません
# 解決法: 異なるブランチ名を使用するか、既存のワークツリーを削除
```

**問題3: ディレクトリが残っているがgit worktree listに表示されない**
```bash
# 管理情報のクリーンアップ
git worktree prune

# 手動でディレクトリ削除
rm -rf orphaned-worktree
```

## コマンドリファレンス

```bash
# 基本的なワークツリー操作
git worktree add <path> -b <branch-name>    # 新規ブランチ作成と同時にワークツリー作成
git worktree add <path> <existing-branch>   # 既存ブランチからワークツリー作成
git worktree list                           # ワークツリー一覧表示
git worktree remove <path>                  # ワークツリー削除
git worktree prune                          # 孤立した管理情報のクリーンアップ

# 高度な操作
git worktree add --detach <path> <commit>   # 特定のコミットをワークツリーとして作成
git worktree remove --force <path>          # 未保存の変更があっても強制削除
git worktree move <path> <new-path>         # ワークツリーの移動
git worktree lock <path>                    # ワークツリーをロック（自動削除を防ぐ）
git worktree unlock <path>                  # ワークツリーのロック解除
```

## まとめ

このハンズオンを通じて、git worktreeの基本的な操作から実践的な活用方法まで学習しました。

### 主要ポイント
- **複数ワークツリーの同時管理**: 1つのリポジトリで複数のブランチを並行作業
- **効率的な開発フロー**: ブランチ切り替えに伴う時間的コストの削減
- **適切なクリーンアップ**: 作業完了後のワークツリー削除でリポジトリを整理

### 実践的な価値
- **開発効率向上**: ビルド時間や依存関係の再インストール時間を短縮
- **作業の並行性**: 緊急対応と通常開発を同時進行
- **コンテキストスイッチの最小化**: 作業内容の退避・復元が不要

### 次のステップ
1. 実際のプロジェクトでgit worktreeを試用
2. チーム開発でのワークフロー改善に活用
3. CI/CDパイプラインとの統合検討

git worktreeを活用することで、Git操作の効率性が大幅に向上し、より柔軟な開発体験を実現できます。

## 参考リンク

- [Git公式ドキュメント - git-worktree](https://git-scm.com/docs/git-worktree)
- [Qiita：徹底解説：git worktree の使い方](https://qiita.com/syukan3/items/dab71e88ce91bca44432)