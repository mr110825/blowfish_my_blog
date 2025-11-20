+++
id = "251120224617"
date = '2025-11-20T22:46:17+09:00'
draft = false
title = 'Gitコミット前の変更確認ガイド'
tags = []
+++
## はじめに
`git commit`を実行する際のコミットメッセージを作成するために\
変更内容を確認するコマンドや手順を整理してメモとする。

## 状況確認コマンド
```bash
# 全体把握
git status

# すべての変更を確認
git diff HEAD --stat

# まだ git add していない変更を確認
git diff --stat

# git add した変更を確認
git diff --staged --stat
git diff --cached --stat
```

## 変更を確定するコマンド
```bash
# コミット
git commit -m "..."

# リモートリポジトリへプッシュ
git push
```

## 日本語ファイル名の表示設定
デフォルトでは日本語ファイル名がエスケープされて表示される問題を解決
実行後、日本語ファイル名が正常に表示される。
```bash
# グローバル設定（全リポジトリに適用）
git config --global core.quotePath false

# または、このリポジトリだけ設定
git config core.quotePath false
```

## その他の有用な設定（オプション）
```bash
# 日本語コミットメッセージも正常表示
git config --global core.pager "less -R"

# git log で日本語を正しく表示
git config --global i18n.logOutputEncoding utf-8
```

## まとめ
- コミット前の変更確認には git diff HEAD --stat が便利
- ステージング済みの変更は --staged オプションで確認
- 日本語表示問題は core.quotePath false で解決
