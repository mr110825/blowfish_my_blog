# スクラップを「最近の記事」から除外する変更内容

## 概要
トップページの「最近の記事」セクションにスクラップが表示されないようにする設定を適用しました。

**対象**: Hugo静的サイトジェネレーター + Blowfishテーマを使用したサイト

## 変更されたファイル

### 1. `config/_default/hugo.toml`
- `mainSections = ["posts"]`を追加
- これにより「最近の記事」には`posts`セクションの記事のみが表示されるようになります

```toml
enableEmoji = true

# Only include posts section in recent articles
mainSections = ["posts"]

# googleAnalytics = "G-XXXXXXXXX"
```

### 2. `content/scraps/_index.md` (新規作成)
- スクラップセクション用のインデックスファイルを作成
- `cascade`設定で`excludeFromRecent: true`を設定（補助的な設定）

```markdown
---
title: "スクラップ"
draft: false
cascade:
  excludeFromRecent: true
---

スクラップ（メモ）の一覧です。
```

## 変更の効果
- トップページの「最近の記事」にはpostsディレクトリの記事のみが表示される
- scrapsディレクトリの記事は除外される
- スクラップページ（/scraps/）は通常通りアクセス可能

## 設定反映方法
変更を反映するには、Hugoサーバーの再起動が必要です。

```bash
hugo server
```