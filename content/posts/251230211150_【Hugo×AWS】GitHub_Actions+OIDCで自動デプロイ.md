---
id: "251230211150"
title: "【Hugo×AWS】GitHub_Actions+OIDCで自動デプロイ"
date: 2025-12-30T21:11:50+09:00
draft: false
tags: []
series = ["【Hugo×AWS】Hugo+S3+CloudFrontで技術ブログを公開する"]
series_order = 2
---

## はじめに

この記事では、GitHub Actionsを使ってHugoブログをAWS（S3 + CloudFront）に自動デプロイする方法を解説します。
OIDC（OpenID Connect）認証を使用することで、アクセスキーを保存せずにセキュアなデプロイ環境を構築します。

### この記事で構築するもの

- mainブランチへのpushで自動的にS3へデプロイ
- CloudFrontのキャッシュ自動無効化
- OIDC認証による安全なAWS認証

### 想定する読者

- 前回の記事でS3 + CloudFront環境を構築済みの方
- GitHub Actionsを使ったCI/CDに興味がある方
- アクセスキーを使わない安全なデプロイ方法を知りたい方

## 完成イメージ

![GitHub_Actions+OIDCで自動デプロイ.drawio](/images/GitHub_Actions+OIDCで自動デプロイ.drawio.png)

mainブランチにpushするだけで、以下が自動実行されます。

1. Hugoでサイトをビルド
2. S3にコンテンツをアップロード
3. CloudFrontのキャッシュを無効化

デプロイ完了まで約40秒です。

## シリーズ全体像

【Hugo×AWS】シリーズ全体で5記事投稿予定です。今回の記事は2本目です。

| # | タイトル | 内容 |
|---|----------|------|
| 1 | Hugo + S3 + CloudFrontで技術ブログを公開する | Hugo環境構築〜手動デプロイまで |
| **2** | **GitHub Actions + OIDCで自動デプロイ** | **CI/CD構築、アクセスキー不要の認証** |
| 3 | CloudWatch + SNSで監視・アラート通知 | ダッシュボード、エラー率アラーム |
| 4 | Athenaでアクセスログを分析する | CloudFrontログのSQL分析 |
| 5 | 独自ドメインを設定する（Route53 + ACM） | カスタムドメイン、HTTPS |

## なぜOIDC認証を使うのか

GitHub ActionsからAWSにアクセスする方法は主に2つあります。

| 方式 | セキュリティ | 管理コスト | AWS/GitHub推奨 |
|------|------------|----------|---------------|
| **OIDC認証** | ◎ 一時認証情報、15分で期限切れ | ◎ ローテーション不要 | ✅ 推奨 |
| アクセスキー | △ 漏洩で永続的アクセスのリスク | △ 定期的なローテーション必要 | - |

### OIDC認証のメリット

- **アクセスキー不要**: GitHubシークレットにAWSの認証情報を保存しない
- **自動期限切れ**: 一時認証情報は15分で失効、漏洩しても被害が限定的
- **細かい権限制御**: リポジトリ名・ブランチ名で認証を制限可能

AWSとGitHubの公式ドキュメントでもOIDC認証が推奨されています。

## 前提条件

### 必要な環境

本記事は、前回の記事で以下が構築済みであることを前提としています。

- S3バケット（コンテンツ用）
- CloudFront Distribution
- Terraformプロジェクト

### 必要な情報

Terraformの出力値から以下を確認してください。

```bash
cd hugo-s3-demo-infra/prod
terraform output
```

```text
s3_bucket_name = "hugo-s3-demo-content-xxxxxxxx"
cloudfront_distribution_id = "E2XXXXXXXXXX"
```

## OIDC認証の仕組み

実装に入る前に、OIDC認証の仕組みを理解しておきましょう。

```
┌─────────────────┐
│  GitHub Actions │
└────────┬────────┘
         │ ① OIDCトークンを要求
         ▼
┌─────────────────┐
│  GitHub OIDC    │
│   Provider      │
└────────┬────────┘
         │ ② トークン発行
         ▼
┌─────────────────┐
│  AWS STS        │
│  (Security      │
│   Token Service)│
└────────┬────────┘
         │ ③ トークンを検証
         │ ④ IAMロールの信頼ポリシーを確認
         │ ⑤ 一時認証情報を発行
         ▼
┌─────────────────┐
│  GitHub Actions │
│  (S3/CloudFront │
│   にアクセス)    │
└─────────────────┘
```

