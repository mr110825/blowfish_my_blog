+++
id = "1754153716"
date = '2025-08-03T01:55:16+09:00'
draft = false
title = 'Github CLIでIssuesをMarkdownファイルとしてダウンロードする方法'
tags = ["Git", "GitHub", "GitHub CLI"]
+++
## はじめに

**GitHub CLI**を使用してGitHubのIssuesをMarkdownファイルとして効率的にダウンロードする方法を解説します。この記事では、基本的な取得から実用的なフォーマット改善まで、段階的にアプローチする方法を紹介します。

### 解決する課題
- GitHubのIssuesを手動でコピー&ペーストする非効率性
- プライベートリポジトリの作業メモやアイデアの効果的な活用不足
- ローカル環境でのIssues管理と再利用の困難さ

### この記事で学べること
- GitHub CLIを使ったIssuesの効率的な取得方法
- jqコマンドによる日時フォーマットの改善手法
- 複数Issuesの一括処理とワークフロー自動化

### 対象読者
- GitHub CLIの基本的な使い方を知っている方
- プライベートリポジトリでIssuesを活用している方
- ドキュメント作成や記事執筆の素材としてIssuesを活用したい方

**最適解コマンド（日本語日時フォーマット）:**
```bash
# Issueの取得（jqコマンドで日時フォーマットを日本語表記に変換）
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments --json comments | jq -r '.comments[] | "## コメント (" + (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y年%m月%d日 %H時%M分")) + ")\n\n" + .body + "\n\n---\n"' > <FILENAME>.md
```

{{< alert icon="lightbulb" cardColor="#d9ff00be" iconColor="#1d3557" textColor="#000000ff" >}}
Isseusを取得する対象としてはプライベートリポジトリかつ、Githubの無料プランを利用しているユーザーを想定しております。<br>
パブリックリポジトリまたは有料プランユーザーの場合は、Github Wiki機能など互換性のある機能があるため、そちらを利用するほうが手順も簡単で、効率的にドキュメント運用できると考えられます。
{{< /alert >}}

**前提条件**

