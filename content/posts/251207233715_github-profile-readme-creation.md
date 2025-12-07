+++
id = "251207233715"
date = '2025-12-07T23:37:15+09:00'
draft = false
title = 'GitHubプロフィールREADMEを作成してみた'
tags = ["ツール", "GitHub", "実践", "メモ"]
+++
## 今日学んだこと

GitHubプロフィールREADMEの作成方法を学びました。自分のユーザー名と同じ名前のリポジトリを作成してREADME.mdを配置すると、プロフィールページのトップに自己紹介を表示できます。

## 学習内容

### GitHubプロフィールREADMEとは

GitHubには「プロフィールREADME」という機能があります。自分のユーザー名と同じ名前のリポジトリ（例：`username/username`）を作成し、README.mdを配置すると、GitHubプロフィールページのトップに表示されます。

通常のプロフィールページでは、アイコン・名前・Bio程度しか表示されませんが、この機能を使うと自己紹介やスキル、プロジェクト紹介などを自由に記載できます。

### 作成手順

#### Step 1: リポジトリを作成

1. GitHubにログイン
2. 右上の「+」→「New repository」をクリック
3. Repository nameに**自分のユーザー名と同じ名前**を入力
4. 「Public」を選択（Privateだとプロフィールに表示されない）
5. 「Add a README file」にチェックを入れる
6. 「Create repository」をクリック

ユーザー名と同じ名前を入力すると、以下のようなメッセージが表示されます。

> **username/username is a special repository.**
> Its README.md will appear on your public profile.

このメッセージが表示されれば、設定は正しいです。

#### Step 2: README.mdを編集

作成されたリポジトリのREADME.mdを編集します。Markdown形式で自由に書けます。

最初は以下のようなテンプレートが入っています。
```markdown
### Hi there 👋

<!--
**username/username** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I'm currently working on ...
- 🌱 I'm currently learning ...
- ...
-->
```

コメントアウトを外して編集するか、自分で一から書き直します。

#### Step 3: プロフィールページで確認

編集後、自分のGitHubプロフィールページ（`https://github.com/username`）にアクセスすると、README.mdの内容が表示されています。

### 何を書けばいいか

最初は何を書けばいいか迷いました。参考までに、自分が書いた項目を紹介します。

| セクション | 内容 |
|-----------|------|
| 自己紹介 | 何をしている人か、何に興味があるか |
| プロジェクト実績 | 取り組んだプロジェクトの概要と使用技術 |
| 技術アウトプット | ブログやZennなどの発信活動 |
| スキルセット | 使える技術をカテゴリ別に整理 |
| 保有資格 | 取得した資格を年度順に |
| 連絡先 | SNSやメールアドレス |

### 実際に書いてみた例

参考として、自分のプロフィールREADMEを載せておきます。

**GitHub**: https://github.com/mr110825

正直、最初はもっとシンプルでした。プロジェクトが完成したり、資格を取得したりするたびに少しずつ更新しています。

### 書いてみて気づいたこと

実際にプロフィールREADMEを書いてみて、いくつか気づいたことがあります。

**完成したものを上に置く**

作成中のプロジェクトより、完成したプロジェクトを先に書いた方が見栄えが良いと感じました。見る人は最初の数秒で判断するので、アピールできるものを上に持ってくるのが良さそうです。

**「学習中」より具体的な内容を書く**

「Terraform学習中」より「Terraformで○○を構築」のように、何をしたか具体的に書いた方が伝わりやすいと思いました。

**テーブル形式は見やすい**

資格やスキルセットなど、項目が多いものはテーブル形式にすると一覧性が高くなりました。

## まとめ

- プロフィールREADMEは`username/username`リポジトリのREADME.mdに書く
- リポジトリはPublicにする必要がある
- Markdown形式で自由に自己紹介を書ける
- 完成したプロジェクトや具体的な実績を上位に置くと効果的

## 参考

- [Managing your profile README - GitHub Docs](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme)
- [自分のプロフィール](https://github.com/mr110825)