| ステップ | 処理内容 |
|----------|----------|
| ① | GitHub ActionsがOIDCトークンを要求 |
| ② | GitHubがJWTトークンを発行（リポジトリ名、ブランチ名を含む） |
| ③ | AWS OIDC ProviderがGitHubの公開鍵でトークンを検証 |
| ④ | IAMロールの信頼ポリシーで、リポジトリ名・ブランチ名が一致するか確認 |
| ⑤ | 条件を満たせば、15分間有効な一時認証情報を発行 |

ポイントは、**AWSにアクセスキーを渡さず、GitHubが発行するトークンで認証する**ことです。

## IAMリソースの作成

### ディレクトリ構成

前回の記事で作成したTerraformプロジェクトに `iam.tf` を追加します。

```text
hugo-s3-demo-infra/
└── prod/
    ├── versions.tf
    ├── backend.tf
    ├── variables.tf
    ├── main.tf
    ├── outputs.tf
    └── iam.tf      ← 新規作成
```

### iam.tf

OIDC Provider、IAMロール、IAMポリシーを作成します。

:::details iam.tf の全体

```hcl
# ===========================================
# GitHub OIDC Provider
# ===========================================
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["ffffffffffffffffffffffffffffffffffffffff"]

  tags = {
    Name = "${var.project_name}-github-oidc"
  }
}

# ===========================================
# GitHub Actions用IAMロール
# ===========================================
resource "aws_iam_role" "github_actions" {
  name = "${var.project_name}-github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:YOUR_GITHUB_USERNAME/YOUR_REPO_NAME:ref:refs/heads/main"
          }
        }
      }
    ]
  })
}

# ===========================================
# GitHub Actions用IAMポリシー
# ===========================================
resource "aws_iam_role_policy" "github_actions" {
  name = "${var.project_name}-github-actions-policy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3Deploy"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.content.arn,
          "${aws_s3_bucket.content.arn}/*"
        ]
      },
      {
        Sid    = "CloudFrontInvalidation"
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation",
          "cloudfront:GetInvalidation"
        ]
        Resource = aws_cloudfront_distribution.main.arn
      }
    ]
  })
}
```

:::

:::message alert
`YOUR_GITHUB_USERNAME/YOUR_REPO_NAME` は、ご自身のGitHubユーザー名とリポジトリ名に置き換えてください。
:::

### コード解説

#### OIDC Provider

```hcl
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["ffffffffffffffffffffffffffffffffffffffff"]
}
```

| 属性 | 説明 |
|------|------|
| `url` | GitHubのOIDCプロバイダーURL |
| `client_id_list` | 対象のオーディエンス（AWS STSを指定） |
| `thumbprint_list` | 証明書のサムプリント（後述） |

:::details thumbprintについて

2023年7月以降、AWSはGitHub OIDCの証明書を自動検証するようになりました。
そのため、`thumbprint_list` には任意の40文字の16進数を設定しても動作します。
以前は正確なthumbprintの取得が必要でしたが、現在は省略可能です。

