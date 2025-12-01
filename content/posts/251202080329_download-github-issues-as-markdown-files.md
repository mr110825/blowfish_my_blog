+++
id = "251202080329"
date = '2025-12-02T08:03:29+09:00'
draft = false
title = 'Github-CLIでIssuesをMarkdownファイルとしてダウンロードする方法'
tags = ["ツール", "Git", "GitHub", "実践", "ハンズオン・チュートリアル"]
+++
## 今日学んだこと

以前、[Zennに投稿した記事](https://zenn.dev/mr110825/articles/098b062d6c0574)を修正してTILとして投稿します。

GitHub CLIの `gh issue view` コマンドを使うと、IssuesをMarkdownファイルとしてダウンロードできます。さらに `jq` コマンドと組み合わせることで、日時フォーマットを日本語表記に変換し、読みやすい形式で出力できることを学びました。

## 学習内容

### 背景と対象読者

GitHubのプライベートリポジトリでIssuesを作業メモとして活用していましたが、書き溜めた内容をコピー&ペーストで取り出す方法しかなく、効率的に活用できていませんでした。この問題を解決するため、IssuesをMarkdownファイルとしてダウンロードする方法を調べました。

**対象読者：**

- GitHub CLIの基本的な使い方を知っている方
- ドキュメント作成や記事執筆の素材としてIssuesを活用したい方

**前提条件：**

- Linux（Ubuntu）環境（WSL2含む）
- 対象リポジトリへのアクセス権限を保有している

> パブリックリポジトリまたは有料プランユーザーの場合は、GitHub Wiki機能など互換性のある機能があるため、そちらを利用するほうが手順も簡単で効率的です。

### Step 1: 環境セットアップ

#### GitHub CLIのインストール

```bash
# インストール状況の確認
gh --version

# GitHub CLIのインストール（必要な場合）
sudo apt install gh
```

#### GitHub CLIへのログイン

```bash
# ログイン状況の確認
gh auth status

# GitHub CLIへログイン実行
gh auth login
```

### Step 2: Issues一覧の確認

```bash
gh issue list --repo <OWNER/REPO>
```

**実行例：**

```bash
gh issue list --repo mr110825/github-issues-to-markdown
```

**出力例：**

```bash
ID  TITLE               LABELS  UPDATED         
#1  サンプル用のIssues          about 1 hour ago
```

### Step 3: Issueの取得（4つの方法）

方法2・3は `--json comments` を指定しているため、コメントのみが出力されます。Issue本文も含めたい場合は方法4を使用してください。

#### 方法1: シンプルな取得

```bash
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments > <FILENAME>.md
```

**出力例：**

```markdown
author:	mr110825
association:	owner
edited:	true
status:	none
--
記事を投稿するので構成をまとめる
--
```

この方法は最もシンプルですが、メタデータが多く含まれ、内容が読みにくくなります。

#### 方法2: コメントのみ取得（ISO形式）

```bash
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments --json comments --template '{{range .comments}}## コメント ({{.createdAt}})

{{.body}}

---
{{end}}' > <FILENAME>.md
```

**出力例：**

```markdown
## コメント (2025-06-28T12:24:28Z)

記事を投稿するので構成をまとめる

---
```

メタデータが除去され、コメントの内容と投稿日時が明確に表示されます。ただし、ISO形式の日時表記は読みづらいです。

#### 方法3: 日本語表記で取得（推奨）

```bash
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --comments --json comments | jq -r '.comments[] | "## コメント (" + (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y年%m月%d日 %H時%M分")) + ")\n\n" + .body + "\n\n---\n"' > <FILENAME>.md
```

`jq` コマンドが必要です：

```bash
sudo apt install jq
```

**出力例：**

```markdown
## コメント (2025年06月28日 12時24分)

記事を投稿するので構成をまとめる

---
```

日本語表記により日時が直感的に理解でき、最も実用的な方法です。

> **注意:** 出力される日時はUTC（協定世界時）です。日本時間（JST）に変換したい場合は、`date`コマンドとの組み合わせや、`jq`内で9時間加算する処理が必要です。

#### 方法4: Issue本文とコメントを取得（推奨）

```bash
gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO> --json title,body,comments | jq -r '
  "# " + .title + "\n\n" + .body + "\n\n---\n\n" +
  ([.comments[] | "## コメント (" + (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y年%m月%d日 %H時%M分")) + ")\n\n" + .body] | join("\n\n---\n\n"))
' > <FILENAME>.md
```

**出力例：**

```markdown
# サンプル用のIssues

これはサンプルのIssueです。

---

## コメント (2025年06月28日 12時24分)

記事を投稿するので構成をまとめる

---

## コメント (2025年06月28日 12時25分)

必要な手順

- [x] 文章企画を構成
- [x] サンプルのリポジトリを作成
- [x] 記事作成
- [x] 記事投稿
```

Issue本文（タイトル・概要）とコメントの両方を取得できるため、Issueの全体像を把握したい場合に最適です。

## まとめ

| 方法 | 特徴 | 推奨度 |
|------|------|--------|
| 方法1（シンプル） | メタデータが多く読みにくい | △ |
| 方法2（ISO形式） | コメントのみ抽出、日時が読みにくい | ○ |
| 方法3（日本語表記） | コメントのみ、読みやすく実用的 | ○ |
| 方法4（本文+コメント） | Issue全体を取得、最も実用的 | ◎ |

- `gh issue view` コマンドでIssuesをMarkdownとして取得できる
- `--json` オプションで `comments` のみ、または `title,body,comments` を指定して出力内容を制御可能
- `jq` コマンドを使えば日時フォーマットを日本語表記に変換できる
- オフライン環境でもIssuesの内容を参照でき、ドキュメント作成の素材として活用できる

## 参考

- [GitHub CLI クイックスタート](https://docs.github.com/ja/github-cli/github-cli/quickstart)
- [【Git のセットアップ】GitHub CLI を使って GitHub に接続する](https://zenn.dev/babyjob/articles/3faf85c33b8725)