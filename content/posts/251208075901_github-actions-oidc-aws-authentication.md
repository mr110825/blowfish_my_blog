+++
id = "251208075901"
date = '2025-12-08T07:59:01+09:00'
draft = false
title = 'GitHub Actions + OIDC認証でアクセスキー不要のAWS認証を実現する'
tags = ["インフラ", "AWS", "GitHub", "実践"]
+++
## 今日学んだこと

GitHub Actions + OIDC認証を使うことで、アクセスキーを一切保存せずにAWSへ安全にアクセスできることを学びました。一時的な認証情報（15分で期限切れ）を使用するため、従来のアクセスキー方式と比べてセキュリティリスクを大幅に軽減できます。

## 学習内容

### なぜOIDC認証を選ぶのか

最初は「アクセスキーをGitHubのシークレットに保存すれば簡単」と考えましたが、調べていくうちにOIDC認証の方がセキュリティ面で優れていることがわかりました。

| 観点 | アクセスキー | OIDC |
|------|-------------|------|
| 認証情報の保存 | GitHubシークレットに保存が必要 | 保存不要 |
| 有効期限 | 無期限（手動でローテーション） | 15分で自動期限切れ |
| 漏洩リスク | シークレット漏洩で永続的なアクセス | トークンは短命で再利用不可 |
| 権限の粒度 | IAMユーザー単位 | リポジトリ・ブランチ単位で制限可能 |

アクセスキーは「漏洩したら終わり」ですが、OIDCは最初から漏洩リスクがありません。AWS/GitHub公式もOIDCを推奨しています。

### OIDCの認証フロー

```
1. GitHub Actions が GitHub OIDC Provider にトークンを要求
                        ↓
2. GitHub OIDC Provider がトークンを発行（リポジトリ名、ブランチ名を含む）
                        ↓
3. AWS STS がトークンを検証し、信頼ポリシーの条件を確認
                        ↓
4. 条件を満たせば、一時認証情報を発行（15分有効）
                        ↓
5. GitHub Actions が一時認証情報でAWSリソースにアクセス
```

GitHub側でOIDCトークンが発行され、トークンには「どのリポジトリの、どのブランチから」という情報が含まれます。AWS側でその情報を検証し、条件を満たせば一時認証情報を発行します。

### 実装手順

OIDC認証の設定は「共通部分」と「デプロイ先に応じた権限設定」の2つに分かれます。

#### Step 1: 共通設定（OIDC Provider + IAMロール）

どのAWSサービスにアクセスする場合でも、この設定は共通です。

```hcl
# 1. OIDC Provider（GitHubとAWSを繋ぐ設定）
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["ffffffffffffffffffffffffffffffffffffffff"]
}

# 2. IAMロール（GitHub Actionsが引き受けるロール）
resource "aws_iam_role" "github_actions" {
  name = "github-actions-deploy-role"

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
            # リポジトリ・ブランチを制限
            "token.actions.githubusercontent.com:sub" = "repo:<OWNER>/<REPO>:ref:refs/heads/main"
          }
        }
      }
    ]
  })
}
```

**thumbprintについて**：2023年7月以降、AWSはGitHub OIDCの証明書を自動検証するようになりました。そのため、任意の値でも動作します。

#### Step 2: デプロイ先に応じた権限設定（IAMポリシー）

IAMポリシーはデプロイ先によって変わります。今回はS3 + CloudFrontへの静的サイト配信を例に説明します。

```hcl
resource "aws_iam_role_policy" "github_actions" {
  name = "github-actions-deploy-policy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::<BUCKET_NAME>",
          "arn:aws:s3:::<BUCKET_NAME>/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation"
        ]
        Resource = "arn:aws:cloudfront::<ACCOUNT_ID>:distribution/<DISTRIBUTION_ID>"
      }
    ]
  })
}
```

| 権限 | 用途 |
|------|------|
| `s3:PutObject` | ファイルアップロード |
| `s3:GetObject` | sync時の差分比較 |
| `s3:DeleteObject` | `--delete`オプション |
| `s3:ListBucket` | バケット内一覧取得 |
| `cloudfront:CreateInvalidation` | キャッシュ無効化 |

#### Step 3: GitHub Actions側の設定

```yaml
name: Deploy to AWS

on:
  push:
    branches:
      - main

permissions:
  id-token: write   # OIDCトークン取得に必須
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::<ACCOUNT_ID>:role/github-actions-deploy-role
          aws-region: ap-northeast-1

      # 以降、AWS CLIでデプロイ操作を実行
      - name: Deploy to S3
        run: aws s3 sync public/ s3://<BUCKET_NAME>/ --delete
```

`permissions: id-token: write` を付けないと、GitHub Actionsがトークンを取得できずにエラーになります。

### 設計のポイント

#### mainブランチのみに制限する理由

```hcl
"token.actions.githubusercontent.com:sub" = "repo:<OWNER>/<REPO>:ref:refs/heads/main"
```

もし `*`（ワイルドカード）にすると、任意のブランチやPRからデプロイ可能になります。悪意のあるPRがマージされる前にデプロイされるリスクを防ぐため、mainブランチのみに制限しました。

#### 最小権限の原則

IAMポリシーでは、必要なAWSサービス・リソースのみに権限を限定します。今回の例では特定のS3バケット・CloudFront Distributionのみを指定しています。

### 他のユースケースへの応用

OIDC Provider + IAMロールの信頼ポリシー（Step 1）は共通で、IAMポリシー（Step 2）を変えるだけで他のAWSサービスにも応用できます。

例えば、EC2へのデプロイであれば以下のような権限が必要になります。

```hcl
Action = [
  "ec2:DescribeInstances",
  "ssm:SendCommand",
  "ssm:GetCommandInvocation"
]
```

## まとめ

- OIDC認証はアクセスキー不要で、15分で自動期限切れのため安全
- 設定は「共通部分（OIDC Provider + IAMロール）」と「デプロイ先に応じた権限（IAMポリシー）」に分かれる
- GitHub Actions側では `permissions: id-token: write` の設定が必須
- mainブランチのみに制限して本番環境を保護する
- IAMポリシーを変えれば、S3以外のAWSサービス（EC2等）にも応用可能

## 参考

- [AWS Security Blog: Use IAM roles to connect GitHub Actions to actions in AWS](https://aws.amazon.com/blogs/security/use-iam-roles-to-connect-github-actions-to-actions-in-aws/)
- [GitHub Docs: About security hardening with OpenID Connect](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [GitHub Docs: Configuring OpenID Connect in Amazon Web Services](https://docs.github.com/ja/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)