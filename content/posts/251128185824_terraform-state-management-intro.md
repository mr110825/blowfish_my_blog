+++
id = "251128185824"
date = '2025-11-28T18:58:24+09:00'
draft = false
title = 'Terraformステート管理 Part1 - S3リモートバックエンドとワークスペース'
tags = ["インフラ", "Terraform", "AWS", "ハンズオン"]
+++

## 今日学んだこと

Terraformのステート管理について、S3リモートバックエンドの構築からワークスペースによる環境分離まで実践した。途中でステートファイルの上書き事故も経験し、その復旧作業から多くの教訓を得た。

## Terraformステートとは

Terraformはインフラの現在状態を`terraform.tfstate`というファイルに記録している。`terraform plan`や`terraform apply`を実行すると、このステートファイルとAWSの実際の状態を比較して差分を検出する。

```json
{
  "version": 4,
  "terraform_version": "1.6.0",
  "serial": 42,
  "resources": []
}
```

個人開発ではローカル保存で問題ないが、チーム開発では以下の課題が発生する

| 課題 | 問題点 |
|------|--------|
| 共有 | メンバー間でステートを共有できない |
| ロック | 同時編集で競合が発生する |
| セキュリティ | 機密情報がローカルに残る |

これを解決するのが**リモートバックエンド**。

---

## Step 1: リモートバックエンド用のS3・DynamoDBを作成

### ディレクトリ作成

```bash
mkdir -p ~/terraform-state-study
cd ~/terraform-state-study
```

### main.tfを作成

```hcl
# main.tf
provider "aws" {
  region = "ap-northeast-1"
}

# S3バケット（ステートファイル保管用）
resource "aws_s3_bucket" "terraform_state" {
  # 重要: バケット名はAWS全体でグローバルに一意にすること
  bucket = "tf-state-backend-20251128"

  # 誤削除防止（学習時はコメントアウト）
  # lifecycle {
  #   prevent_destroy = true
  # }
}

# バージョニング有効化（ロールバック可能に）
resource "aws_s3_bucket_versioning" "enabled" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# サーバーサイド暗号化
resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# パブリックアクセスブロック
resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket                  = aws_s3_bucket.terraform_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDBテーブル（ロック用）
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "tf-state-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"  # 大文字小文字を完全一致させること

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

### デプロイ

```bash
terraform init
terraform validate
terraform apply
```

最初に`tf-state-backend`というバケット名で試したところ、既に他のユーザーに使われていてエラーになった。S3バケット名はグローバルで一意である必要があるため、日付を追加して解決した。

`lifecycle`は誤削除を防止することが目的なので、リソース削除時はコメントアウトが必要。
```terraform
lifecycle {
  prevent_destroy = true
}
```

---

## Step 2: ステートをS3に移行

この時点ではステートはまだローカルに保存されている。S3に移行するためにbackend設定を追加する。

### backend.hclを作成（部分設定）

`backend`ブロックでは変数が使えないため、共通設定を外部ファイルに切り出す。

```hcl
# backend.hcl
bucket         = "tf-state-backend-20251128"
region         = "ap-northeast-1"
dynamodb_table = "tf-state-locks"
encrypt        = true
```

### main.tfにbackend設定を追加

```hcl
terraform {
  backend "s3" {
    key = "global/s3/terraform.tfstate"
  }
}
```

### ステートを移行

```bash
terraform init -backend-config=backend.hcl
```

「既存のステートをS3にコピーするか？」と聞かれるので`yes`を入力。

S3コンソールで`global/s3/terraform.tfstate`が作成されていることを確認できた。

---

## Step 3: ワークスペースによる分離を体験

同じコードで複数の環境（default、staging、prodなど）を管理する仕組み。

### ワークスペース用ディレクトリ作成

```bash
mkdir -p ~/terraform-state-study-workspace
cd ~/terraform-state-study-workspace
```

### main.tfを作成

```hcl
provider "aws" {
  region = "ap-northeast-1"
}

resource "aws_instance" "example" {
  ami           = "ami-03852a41f1e05c8e4"
  instance_type = "t2.micro"
}

terraform {
  backend "s3" {
    # 重要: Step 1（リモートバックエンド用）と異なるkeyを使用すること！
    key            = "workspace-example/terraform.tfstate"
    bucket         = "tf-state-backend-20251128"
    region         = "ap-northeast-1"
    dynamodb_table = "tf-state-locks"
    encrypt        = true
  }
}
```

### ワークスペースの操作

```bash
terraform init
terraform apply

# 現在のワークスペース確認
terraform workspace show
# => default

# 新しいワークスペース作成
terraform workspace new example1
terraform apply  # 別のEC2が作成される

# さらに作成
terraform workspace new example2
terraform apply

# 一覧確認
terraform workspace list
#   default
#   example1
# * example2

# 切り替え
terraform workspace select example1
```

S3には以下のパスでステートが保存される：

```
s3://bucket/
├── workspace-example/terraform.tfstate              # default
└── env:/
    ├── example1/workspace-example/terraform.tfstate
    └── example2/workspace-example/terraform.tfstate