参考: [GitHub Actions の OIDC トークンを使用した AWS へのアクセス](https://docs.github.com/ja/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)

:::

#### IAMロールの信頼ポリシー

```hcl
assume_role_policy = jsonencode({
  # ...省略...
  Condition = {
    StringEquals = {
      "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
    }
    StringLike = {
      "token.actions.githubusercontent.com:sub" = "repo:YOUR_GITHUB_USERNAME/YOUR_REPO_NAME:ref:refs/heads/main"
    }
  }
})
```

| Condition | 意味 |
|-----------|------|
| `aud = "sts.amazonaws.com"` | AWS STSに対するトークンであることを確認 |
| `sub = "repo:xxx:ref:refs/heads/main"` | 特定のリポジトリのmainブランチからのリクエストのみ許可 |

:::message
**なぜmainブランチに限定するのか？**

`*` （ワイルドカード）にすると、任意のブランチやPull Requestからデプロイ可能になります。
悪意のあるPRがマージされる前にデプロイされるリスクがあるため、本番環境へのデプロイはmainブランチのみに制限するのがベストプラクティスです。
:::

#### IAMポリシー（最小権限設計）

```hcl
policy = jsonencode({
  Statement = [
    {
      Sid    = "S3Deploy"
      Action = [
        "s3:PutObject",    # ファイルアップロード
        "s3:GetObject",    # sync時の比較に必要
        "s3:DeleteObject", # --deleteオプション用
        "s3:ListBucket"    # バケット内一覧取得
      ]
      Resource = [
        aws_s3_bucket.content.arn,      # バケット自体
        "${aws_s3_bucket.content.arn}/*" # バケット内オブジェクト
      ]
    },
    {
      Sid    = "CloudFrontInvalidation"
      Action = [
        "cloudfront:CreateInvalidation", # キャッシュ無効化
        "cloudfront:GetInvalidation"     # 無効化ステータス確認
      ]
      Resource = aws_cloudfront_distribution.main.arn
    }
  ]
})
```

ポイントは以下の2点です。

1. **最小権限の原則**: デプロイに必要な権限のみを付与
2. **リソース制限**: 特定のS3バケット・CloudFront Distributionのみに権限を制限

### outputs.tf に追記

GitHub Actionsで使用するIAMロールのARNを出力します。

```hcl
output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
}
```

### 実行

```bash
terraform plan
terraform apply
```

出力値をメモしておいてください。

```text
github_actions_role_arn = "arn:aws:iam::123456789012:role/hugo-s3-demo-github-actions-role"
```

## GitHub Actionsの設定

### ワークフローファイルの作成

Hugoプロジェクトに `.github/workflows/deploy.yml` を作成します。

```text
hugo-s3-demo/
├── .github/
│   └── workflows/
│       └── deploy.yml  ← 新規作成
├── content/
├── themes/
└── hugo.toml
```

### deploy.yml

:::details deploy.yml の全体

```yaml
name: Deploy to AWS

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

env:
  AWS_REGION: ap-northeast-1
  S3_BUCKET: hugo-s3-demo-content-xxxxxxxx        # terraform outputの値に置き換え
  CLOUDFRONT_DISTRIBUTION_ID: E2XXXXXXXXXX        # terraform outputの値に置き換え

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: true

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
          extended: true

      - name: Build
        run: hugo --minify

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/hugo-s3-demo-github-actions-role  # terraform outputの値に置き換え
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy to S3
        run: aws s3 sync public/ s3://${{ env.S3_BUCKET }}/ --delete

      - name: Invalidate CloudFront Cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ env.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"
```

:::

:::message alert
以下の3箇所を、`terraform output` で確認した値に置き換えてください。

- `S3_BUCKET`
- `CLOUDFRONT_DISTRIBUTION_ID`
- `role-to-assume`
:::

### コード解説

#### トリガー設定

```yaml
on:
  push:
    branches:
      - main
  workflow_dispatch:
```

| 設定 | 意味 |
|------|------|
| `push: branches: - main` | mainブランチへのpush時に実行 |
| `workflow_dispatch:` | GitHub UIからの手動実行も可能にする |

#### パーミッション設定

```yaml
permissions:
  id-token: write
  contents: read
```

| 権限 | 意味 | なぜ必要か |
|------|------|-----------|
| `id-token: write` | OIDCトークンの発行を許可 | AWS認証に必須 |
| `contents: read` | リポジトリの読み取りを許可 | コードをcheckoutするため |

:::message
`id-token: write` がないとOIDC認証が失敗します。
:::

#### ステップ詳細

**1. Checkout**

```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:
    submodules: true
```

- リポジトリのコードを取得
- `submodules: true` でHugoテーマ（gitサブモジュール）も取得

**2. Setup Hugo**

```yaml
- name: Setup Hugo
  uses: peaceiris/actions-hugo@v3
  with:
    hugo-version: 'latest'
    extended: true
```

- Hugo extended版をインストール
- `extended: true` でSCSS対応版を使用

**3. Build**

```yaml
- name: Build
  run: hugo --minify
```

- `--minify` でHTML/CSS/JSを圧縮
- `public/` ディレクトリに静的ファイルが生成される

**4. Configure AWS Credentials**

```yaml
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/hugo-s3-demo-github-actions-role
    aws-region: ${{ env.AWS_REGION }}
```

- AWS公式のアクション
- OIDCトークンを使ってIAMロールを引き受ける
- **アクセスキーは不要**

**5. Deploy to S3**

```yaml
- name: Deploy to S3
  run: aws s3 sync public/ s3://${{ env.S3_BUCKET }}/ --delete
```

- `sync` で差分のみ転送（効率的）
- `--delete` でローカルにないファイルをS3から削除

**6. Invalidate CloudFront Cache**

```yaml
- name: Invalidate CloudFront Cache
  run: |
    aws cloudfront create-invalidation \
      --distribution-id ${{ env.CLOUDFRONT_DISTRIBUTION_ID }} \
      --paths "/*"
```

- CloudFrontのエッジキャッシュを無効化
- `/*` で全パスを対象

:::message
キャッシュ無効化は月1,000パスまで無料です。
`/*` で全ファイルを無効化すると1パスとしてカウントされます。
:::

## 動作確認

### 1. ワークフローをコミット・プッシュ

```bash
cd hugo-s3-demo
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Actions workflow for deployment"
git push origin main
```

### 2. GitHub Actionsの実行を確認

GitHubリポジトリの「Actions」タブで、ワークフローの実行状況を確認します。

確認ポイント：

- [ ] 全ステップが緑色（成功）になっている
- [ ] 実行時間が1分以内

### 3. サイトの更新を確認

記事を編集してpushし、自動デプロイを確認します。

```bash
# 記事を編集
vim content/posts/first-post.md

# コミット・プッシュ
git add .
git commit -m "Update first post"
git push origin main
```

ブラウザでサイトにアクセスし、変更が反映されていることを確認します。

## セキュリティのポイント

本記事で構築した環境のセキュリティポイントをまとめます。

### 1. OIDC認証

| 観点 | 従来方式（アクセスキー） | 本記事の方式（OIDC） |
|------|-------------------------|---------------------|
| 認証情報の保存 | GitHubシークレットに保存が必要 | 保存不要 |
| 有効期限 | 無期限（手動ローテーション） | 15分（自動期限切れ） |
| 漏洩リスク | 高（永続的なアクセス） | 低（短命で再利用不可） |

### 2. ブランチ制限

```hcl
"token.actions.githubusercontent.com:sub" = "repo:xxx/xxx:ref:refs/heads/main"
```

mainブランチからのリクエストのみを許可し、不正なデプロイを防止しています。

### 3. 最小権限のIAMポリシー

デプロイに必要な最小限の権限のみを付与し、特定のリソースのみに制限しています。

| 権限 | 用途 |
|------|------|
| `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`, `s3:ListBucket` | S3へのコンテンツデプロイ |
| `cloudfront:CreateInvalidation`, `cloudfront:GetInvalidation` | キャッシュ無効化 |

## トラブルシューティング

### OIDC認証が失敗する

**症状**: `Error: Could not assume role with OIDC` などのエラー

**確認ポイント**:

1. **IAMロールの信頼ポリシー**
   - リポジトリ名が正確か（`repo:username/repo-name` の形式）
   - ブランチ名が一致しているか（`refs/heads/main`）

2. **GitHub Actionsのパーミッション**
   - `permissions: id-token: write` が設定されているか

3. **AWS OIDC Provider**
   - `url` が `https://token.actions.githubusercontent.com` になっているか

### デプロイは成功したが反映されない

**症状**: GitHub Actionsは成功しているが、サイトに変更が反映されない

**確認ポイント**:

1. **CloudFrontキャッシュ**
   - AWS ConsoleでInvalidationの状態を確認（Completedになっているか）

2. **ブラウザキャッシュ**
   - シークレットウィンドウで確認、またはキャッシュをクリア

3. **S3バケット**
   - AWS Consoleで、正しくファイルがアップロードされているか確認

### S3へのアクセスが拒否される

**症状**: `Access Denied` エラー

**確認ポイント**:

1. **IAMポリシーのリソース**
   - S3バケット名が正しいか
   - `arn:aws:s3:::bucket-name` と `arn:aws:s3:::bucket-name/*` の両方が指定されているか

2. **S3バケットの権限**
   - バケットポリシーでIAMロールからのアクセスがブロックされていないか

## まとめ

本記事では、以下を構築しました。

- **GitHub Actions**: mainブランチへのpushで自動デプロイ
- **OIDC認証**: アクセスキー不要の安全な認証
- **IAMロール/ポリシー**: 最小権限の原則に基づいた設計

### 作成したリソース

| リソース | 用途 |
|----------|------|
| OIDC Provider | GitHubとAWSの信頼関係を構築 |
| IAM Role | GitHub Actionsが引き受けるロール |
| IAM Policy | S3デプロイ、CloudFrontキャッシュ無効化の権限 |

### デプロイフロー

```
git push (main)
    ↓
GitHub Actions起動
    ↓
Hugo Build (約10秒)
    ↓
OIDC認証 → IAMロール引き受け
    ↓
S3 Sync (差分のみ)
    ↓
CloudFront Cache Invalidation
    ↓
デプロイ完了 (合計約40秒)
```

## 参考資料

- [GitHub Actions OIDC + AWS](https://docs.github.com/ja/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [AWS IAM OIDC Provider](https://docs.aws.amazon.com/ja_jp/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [peaceiris/actions-hugo](https://github.com/peaceiris/actions-hugo)
- [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)
- [Terraform aws_iam_openid_connect_provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_openid_connect_provider)
