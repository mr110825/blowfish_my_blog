---
id: "251230210947"
title: "【Hugo×AWS】Hugo+S3+CloudFrontで技術ブログを公開する"
date: 2025-12-30T21:09:47+09:00
draft: false
tags: ["学習・作業ログ", "AWS", "Terraform", "Hugo"]
series: [Hugo-S3-CloudFrontで技術ブログを公開する]
series_order: 1
---

## はじめに

この記事では、Hugoで作成した静的サイトをAWS（S3 + CloudFront）でホスティングする方法を解説します。
Terraformを使ってインフラをコード化し、手動デプロイまでを行います。

### 想定する読者

- AWSを使って静的サイトをホスティングしたい方
- Terraformでインフラをコード化したい方
- AWS初心者〜中級者

#### Terraformを初めて使う方へ

本記事ではTerraformの基本的な使い方（`terraform init/plan/apply`の意味、HCL構文等）は省略しています。初めての方は[HashiCorp公式チュートリアル](https://developer.hashicorp.com/terraform/tutorials/aws-get-started)を先に確認することをお勧めします。

## 完成イメージ

![S3+CloudFront構成図](/img/S3+CloudFront構成図_はじめ.drawio.png)

- 本記事の完了後、CloudFrontのデフォルトドメイン（`https://dxxxxx.cloudfront.net`）でブログにアクセスできるようになります。
- CloudFrontからS3へのアクセスにはOAC（Origin Access Control）を使用し、S3バケットへの直接アクセスを禁止します。

## シリーズ全体像

【Hugo×AWS】シリーズ全体で5記事投稿予定です。今回の記事は1本目です。

| # | タイトル | 内容 |
|---|----------|------|
| **1** | **Hugo + S3 + CloudFrontで技術ブログを公開する** | **Hugo環境構築〜手動デプロイまで** |
| 2 | GitHub Actions + OIDCで自動デプロイ | CI/CD構築、アクセスキー不要の認証 |
| 3 | CloudWatch + SNSで監視・アラート通知 | ダッシュボード、エラー率アラーム |
| 4 | Athenaでアクセスログを分析する | CloudFrontログのSQL分析 |
| 5 | 独自ドメインを設定する（Route53 + ACM） | カスタムドメイン、HTTPS |

## なぜS3 + CloudFrontで構築するのか

静的サイトのホスティング方法として、以下を比較検討しました。

| 選択肢 | コスト（月額） | 管理負担 | IaC化 |
|--------|---------------|---------|-------|
| **S3 + CloudFront** | 100〜170円 ※1| なし | ◎ |
| EC2 + Nginx | 1,500円〜 | OS管理必要 | ○ |
| Lightsail | 500円〜 | OS管理必要 | △ |
| Amplify Hosting | 無料枠あり | なし | × |

※1 個人ブログ規模の予想値となります。おおよそのコスト感としてとらえてください。

### S3 + CloudFrontを選んだ理由

- **コスト効率**：静的サイトに最適、月額100円台
- **運用負担ゼロ**：サーバーレスでOS管理不要
- **Terraform対応**：全リソースをコードで管理可能
- **高可用性**：S3のSLA 99.99%
- **高速配信**：CloudFrontのエッジキャッシュ
- **セキュリティ**：OAC（Origin Access Control）でS3への直接アクセスを禁止

EC2/Lightsailは静的サイトにはオーバースペックで、Amplifyは便利だがTerraformで管理できないため見送りました。

## 前提条件

### 構築環境

本記事は以下の環境で構築しています。

- OS: Ubuntu 24.04（Docker）
- Hugo: v0.152.2 extended
- Terraform: v1.14.2
- AWS CLI: v2.32.16

### 必要なツール

以下のツールがインストールされていることを確認してください。

| ツール | バージョン | 公式ドキュメント |
|--------|-----------|-----------------|
| AWS CLI | v2 | [インストールガイド](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) |
| Terraform | 1.0以上 | [インストールガイド](https://developer.hashicorp.com/terraform/install) |
| Git | - | [インストールガイド](https://git-scm.com/book/ja/v2/使い始める-Gitのインストール) |
| Hugo | - | [インストールガイド](https://gohugo.io/installation/) |

AWSアカウントが必要です。ルートユーザーではなく、IAMユーザーでの操作を推奨します。

:::details 参考用：自分が実際に実行したコマンド

#### AWS CLI

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

#### Terraform

```bash
sudo apt-get update && sudo apt-get install -y gnupg lsb-release
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install -y terraform
```

#### Hugo

```bash
# 最新バージョンを確認
curl -s https://api.github.com/repos/gohugoio/hugo/releases/latest | grep "tag_name"

# extended版をダウンロード・インストール
wget https://github.com/gohugoio/hugo/releases/download/v0.152.2/hugo_extended_0.152.2_linux-amd64.deb
sudo dpkg -i hugo_extended_0.152.2_linux-amd64.deb
```

#### Git

最初からインストール済みのため対応不要でした。

:::

AWS CLIの認証情報を設定していない場合は、以下のコマンドで設定してください。

```bash
aws configure
```

プロンプトに従って入力します。

```text
AWS Access Key ID [None]: {IAMユーザーのアクセスキーを入力}
AWS Secret Access Key [None]: {IAMユーザーのシークレットアクセスキーを入力}
Default region name [None]: ap-northeast-1
Default output format [None]: json
```

### 確認コマンド

```bash
aws --version
terraform --version
git --version
hugo version
aws sts get-caller-identity  # AWS認証情報の確認
```

## Hugoセットアップ

### 作業ディレクトリ構成

本記事では以下のディレクトリ構成で作業します。

```text
作業ディレクトリ/
├── hugo-s3-demo/           # Hugoプロジェクト
└── hugo-s3-demo-infra/     # Terraformプロジェクト
    ├── backend-setup/
    └── prod/
```

### サイト作成

```bash
hugo new site hugo-s3-demo
cd hugo-s3-demo
```

### テーマ追加

Anankeテーマ（Hugo公式チュートリアルでも採用）を追加します。
git submoduleを使うことで、テーマの更新管理が容易になります。

```bash
git init
git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke
```

### hugo.toml編集

`hugo.toml` を編集してテーマを有効化します。

```toml
baseURL = 'https://example.org/'
languageCode = 'en-us'
title = 'Hugo S3 Demo'
theme = 'ananke'
```

`baseURL` は後でCloudFrontのドメインに変更します。

### 最初の記事作成

```bash
hugo new content posts/first-post.md
```

作成されたファイルを編集し、`draft = false` に変更して公開状態にします。

```toml
+++
date = '2025-12-14T14:59:51Z'
draft = false
title = 'First Post'
+++

これは最初の投稿です。
```

### ビルド確認

```bash
# Hugoでビルド実行
hugo

# `public/` ディレクトリにHTMLファイルが生成されていればOK
ls public/
# 404.html  ananke  categories  images  index.html  index.xml  posts  sitemap.xml  tags
```

### ローカルでプレビューしたい場合

```bash
hugo server
```

`http://localhost:1313/` でプレビューできます。Ctrl+C で停止します。

## Terraform state管理の準備

### Terraformとは

**TerraformはHashiCorpが開発したInfrastructure as Code（IaC）ツール**です。
Go言語で実装されたOSSで、AWS・Azure・GCPなどのクラウドインフラをコードとして記述・管理できます。

本記事では、TerraformでS3バケットやCloudFrontディストリビューションを定義して、AWS環境を構築します。

### Terraformを使うメリット

1. **宣言的な記述** - 「こうなってほしい」状態を書くだけで構築できる
2. **スピードと安全性** - デプロイの自動化で高速かつ繰り返し実行可能
3. **ドキュメント化** - コード自体がインフラ構成のドキュメントになる
4. **バージョン管理** - Gitでインフラの変更履歴を追跡できる
5. **再利用性** - 実績あるコードを再利用できる

### VSCode拡張機能（推奨）

Terraformのコードを書く際は、VSCode拡張機能「**HashiCorp Terraform**」のインストールを推奨します。シンタックスハイライト、自動補完、フォーマットなどが利用できます。
[マーケットプレイスへのリンク](https://marketplace.visualstudio.com/items?itemName=HashiCorp.terraform)

### なぜ先にstate管理環境を作るのか

Terraformはインフラの状態を「tfstate」というファイルで管理します。
このファイルをS3に保存し、チームで共有・ロック管理します。
tfstateによってTerraformのステータスなどを管理するので、
本体のインフラ環境とは別ディレクトリで先に作成します

- tfstateを保存するS3バケットが必要
  - そのS3バケットをTerraformで作りたい
    - でもTerraform実行前にbackend（S3）が存在している必要がある
      →　**最初にtfstate管理環境を構築する**

### ディレクトリ構成

```bash
hugo-s3-demo-infra/
└── backend-setup/
    └── main.tf
```

`backend-setup/` でtfstate管理用のリソースを作成します。

```bash
mkdir -p hugo-s3-demo-infra/backend-setup
cd hugo-s3-demo-infra/backend-setup
```

### backend-setup/main.tf

:::details 以下がmain.tfの全体となります。

```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "tfstate" {
  bucket = "hugo-s3-demo-tfstate-${random_id.suffix.hex}"
}

resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "tfstate" {
  bucket                  = aws_s3_bucket.tfstate.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "tfstate_lock" {
  name         = "hugo-s3-demo-tfstate-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

output "s3_bucket_name" {
  value = aws_s3_bucket.tfstate.bucket
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.tfstate_lock.name
}
```

:::

### コード解説

#### terraform / provider ブロック

```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    # AWSリソースを作成するためのプロバイダー
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    # ランダム文字列を生成するためのプロバイダー
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"  # 東京リージョン
}
```

- `terraform` ブロック：Terraformのバージョンと使用するプロバイダーを指定
- `provider` ブロック：AWSリージョンを東京（ap-northeast-1）に設定

#### random_id

```hcl
# S3バケット名の一意性を確保するためのランダム文字列
resource "random_id" "suffix" {
  byte_length = 4  # 8文字の16進数を生成
}
```

S3バケット名はグローバルで一意である必要があります。
`random_id` でランダムな文字列を生成し、バケット名の末尾に付与します。

#### S3バケット

```hcl
# tfstate保存用バケット
resource "aws_s3_bucket" "tfstate" {
  bucket = "hugo-s3-demo-tfstate-${random_id.suffix.hex}"
}

# バージョニング有効化（誤操作時に復元可能）
resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

# サーバーサイド暗号化（tfstateには機密情報が含まれる可能性がある）
resource "aws_s3_bucket_server_side_encryption_configuration" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# パブリックアクセスを完全ブロック
resource "aws_s3_bucket_public_access_block" "tfstate" {
  bucket                  = aws_s3_bucket.tfstate.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

| リソース | 役割 |
|----------|------|
| `aws_s3_bucket` | tfstate保存用バケット |
| `aws_s3_bucket_versioning` | バージョニング有効化（誤操作時に復元可能） |
| `aws_s3_bucket_server_side_encryption_configuration` | 暗号化（tfstateには機密情報が含まれる可能性がある） |
| `aws_s3_bucket_public_access_block` | パブリックアクセスを完全ブロック |

#### DynamoDB

```hcl
# tfstateロック用テーブル（同時実行を防止）
resource "aws_dynamodb_table" "tfstate_lock" {
  name         = "hugo-s3-demo-tfstate-lock"
  billing_mode = "PAY_PER_REQUEST"  # 使った分だけ課金
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"  # 文字列型
  }
}
```

tfstateのロック管理用テーブルです。
複数人が同時に `terraform apply` を実行した際の競合を防ぎます。

#### outputs

```hcl
# 作成されたリソース名を出力（次のセクションで使用）
output "s3_bucket_name" {
  value = aws_s3_bucket.tfstate.bucket
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.tfstate_lock.name
}
```

作成されたリソース名を出力します。次のセクションでbackend設定に使用します。

### 実行

`main.tf` を作成したら実行します。

#### terraform init

```bash
terraform init
```

プロバイダー（AWS、random）がダウンロードされます。

```text
Initializing the backend...
Initializing provider plugins...
- Installing hashicorp/aws v5.x.x...
- Installing hashicorp/random v3.x.x...

Terraform has been successfully initialized!
```

#### terraform plan

```bash
terraform plan
```

実行計画を確認します。実際のリソースは作成されません。

```text
Plan: 6 to add, 0 to change, 0 to destroy.
```

6つのリソースが作成される予定であることを確認できます。

#### terraform apply

```bash
terraform apply
```

`Enter a value:` と表示されたら `yes` と入力します。

```text
Apply complete! Resources: 6 added, 0 changed, 0 destroyed.

Outputs:

dynamodb_table_name = "hugo-s3-demo-tfstate-lock"
s3_bucket_name = "hugo-s3-demo-tfstate-xxxxxxxx"
```

:::message
**出力値をメモしてください**
`s3_bucket_name` と `dynamodb_table_name` は次のセクションで使用します。
:::

### よく使うTerraformコマンド

本セクションで使用したコマンドをまとめます。

| コマンド | 説明 |
|----------|------|
| `terraform init` | 初期化（プロバイダーのダウンロード） |
| `terraform fmt` | コードのフォーマット整形 |
| `terraform validate` | 構文チェック |
| `terraform plan` | 実行計画の確認（実際には変更しない） |
| `terraform apply` | インフラの構築・変更 |
| `terraform destroy` | インフラの削除 |

基本的な流れは `init` → `plan` → `apply` です。

`fmt`、`validate`、`plan` は以下のように一気に実行できます。

```bash
terraform fmt && terraform validate && terraform plan
```

## Terraform基盤構築

前のセクションでtfstate管理用のS3とDynamoDBを作成しました。
このセクションでは、実際にブログをホスティングするためのS3バケットとCloudFrontを構築します。

### ディレクトリ構成

```bash
hugo-s3-demo-infra/
├── backend-setup/
│   └── main.tf          # tfstate用（作成済み）
└── prod/
    ├── versions.tf      # Terraform + Provider設定
    ├── backend.tf       # S3 backend設定
    ├── variables.tf     # 変数定義
    ├── main.tf          # S3, OAC, CloudFront
    └── outputs.tf       # 出力値
```

`prod/` ディレクトリを作成します。

```bash
mkdir -p ../prod
cd ../prod
```

### versions.tf

Terraformのバージョンとプロバイダーを設定します。

```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"
}
```

### backend.tf

tfstateをS3で管理するための設定です。
**前のセクションで出力された値を使用してください。**

```hcl
terraform {
  backend "s3" {
    bucket         = "hugo-s3-demo-tfstate-xxxxxxxx"  # 出力されたs3_bucket_name
    key            = "prod/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "hugo-s3-demo-tfstate-lock"      # 出力されたdynamodb_table_name
    encrypt        = true
  }
}
```

:::message alert
`bucket` の値は、前のセクションで出力された `s3_bucket_name` に置き換えてください。
:::

### variables.tf

プロジェクト名を変数として定義します。

```hcl
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "hugo-s3-demo"
}
```

### main.tf

S3バケット、OAC、CloudFront Functionを作成します。

```hcl
# バケット名の一意性を確保するためのランダム文字列
resource "random_id" "suffix" {
  byte_length = 4
}

# コンテンツ用S3バケット
resource "aws_s3_bucket" "content" {
  bucket = "${var.project_name}-content-${random_id.suffix.hex}"
}

# パブリックアクセスブロック
resource "aws_s3_bucket_public_access_block" "content" {
  bucket                  = aws_s3_bucket.content.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudFront OAC（Origin Access Control）
resource "aws_cloudfront_origin_access_control" "main" {
  name                              = "${var.project_name}-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront Function（URLリライト）
resource "aws_cloudfront_function" "url_rewrite" {
  name    = "${var.project_name}-url-rewrite"
  runtime = "cloudfront-js-2.0"
  publish = true
  code    = <<-EOF
    function handler(event) {
      var request = event.request;
      var uri = request.uri;
      if (uri.endsWith('/')) {
        request.uri += 'index.html';
      } else if (!uri.includes('.')) {
        request.uri += '/index.html';
      }
      return request;
    }
  EOF
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "main" {
  origin {
    domain_name              = aws_s3_bucket.content.bucket_regional_domain_name
    origin_id                = "S3Origin"
    origin_access_control_id = aws_cloudfront_origin_access_control.main.id
  }

  enabled             = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3Origin"
    viewer_protocol_policy = "redirect-to-https"
    cache_policy_id        = "658327ea-f89d-4fab-a63d-7e88639e58f6" # CachingOptimized

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.url_rewrite.arn
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# S3バケットポリシー（CloudFrontからのアクセスを許可）
resource "aws_s3_bucket_policy" "content" {
  bucket = aws_s3_bucket.content.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.content.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.main.arn
          }
        }
      }
    ]
  })
}
```

### コード解説

#### OAC（Origin Access Control）

```hcl
resource "aws_cloudfront_origin_access_control" "main" {
  name                              = "${var.project_name}-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}
```

OACはCloudFrontからS3へのアクセスを制御する仕組みです。
S3バケットへの直接アクセスを禁止し、CloudFront経由のみに制限できます。

旧方式のOAI（Origin Access Identity）より細かい権限制御が可能で、AWSが推奨する新しい方式です。

#### CloudFront Function

```hcl
resource "aws_cloudfront_function" "url_rewrite" {
  name    = "${var.project_name}-url-rewrite"
  runtime = "cloudfront-js-2.0"
  publish = true
  code    = <<-EOF
    function handler(event) {
      var request = event.request;
      var uri = request.uri;
      if (uri.endsWith('/')) {
        request.uri += 'index.html';
      } else if (!uri.includes('.')) {
        request.uri += '/index.html';
      }
      return request;
    }
  EOF
}
```

**なぜCloudFront Functionが必要なのか？**

OACを使用すると、S3の「静的ウェブサイトホスティング」機能が使えません。
そのため、`/posts/first-post/` へのアクセスで `index.html` が自動補完されず、404エラーになります。

CloudFront Functionでviewer-requestイベント時にURLリライトを行い、この問題を解決します。

| URLパターン | 変換後 |
|------------|--------|
| `/posts/` | `/posts/index.html` |
| `/posts/first-post` | `/posts/first-post/index.html` |

#### CloudFront Distribution

```hcl
resource "aws_cloudfront_distribution" "main" {
  # ...省略...
  
  default_cache_behavior {
    # HTTPをHTTPSにリダイレクト
    viewer_protocol_policy = "redirect-to-https"
    # AWS管理のキャッシュポリシー（静的サイトに最適）
    cache_policy_id        = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    
    # CloudFront Functionを関連付け
    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.url_rewrite.arn
    }
  }
  
  # デフォルト証明書を使用（カスタムドメインは#5で設定）
  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
```

`cache_policy_id` の `658327ea-f89d-4fab-a63d-7e88639e58f6` は、AWSが提供する「CachingOptimized」ポリシーのIDです。
静的サイトに最適化されたキャッシュ設定が適用されます。

#### S3バケットポリシー

```hcl
resource "aws_s3_bucket_policy" "content" {
  bucket = aws_s3_bucket.content.id
  policy = jsonencode({
    # ...省略...
    Condition = {
      StringEquals = {
        "AWS:SourceArn" = aws_cloudfront_distribution.main.arn
      }
    }
  })
}
```

CloudFrontからのアクセスのみを許可するバケットポリシーです。
`Condition` で特定のCloudFront DistributionのARNを指定し、他のCloudFrontからのアクセスも拒否します。

### outputs.tf

作成されたリソースの情報を出力します。

```hcl
output "s3_bucket_name" {
  value = aws_s3_bucket.content.bucket
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.main.id
}

output "cloudfront_domain_name" {
  value = aws_cloudfront_distribution.main.domain_name
}
```

### 実行

5つのファイルを作成したら実行します。

```bash
# 初期化（backend設定を読み込み）
terraform init

# 実行計画の確認
terraform plan

# 構築
terraform apply
```

`terraform apply` の実行後、以下のような出力が表示されます。

```text
Apply complete! Resources: 7 added, 0 changed, 0 destroyed.

Outputs:

cloudfront_distribution_id = "E2XXXXXXXXXX"
cloudfront_domain_name = "dxxxxxxxxxxxxx.cloudfront.net"
s3_bucket_name = "hugo-s3-demo-content-xxxxxxxx"
```

:::message
**出力値をメモしてください**
`s3_bucket_name` と `cloudfront_domain_name` は次のセクションで使用します。
:::

## 手動デプロイ

S3バケットとCloudFrontが作成されたので、Hugoでビルドしたコンテンツをデプロイします。

### baseURLの更新

Hugoプロジェクトに戻り、`hugo.toml` の `baseURL` をCloudFrontのドメインに更新します。

```bash
cd /path/to/hugo-s3-demo
```

`hugo.toml` を編集します。

```toml
baseURL = 'https://dxxxxxxxxxxxxx.cloudfront.net/'  # 出力されたcloudfront_domain_name
languageCode = 'en-us'
title = 'Hugo S3 Demo'
theme = 'ananke'
```

:::message alert
`baseURL` は、前のセクションで出力された `cloudfront_domain_name` に置き換えてください。
末尾のスラッシュ `/` を忘れずに付けてください。
:::

### ビルド

```bash
hugo
```

`public/` ディレクトリにHTMLファイルが生成されます。

### S3にアップロード

```bash
aws s3 sync public/ s3://hugo-s3-demo-content-xxxxxxxx/ --delete
```

- `s3://hugo-s3-demo-content-xxxxxxxx/` は出力された `s3_bucket_name` に置き換えてください
- `--delete` オプションは、S3にあってローカルにないファイルを削除します

### 動作確認

ブラウザで `https://dxxxxxxxxxxxxx.cloudfront.net/` にアクセスします。

以下を確認してください。

- [ ] トップページが表示される
- [ ] HTTPSで接続できる（ブラウザのアドレスバーに鍵マーク）
- [ ] 記事詳細ページ（`/posts/first-post/`）が表示される

:::message
記事詳細ページが404になる場合は、CloudFront Functionが正しく動作していません。
Terraformコードの `aws_cloudfront_function` を確認してください。
:::

## トラブルシューティング

### 403 Forbidden

**原因**: S3バケットポリシーが正しく設定されていない

**対処法**:

1. `terraform apply` を再実行
2. S3バケットポリシーがCloudFrontのARNを許可しているか確認

### 404 Not Found（サブページのみ）

**原因**: CloudFront Functionが動作していない

**対処法**:

1. AWSコンソールでCloudFront Functionsを開く
2. 関数が「Published」状態になっているか確認
3. CloudFront Distributionに関連付けられているか確認

### 更新が反映されない

**原因**: CloudFrontのキャッシュが残っている

**対処法**: キャッシュを無効化します。

```bash
aws cloudfront create-invalidation \
  --distribution-id E2XXXXXXXXXX \
  --paths "/*"
```

`--distribution-id` は `terraform output` で確認できます。

:::message
キャッシュ無効化は月1,000パスまで無料です。
`/*` で全ファイルを無効化すると1パスとしてカウントされます。
:::

## クリーンアップ（リソース削除）

記事の検証が終わったら、AWSリソースを削除してコストを抑えましょう。

### prod環境の削除

```bash
cd hugo-s3-demo-infra/prod

# S3バケット内のファイルを削除（空でないと削除できない）
aws s3 rm s3://hugo-s3-demo-content-xxxxxxxx/ --recursive

# Terraformリソースを削除
terraform destroy
```

### backend-setup環境の削除

```bash
cd ../backend-setup

# S3バケット内のファイルを削除
aws s3 rm s3://hugo-s3-demo-tfstate-xxxxxxxx/ --recursive

# バージョニング有効のため、DeleteMarkerも削除が必要な場合あり
# 削除に失敗した場合は、AWSコンソールからバケットを空にしてください

# Terraformリソースを削除
terraform destroy
```

:::message alert
`terraform destroy` を実行すると、すべてのリソースが削除されます。
本番環境では十分注意してください。
:::

## まとめ

本記事では、以下を構築しました。

- **Hugo**: 静的サイトジェネレーターでブログを作成
- **S3**: コンテンツの保存先
- **CloudFront**: CDNでHTTPS配信
- **OAC**: S3への直接アクセスを禁止
- **CloudFront Function**: URLリライトで404を回避
- **Terraform**: 全リソースをコード化

### 作成したリソース

| リソース | 用途 |
|----------|------|
| S3バケット（content） | Hugoビルド成果物の保存 |
| S3バケット（tfstate） | Terraformのstate管理 |
| DynamoDB | tfstateのロック管理 |
| CloudFront Distribution | CDN、HTTPS終端 |
| CloudFront OAC | S3へのアクセス制御 |
| CloudFront Function | URLリライト |
| S3バケットポリシー | CloudFrontからのアクセス許可 |

## 参考資料

- [Hugo公式ドキュメント](https://gohugo.io/documentation/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [CloudFront OAC - AWS公式](https://docs.aws.amazon.com/ja_jp/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)
- [CloudFront Functions - AWS公式](https://docs.aws.amazon.com/ja_jp/AmazonCloudFront/latest/DeveloperGuide/cloudfront-functions.html)