```

### クリーンアップ

```bash
# 各ワークスペースでdestroy
terraform workspace select example1 && terraform destroy
terraform workspace select example2 && terraform destroy
terraform workspace select default && terraform destroy
```

---

## 実際に起きたトラブルと教訓

### 事故: 同じkeyを使い回してステートが上書きされた

Step 3（ワークスペース）で`terraform apply`を実行した際、最初はStep 1と**同じkey**（`global/s3/terraform.tfstate`）を使ってしまった。

その結果：
1. Step 1で作成したS3・DynamoDBリソースのステートが上書きされた
2. Step 3のコードにはDynamoDBの定義がないため、Terraformは「削除すべきリソース」と判断
3. **DynamoDBテーブルが削除された**
4. 以降のTerraform操作でロックが取れずエラー

```
Error: Error acquiring the state lock
ResourceNotFoundException: Requested resource not found
```

### 復旧方法

```bash
# 緊急時のみ: ロックをスキップしてdestroy
terraform destroy -lock=false
```

S3バケットはバージョニングが有効なため、全オブジェクトバージョンを削除しないと削除できない：

```bash
# オブジェクトバージョン確認
aws s3api list-object-versions --bucket <バケット名> --region ap-northeast-1

# 全バージョン削除後、バケット削除
aws s3 rb s3://<バケット名>
```

### 教訓

| 教訓 | 対策 |
|------|------|
| **keyは必ず一意にする** | 各プロジェクトで`project-name/terraform.tfstate`のように分ける |
| **バックエンドのインフラは慎重に** | S3・DynamoDBが破壊されると全てに影響する |
| **`-lock=false`は緊急時のみ** | 競合リスクがあるため通常は使用しない |

---

## ファイルレイアウトによる分離（概要）

ワークスペースには以下の欠点がある：

- 全環境で同じバックエンドを使用（権限分離が困難）
- どのワークスペースにいるか分かりにくい
- 誤操作で本番環境を破壊するリスク

より堅牢な分離には、**環境ごとにディレクトリを分ける**方法が推奨される：

```
terraform-project/
├── stage/                            # ステージング環境
│   ├── data-stores/mysql/            # DB層
│   └── services/webserver-cluster/   # App層
└── prod/                             # 本番環境（完全に別管理）
```

分離したコンポーネント間（例: RDSとWebサーバー）で情報を共有するには、`terraform_remote_state`データソースを使用する。

詳細な実装手順（RDS構築、terraform_remote_stateによる連携、templatefile関数の活用）は[Part2]({{< ref "/posts/251128193149_terraform-file-layout-separation" >}})で解説。

---

## 完成形のコード

### ディレクトリ構成

```
~/terraform-state-study/           # Step 1: リモートバックエンド用
├── main.tf
└── backend.hcl

~/terraform-state-study-workspace/ # Step 3: ワークスペース検証用
└── main.tf
```

<details>
<summary>Step 1: リモートバックエンド用（~/terraform-state-study/）</summary>

**main.tf**
```hcl
provider "aws" {
  region = "ap-northeast-1"
}

# S3バケット（ステートファイル保管用）
resource "aws_s3_bucket" "terraform_state" {
  bucket = "tf-state-backend-20251128"

  # lifecycle {
  #   prevent_destroy = true
  # }
}

# バージョニング有効化
resource "aws_s3_bucket_versioning" "enabled" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# サーバーサイド暗号化
resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# パブリックアクセスブロック
resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket                  = aws_s3_bucket.terraform_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDBテーブル（ロック用）
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "tf-state-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

terraform {
  backend "s3" {
    key = "global/s3/terraform.tfstate"
  }
}
```

**backend.hcl**
```hcl
bucket         = "tf-state-backend-20251128"
region         = "ap-northeast-1"
dynamodb_table = "tf-state-locks"
encrypt        = true
```

</details>

<details>
<summary>Step 3: ワークスペース用（~/terraform-state-study-workspace/）</summary>

**main.tf**
```hcl
provider "aws" {
  region = "ap-northeast-1"
}

resource "aws_instance" "example" {
  ami           = "ami-03852a41f1e05c8e4"
  instance_type = "t2.micro"
}

terraform {
  backend "s3" {
    key            = "workspace-example/terraform.tfstate"
    bucket         = "tf-state-backend-20251128"
    region         = "ap-northeast-1"
    dynamodb_table = "tf-state-locks"
    encrypt        = true
  }
}
```

</details>

---

## まとめ

### 学んだこと

1. **リモートバックエンド**: S3 + DynamoDBでステート管理とロックを実現
2. **部分設定**: `backend.hcl`で共通設定を切り出してコピペを削減
3. **ワークスペース**: 簡易な環境分離だが、可視性が低く誤操作リスクあり
4. **ファイルレイアウト**: 本番環境の分離には環境ごとのディレクトリ分割が推奨（[Part2]({{< ref "/posts/251128193149_terraform-file-layout-separation" >}})で実践）

### チェックリスト

- [ ] S3バケット名はグローバルで一意か
- [ ] DynamoDBのプライマリキーは`LockID`（大文字小文字一致）か
- [ ] 各プロジェクトの`key`は一意か

---

## 参考

- [詳解 Terraform 第3版 ―Infrastructure as Codeを実現する](https://www.oreilly.co.jp/books/9784814400522/)
  - 著者：Yevgeniy Brikman
  - 訳者：松浦 隼人
  - 出版社：オライリージャパン
  - 出版年：2023年
- [Terraform公式ドキュメント](https://developer.hashicorp.com/terraform/docs)
- [Terraformステート管理 Part2 - ファイルレイアウトとterraform_remote_state]({{< ref "/posts/251128193149_terraform-file-layout-separation" >}})