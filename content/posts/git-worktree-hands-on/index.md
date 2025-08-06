+++
date = '2025-08-07T07:25:37+09:00'
draft = false
title = 'git worktree ハンズオン'
tags = ["Git"]
+++
# git worktree ハンズオン

## 1. はじめに

### `git worktree` とは？

`git worktree` は、1つのGitリポジトリに対して、複数のワーキングツリー（作業ディレクトリ）を同時に作成し、管理するためのGitコマンドです。

通常、`git checkout` を使ってブランチを切り替えると、現在のワーキングツリーの内容が対象ブランチのものに完全に置き換わります。しかし、`git worktree` を利用すると、異なるブランチをそれぞれ別のディレクトリにチェックアウトした状態に保つことができます。

### `git worktree` はどのような時に便利か？

この機能は、以下のような状況で非常に役立ちます。

*   **機能開発とバグ修正の並行作業:**
    *   大規模な新機能（例: `feature-A`）の開発中に、本番環境で発生した緊急のバグ（例: `hotfix`）にすぐ対応する必要がある場合。`feature-A`の作業を`git stash`などで退避させることなく、別のディレクトリで`hotfix`ブランチの作業をすぐに始められます。
*   **複数の機能の同時開発:**
    *   複数のフィーチャーブランチを並行して開発し、それぞれの動作確認を簡単に行いたい場合。ブランチごとにディレクトリが分かれているため、ビルド成果物などが混ざり合うこともありません。

---

## 2. ハンズオン

### Step 0: 準備

まず、ハンズオン用のリポジトリを準備します。

```bash
# 1. 作業用のディレクトリを作成し、移動します
mkdir git-worktree-handson-tutorial
cd git-worktree-handson-tutorial

# 2. Gitリポジトリを初期化します
git init

# 3. 最初のファイルを作成してコミットします
echo "Hello World" > main.txt
git add main.txt
git commit -m "first commit"
```

### Step 1: `feature-A` のためのワークツリー作成

`main`ブランチとは別の場所で、新しい機能 `feature-A` の開発に着手します。そのために、専用のワークツリーを作成しましょう。

```bash
# 'feature-A' という名前の新しいブランチを、'feature-a-worktree' というディレクトリに作成します
git worktree add ./feature-a-worktree -b feature-A
```

*   `./feature-a-worktree`: 新しく作成されるディレクトリのパスです。
*   `-b feature-A`: 新しく作成するブランチの名前です。このブランチが `feature-a-worktree` ディレクトリにチェックアウトされます。

`git worktree list` コマンドで、現在のワークツリーの状態を確認してみましょう。

```bash
git worktree list
```

以下のような出力が表示され、2つのワークツリーが存在することがわかります。

```
/path/to/git-worktree-handson-tutorial  (bare)
/path/to/git-worktree-handson-tutorial/feature-a-worktree  [feature-A]
```

### Step 2: `feature-A` ワークツリーでの作業

`feature-A` の開発作業を進めます。

```bash
# 1. feature-A のワークツリーに移動します
cd feature-a-worktree

# 2. 現在のブランチを確認します
git branch # => * feature-A

# 3. feature-A のための新しいファイルを作成し、コミットします
echo "Goodby World" > feature-A.txt
git add feature-A.txt
git commit -m "feat: Add feature-A file"
```

これで、`feature-A`ブランチに新しいコミットが追加されました。

### Step 3: `feature-A` のマージ

`feature-A`の開発が完了したと仮定して、`main`ブランチにマージします。

```bash
# 1. 元のワークツリー（mainブランチ）に移動します
cd ..

# 2. main ブランチにいることを確認します
git branch # => * main

# 3. feature-A ブランチをマージします
git merge feature-A
```

`git log --graph --oneline --all` を実行すると、`feature-A`が`main`ブランチにマージされた歴史を確認できます。

### Step 4: ワークツリーのクリーンアップ

作業が完了したブランチのワークツリーは不要なので、削除してリポジトリを整理します。

```bash
# ワークツリーの一覧を再度確認
git worktree list

# 不要になったワークツリーを削除する
# 注意: ワークツリー内に未コミットの変更が残っている場合、削除は失敗します。
# その場合は --force オプションで強制削除できます。
git worktree remove feature-a-worktree

# .gitの管理情報から削除されるだけで、ディレクトリ自体は残るため手動で削除します
rm -rf feature-a-worktree
```

`git worktree prune` コマンドは、何らかの理由でディレクトリだけが先に削除されてしまった場合に、関連する管理情報をクリーンアップするのに役立ちます。

---

## 3. まとめ

このハンズオンでは、以下のことを学びました。

*   `git worktree add` で新しいワークツリーとブランチを作成する方法
*   複数のワークツリー間を `cd` で自由に移動し、並行して作業を進める方法
*   作業が完了したワークツリーを `git worktree remove` で安全に削除する方法

`git worktree` を活用することで、ブランチの切り替えに伴う時間のかかるビルドや依存関係の再インストールといった手間を回避し、開発効率を劇的に向上させることができます。ぜひ、日々の開発に取り入れてみてください。

---

## 4. コマンドリファレンス

```bash
# 指定したパスに新しいワークツリーを作成
# 同時に新しいブランチを作成してチェックアウトする
git worktree add <path> -b <branch-name>
```

```bash
# ワークツリーの一覧を表示
git worktree list
```

```bash
# 指定したパスのワークツリーを削除
git worktree remove <path>
```

```bash
# ワークツリーの管理情報をクリーンアップ
git worktree prune
```

## 5. 参考リンク
- [Qiita：徹底解説：git worktree の使い方](https://qiita.com/syukan3/items/dab71e88ce91bca44432)
- [git-worktree - Manage multiple working trees](https://git-scm.com/docs/git-worktree)