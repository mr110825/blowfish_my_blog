+++
id = "1757399400"
date = '2025-09-09T15:30:00+09:00'
draft = false
title = 'Hugo+Blowfish｜mainSections設定でコンテンツ分離する方法'
tags = ["hugo", "blowfish"]
+++

## はじめに

Hugo静的サイトジェネレーター + Blowfishテーマを使用したサイトにおいて、トップページの「最近の記事」セクションに特定のコンテンツセクション（この場合はスクラップ）を表示させない方法について整理しました。

この設定により、メインの記事とスクラップメモを分離して表示でき、読者により適切なコンテンツ体験を提供できます。

## 設定方法

### 1. hugo.tomlファイルの設定

`config/_default/hugo.toml`に`mainSections`設定を追加します。

```toml
enableEmoji = true

# Only include posts section in recent articles
mainSections = ["posts"]

# googleAnalytics = "G-XXXXXXXXX"
```

**効果:**
- `mainSections = ["posts"]`により「最近の記事」には`posts`セクションの記事のみが表示される
- `scraps`ディレクトリの記事は自動的に除外される


## 設定反映手順

| 手順 | 説明 |
| :--- | :--- |
| **1. ファイル編集** | 上記の設定を該当ファイルに追加 |
| **2. サーバー再起動** | `hugo server`コマンドでローカルサーバーを再起動 |
| **3. 確認** | トップページで「最近の記事」にpostsのみが表示されることを確認 |

### 設定反映コマンド

```bash
# サーバー再起動
hugo server

# 下書き含む場合
hugo server -D
```

## 変更の効果

設定後の動作は以下のようになります：

- ✅ **トップページ**: 「最近の記事」にはpostsディレクトリの記事のみ表示
- ✅ **スクラップページ**: `/scraps/`は通常通りアクセス可能
- ✅ **記事分離**: メインコンテンツと学習メモの適切な分離
- ✅ **SEO効果**: 読者にとって価値の高いメインコンテンツが優先表示

## トラブルシューティング

### よくある問題と解決策

| 問題 | 原因 | 解決策 |
| :--- | :--- | :--- |
| **設定が反映されない** | サーバーが再起動されていない | `hugo server`コマンドでサーバーを再起動 |
| **スクラップページが表示されない** | `_index.md`が作成されていない | `content/scraps/_index.md`を作成 |
| **他のセクションも除外したい** | `mainSections`の設定が不適切 | `mainSections = ["posts", "articles"]`のように配列に追加 |

## 応用設定

### 複数セクションを含める場合

```toml
# 複数のセクションを「最近の記事」に含める
mainSections = ["posts", "articles", "tutorials"]
```

### セクション別の除外設定

特定のセクションのみ除外したい場合は、Front Matterでの制御も可能です：

```yaml
---
title: "記事タイトル"
excludeFromRecent: true  # この記事を「最近の記事」から除外
---
```

## 参考リンク

- [Hugo公式ドキュメント - mainSections](https://gohugo.io/variables/site/#site-variables)
- [Blowfishテーマ公式ドキュメント](https://blowfish.page/)
- [Hugo Configuration Documentation](https://gohugo.io/getting-started/configuration/)