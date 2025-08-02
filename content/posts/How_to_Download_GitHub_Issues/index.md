+++
date = '2025-08-03T01:55:16+09:00'
draft = false
title = 'Github CLIでIssuesをMarkdownファイルとしてダウンロードする方法'
+++
私は普段、Githubのプライベートリポジトリにメモやアイデアを書き溜めています。
リポジトリには、清書したメモなどを保管。Issuesに一時メモや作業メモをまとめています。
（IssuesについてはZennのスクラップと同じような感じで利用しています。）
しかし、Issuesの作業メモなどは書き溜めた後、コピー&ペーストするような方法ばかりで、
効率的に活用できていませんでした。

この問題を解決するため、Issuesをmarkdownファイルとしてダウンロードして、ローカル環境で管理することを決めました。この記事では、GitHub CLIを使ってGitHubのIssuesをmarkdownファイルとしてダウンロードする方法を紹介します。

**対象読者：**

- Github CLIの基本的な使い方を知っている方
- ドキュメント作成や記事執筆の素材としてIssuesを活用したい方

:::message
Isseusを取得する対象としてはプライベートリポジトリかつ、Githubの無料プランを利用しているユーザーを想定しております。

パブリックリポジトリまたは有料プランユーザーの場合は、Github Wiki機能など互換性のある機能があるため、そちらを利用するほうが手順も簡単で、効率的にドキュメント運用できると考えられます。
:::

**前提条件**

- **OS**: Linux（Ubuntu）環境（WSL2含む）
- **権限**: GitHubにて対象リポジトリへのアクセス権限を保有している
- **サンプル**: 当記事では[サンプルリポジトリ（mr110825/github-issues-to-markdown）](https://github.com/mr110825/github-issues-to-markdown/issues/1)を例として説明します

## 環境セットアップ

### GitHub CLIのインストール

```bash
# インストール状況の確認
gh --version

# GitHub CLIのインストール（必要な場合）
sudo apt install gh
```

### GitHub CLIへのログイン

```bash
# ログイン状況の確認
gh auth status

# GitHub CLIへログイン実行
gh auth login
```

:::message
GitHub CLIへのログイン手順の詳細については、以下の記事をご参照ください。

- [【Git のセットアップ】GitHub CLI を使って GitHub に接続する](https://zenn.dev/babyjob/articles/3faf85c33b8725)
- [GitHub CLIのクイックスタート](https://docs.github.com/ja/enterprise-cloud@latest/github-cli/github-cli/quickstart)

:::

## リポジトリのIssues一覧確認

```bash
gh issue list --repo <OWNER/REPO>
```

### 実行例

```bash
# サンプルのリポジトリ（mr110825/github-issues-to-markdown）のIssueを対象とする
gh issue list --repo mr110825/github-issues-to-markdown
```

#### 出力例

```bash
ID  TITLE               LABELS  UPDATED         
#1  サンプル用のIssues          about 1 hour ago
```

## Issueの取得

```bash
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments > <FILENAME>.md
```

### 実行例

```bash
# サンプルのリポジトリ（mr110825/github-issues-to-markdown）のIssues#1を「test1.md」として取得する
gh issue view 1 --repo mr110825/github-issues-to-markdown --comments > test1.md
```

#### 出力例

```markdown
author:	mr110825
association:	owner
edited:	true
status:	none
--
記事を投稿するので構成をまとめる
--
author:	mr110825
association:	owner
edited:	true
status:	none
--
必要な手順

- [x] 文章企画を構成
- [x] サンプルのリポジトリを作成
- [x] 記事作成
- [x] 記事投稿
--
```

:::message
この方法は最もシンプルですが、出力されるファイルには多くのメタデータが含まれており、実際の内容を読みにくく感じました。特に、複数のコメントがある場合、どのコメントがどのタイミングで投稿されたのかが分かりにくいという問題があります。
:::

## Issueの取得（不要なプロパティを除外してISO形式でコメントのみを取得）

```bash
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments --json comments --template '{{range .comments}}## コメント ({{.createdAt}})

{{.body}}

---
{{end}}' > <FILENAME>.md
```

### 実行例

```bash
# サンプルのリポジトリ（mr110825/github-issues-to-markdown）のIssues#1を「test2.md」として取得する
gh issue view 1 --repo mr110825/github-issues-to-markdown --comments --json comments --template '{{range .comments}}## コメント ({{.createdAt}})

{{.body}}

---
{{end}}' > test2.md
```

#### 出力例

```markdown
## コメント (2025-06-28T12:24:28Z)

記事を投稿するので構成をまとめる

---
## コメント (2025-06-28T12:25:50Z)

必要な手順

- [x] 文章企画を構成
- [x] サンプルのリポジトリを作成
- [x] 記事作成
- [x] 記事投稿

---
```

:::message
この方法では、メタデータが除去され、コメントの内容と投稿日時が明確に表示されるようになりました。しかし、ISO形式の日時表記は読みづらいため、さらに改善が必要です。
:::

## Issueの取得（jqコマンドで日時フォーマットを日本語表記に変換）

```bash
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments --json comments | jq -r '.comments[] | "## コメント (" + (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y年%m月%d日 %H時%M分")) + ")\n\n" + .body + "\n\n---\n"' > <FILENAME>.md
```

```bash
# jqコマンドのインストール（必要な場合）
sudo apt install jq
```

### 実行例

```bash
# サンプルのリポジトリ（mr110825/github-issues-to-markdown）のIssues#1を「test3.md」として取得する
gh issue view 1 --repo mr110825/github-issues-to-markdown --comments --json comments | jq -r '.comments[] | "## コメント (" + (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y年%m月%d日 %H時%M分")) + ")\n\n" + .body + "\n\n---\n"' > test3.md
```

#### 出力例

```markdown
## コメント (2025年06月28日 12時24分)

記事を投稿するので構成をまとめる

---
## コメント (2025年06月28日 12時25分)

必要な手順

- [x] 文章企画を構成
- [x] サンプルのリポジトリを作成
- [x] 記事作成
- [x] 記事投稿

---
```

:::message
この方法が最も実用的です。日本語表記により、日時が直感的に理解でき、ドキュメントとして保存した際にも読みやすくなります。ただし、`jq`コマンドのインストールが必要になるため、環境によっては追加のセットアップが必要になります。
:::

## コマンドのまとめ

```bash
# Issues一覧確認
gh issue list --repo <OWNER/REPO>
```

```bash
# Issueの取得
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments > <FILENAME>.md
```

```bash
# Issueの取得（不要なプロパティを除外してISO形式でコメントのみを取得）
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments --json comments --template '{{range .comments}}## コメント ({{.createdAt}})

{{.body}}

---
{{end}}' > <FILENAME>.md
```

```bash
# Issueの取得（jqコマンドで日時フォーマットを日本語表記に変換）
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments --json comments | jq -r '.comments[] | "## コメント (" + (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y年%m月%d日 %H時%M分")) + ")\n\n" + .body + "\n\n---\n"' > <FILENAME>.md
```

## まとめ

Github CLIを使用してIssuesをMarkdownファイルとしてダウンロードする方法を紹介しました。特に、jqコマンドを使用した日本語表記でのダウンロード方法が、実用的で読みやすい結果を得られると感じています。

この方法により、オフライン環境でもIssuesの内容を参照でき、ドキュメント作成や記事執筆の素材としても活用できるようになります。実際に使用してみて、いくつかの改善点も見つかりましたが、基本的なニーズを満たすには十分な方法だと思います。