- **OS**: Linux（Ubuntu）環境（WSL2含む）
- **権限**: GitHubにて対象リポジトリへのアクセス権限を保有している
- **サンプル**: 当記事では[サンプルリポジトリ（mr110825/gemini-cli-test-repo）](https://github.com/mr110825/gemini-cli-test-repo/issues/1)を例として説明します

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

GitHub CLIへのログイン手順の詳細については、以下の記事をご参照ください。
- [【Git のセットアップ】GitHub CLI を使って GitHub に接続する](https://zenn.dev/babyjob/articles/3faf85c33b8725)
- [GitHub CLIのクイックスタート](https://docs.github.com/ja/enterprise-cloud@latest/github-cli/github-cli/quickstart)


## ハンズオン

### Step 1: 基本的なIssues一覧確認

まず、対象リポジトリのIssues一覧を確認します：

```bash
gh issue list --repo <OWNER/REPO>
```

**実行例:**
```bash
# サンプルリポジトリのIssues確認
gh issue list --repo mr110825/gemini-cli-test-repo
```

**出力例:**
```bash
ID  TITLE               LABELS  UPDATED         
#1  サンプル用のIssues          about 1 hour ago
```

### Step 2: 基本的なIssue取得

最もシンプルな方法でIssueを取得します：

```bash
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments > <FILENAME>.md
```

**実行例:**
```bash
# Issues#1を「test1.md」として取得
gh issue view 1 --repo mr110825/gemini-cli-test-repo --comments > test1.md
```

**出力例:**

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

{{< alert icon="lightbulb" cardColor="#d9ff00be" iconColor="#1d3557" textColor="#000000ff" >}}
**課題**: この方法は最もシンプルですが、多くのメタデータが含まれており読みにくく、コメントのタイミングが分かりづらい問題があります。
{{< /alert >}}

### Step 3: メタデータ除去とISO形式での取得

不要なプロパティを除外し、コメントのみを整形して取得します：

```bash
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments --json comments --template '{{range .comments}}## コメント ({{.createdAt}})

{{.body}}

---
{{end}}' > <FILENAME>.md
```

**実行例:**
```bash
# 整形されたコメントを「test2.md」として取得
gh issue view 1 --repo mr110825/gemini-cli-test-repo --comments --json comments --template '{{range .comments}}## コメント ({{.createdAt}})

{{.body}}

---
{{end}}' > test2.md
```

**出力例:**

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

{{< alert icon="lightbulb" cardColor="#d9ff00be" iconColor="#1d3557" textColor="#000000ff" >}}
**改善点**: メタデータが除去され、コメントの内容と投稿日時が明確になりました。しかし、ISO形式の日時表記は読みづらいため、さらなる改善が必要です。
{{< /alert >}}

### Step 4: jqコマンドによる日時フォーマット改善（推奨）

jqコマンドを使用して、日時を日本語表記に変換します：

```bash
# jqコマンドのインストール（必要な場合）
sudo apt install jq
```

```bash
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments --json comments | jq -r '.comments[] | "## コメント (" + (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y年%m月%d日 %H時%M分")) + ")\n\n" + .body + "\n\n---\n"' > <FILENAME>.md
```

**実行例:**
```bash
# 日本語日時形式で「test3.md」として取得
gh issue view 1 --repo mr110825/gemini-cli-test-repo --comments --json comments | jq -r '.comments[] | "## コメント (" + (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y年%m月%d日 %H時%M分")) + ")\n\n" + .body + "\n\n---\n"' > test3.md
```

**出力例:**
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

{{< alert icon="lightbulb" cardColor="#d9ff00be" iconColor="#1d3557" textColor="#000000ff" >}}
**最適解**: この方法が最も実用的です。日本語表記により日時が直感的に理解でき、ドキュメントとして保存した際も読みやすくなります。
{{< /alert >}}

### Step 5: Issueタイトル・本文・コメントの完全取得

Issueの全情報を取得したい場合の完全版コマンド：

```bash
# Issueのタイトル、本文、コメントを完全取得
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments --json title,body,comments | jq -r '"# " + .title + "\n\n" + "## Issue本文\n\n" + .body + "\n\n---", (.comments[] | "## コメント (" + (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y年%m月%d日 %H時%M分")) + ")\n\n" + .body + "\n\n---")' > <FILENAME>.md
```

これにより、Issueのタイトル、本文、整形されたコメントが順番に出力されるMarkdownファイルが生成されます。

## 応用パターン

### 複数Issues の一括取得

```bash
# 全Issuesを一括でMarkdown化
for issue in $(gh issue list --repo <OWNER/REPO> --json number -q '.[].number'); do
  gh issue view $issue --repo <OWNER/REPO> --comments --json title,body,comments | jq -r '"# " + .title + "\n\n" + "## Issue本文\n\n" + .body + "\n\n---", (.comments[] | "## コメント (" + (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y年%m月%d日 %H時%M分")) + ")\n\n" + .body + "\n\n---")' > "issue-${issue}.md"
done
```

### 特定ラベルのIssues取得

```bash
# 特定ラベル（例：documentation）のIssuesのみ取得
gh issue list --repo <OWNER/REPO> --label "documentation" --json number -q '.[].number'
```

## トラブルシューティング

### よくある問題と解決法

**問題1: GitHub CLI認証エラー**
```bash
# エラー例: "authentication required"
# 解決法: 再認証の実行
gh auth login
```

**問題2: jqコマンドが見つからない**
```bash
# Ubuntu/Debian系
sudo apt install jq

# CentOS/RHEL系
sudo yum install jq

# macOS
brew install jq
```

**問題3: 日時フォーマットエラー**
```bash
# strptime/strftimeが動作しない場合は、シンプルな置換を使用
gh issue view 1 --repo <OWNER/REPO> --comments --json comments | jq -r '.comments[] | "## コメント (" + .createdAt + ")\n\n" + .body + "\n\n---\n"'
```

**問題4: プライベートリポジトリへのアクセス権限不足**
```bash
# 権限スコープの確認
gh auth status

# 必要に応じて追加スコープで再認証
gh auth login --scopes "repo"
```

## コマンドリファレンス

```bash
# 基本操作
gh issue list --repo <OWNER/REPO>                    # Issues一覧表示
gh issue view <NUMBER> --repo <OWNER/REPO>           # 基本的なIssue表示
gh auth status                                       # 認証状況確認
gh auth login                                        # GitHub認証

# メタデータ付き取得
gh issue view <NUMBER> --repo <OWNER/REPO> --comments > <FILE>.md

# JSON形式での取得
gh issue view <NUMBER> --repo <OWNER/REPO> --json title,body,comments

# テンプレート使用（ISO日時）
gh issue view <NUMBER> --repo <OWNER/REPO> --comments --json comments --template '{{range .comments}}## コメント ({{.createdAt}})\n\n{{.body}}\n\n---\n{{end}}'

# jq使用（日本語日時・推奨）
gh issue view <NUMBER> --repo <OWNER/REPO> --comments --json comments | jq -r '.comments[] | "## コメント (" + (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y年%m月%d日 %H時%M分")) + ")\n\n" + .body + "\n\n---\n"'

# 完全版（タイトル・本文・コメント）
gh issue view <NUMBER> --repo <OWNER/REPO> --comments --json title,body,comments | jq -r '"# " + .title + "\n\n" + "## Issue本文\n\n" + .body + "\n\n---", (.comments[] | "## コメント (" + (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y年%m月%d日 %H時%M分")) + ")\n\n" + .body + "\n\n---")'

# 一括処理
for issue in $(gh issue list --repo <OWNER/REPO> --json number -q '.[].number'); do
  gh issue view $issue --repo <OWNER/REPO> --comments --json title,body,comments | jq -r '"# " + .title + "\n\n" + .body + "\n\n---"' > "issue-${issue}.md"
done

# 特定ラベルでフィルタ
gh issue list --repo <OWNER/REPO> --label "<LABEL_NAME>"
```

## まとめ

GitHub CLIを使用してIssuesをMarkdownファイルとしてダウンロードする方法を段階的改善アプローチで解説しました。

### 主要ポイント
- **段階的改善**: 基本的な取得から最適化まで5段階のアプローチ
- **実用的な解決策**: jqコマンドを使った日本語日時フォーマットが最適解
- **柔軟な活用**: 単発取得から一括処理まで様々なパターンに対応

### 推奨ワークフロー
1. **基本取得**: まずシンプルな方法でデータを確認
2. **フォーマット改善**: jqコマンドで読みやすい形式に変換
3. **自動化**: 複数Issuesや定期取得の仕組み構築
4. **統合活用**: 既存のドキュメント管理システムとの連携

GitHub CLIとjqコマンドの組み合わせにより、GitHubのデータを効率的にローカル環境で活用する基盤が整います。

## 参考リンク

- [GitHub CLI公式ドキュメント](https://docs.github.com/ja/github-cli)
- [GitHub CLIクイックスタート](https://docs.github.com/ja/github-cli/github-cli/quickstart)
- [jq公式ドキュメント](https://jqlang.github.io/jq/)
- [GitHub API v4ドキュメント](https://docs.github.com/ja/graphql)
