+++
id = "251210221100"
date = '2025-12-10T22:11:00+09:00'
draft = false
title = 'Terraformチートシート：コマンド・構文・関数クイックリファレンス'
tags = ["インフラ", "Terraform", "AWS", "メモ"]
+++
## 今日学んだこと

Terraformを使う上で頻繁に参照するコマンド、ブロック構文、関数、パターンを1つの記事にまとめました。作業中に「あれ、どう書くんだっけ？」となったときにすぐ参照できるチートシートです。

## 学習内容

### 基本コマンド

<details>
<summary>初期化・実行コマンド</summary>

| コマンド | 説明 | よく使うオプション |
|----------|------|-------------------|
| `terraform init` | 初期化（Provider取得） | `-upgrade`（Provider更新） |
| `terraform plan` | 差分確認（ドライラン） | `-out=plan.tfplan`（計画を保存） |
| `terraform apply` | 変更を適用 | `-auto-approve`（確認スキップ） |
| `terraform destroy` | 全リソース削除 | `-target=xxx`（特定リソースのみ） |

</details>

<details>
<summary>確認・検証コマンド</summary>

| コマンド | 説明 |
|----------|------|
| `terraform validate` | 構文チェック |
| `terraform fmt` | コード整形（インデント等） |
| `terraform fmt -check` | 整形が必要か確認のみ |
| `terraform show` | 現在のStateを表示 |
| `terraform output` | Output値を表示 |

</details>

<details>
<summary>State操作コマンド</summary>

| コマンド | 説明 |
|----------|------|
| `terraform state list` | 管理中リソース一覧 |
| `terraform state show <リソース>` | 特定リソースの詳細 |
| `terraform state rm <リソース>` | Stateから削除（実リソースは残る） |
| `terraform state mv <旧> <新>` | リソース名変更 |
| `terraform force-unlock <LOCK_ID>` | ロック強制解除 |

</details>

<details>
<summary>その他のコマンド</summary>

| コマンド | 説明 |
|----------|------|
| `terraform graph` | 依存関係をDOT形式で出力 |
| `terraform console` | 対話モード（式の評価テスト） |
| `terraform import <リソース> <ID>` | 既存リソースをStateに取り込み |
| `terraform apply -replace=<リソース>` | 指定リソースを再作成 |

> **Note**: `terraform taint`は非推奨。`-replace`オプションを使用する。

</details>

---

### ブロック構文

<details>
<summary>terraform ブロック（設定）</summary>
```hcl
terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "my-tfstate-bucket"
    key            = "terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "my-tfstate-lock"
    encrypt        = true
  }
}
```

</details>

<details>
<summary>provider ブロック</summary>
```hcl
provider "aws" {
  region = "ap-northeast-1"

  default_tags {
    tags = {
      Project   = "my-project"
      ManagedBy = "terraform"
    }
  }
}

# 複数リージョン対応（alias）
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}
```

</details>

<details>
<summary>resource ブロック</summary>
```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id

  tags = {
    Name = "web-server"
  }

  depends_on = [aws_internet_gateway.main]

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = false
    ignore_changes        = [tags]
  }
}
```

</details>

<details>
<summary>data ブロック（既存リソース参照）</summary>
```hcl
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "web" {
  ami = data.aws_ami.amazon_linux.id
}
```

</details>

<details>
<summary>variable ブロック（入力変数）</summary>
```hcl
variable "instance_type" {
  type        = string
  default     = "t3.micro"
  description = "EC2 instance type"
}

variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "stg", "prod"], var.environment)
    error_message = "environment must be dev, stg, or prod"
  }
}

variable "password" {
  type      = string
  sensitive = true
}
```

</details>

<details>
<summary>output / locals ブロック</summary>
```hcl
output "instance_id" {
  value       = aws_instance.web.id
  description = "EC2 instance ID"
}

output "db_password" {
  value     = aws_db_instance.main.password
  sensitive = true
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
  name_prefix = "${var.project_name}-${var.environment}"
}
```

</details>

<details>
<summary>module ブロック</summary>
```hcl
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr    = "10.0.0.0/16"
  environment = var.environment
}

module "s3" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "3.0.0"

  bucket = "my-bucket"
}

# マルチリージョンプロバイダーを渡す
module "acm" {
  source = "./modules/acm"

  providers = {
    aws = aws.us_east_1
  }
}
```

</details>

<details>
<summary>moved ブロック（リファクタリング）</summary>
```hcl
moved {
  from = aws_s3_bucket.content
  to   = module.s3_content.aws_s3_bucket.this
}

moved {
  from = aws_instance.web
  to   = aws_instance.web_server
}
```

</details>

---

### よく使う型

| 型 | 例 |
|----|-----|
| `string` | `"hello"` |
| `number` | `123` |
| `bool` | `true`, `false` |
| `list(string)` | `["a", "b", "c"]` |
| `set(string)` | `toset(["a", "b"])` |
| `map(string)` | `{ key1 = "value1", key2 = "value2" }` |
| `object({...})` | `{ name = string, port = number }` |
| `any` | 任意の型 |

---

### よく使う関数

<details>
<summary>文字列関数</summary>

| 関数 | 説明 | 例 |
|------|------|-----|
| `format()` | 書式化 | `format("Hello, %s!", var.name)` |
| `join()` | 結合 | `join(", ", ["a", "b", "c"])` → `"a, b, c"` |
| `split()` | 分割 | `split(",", "a,b,c")` → `["a", "b", "c"]` |
| `lower()` | 小文字化 | `lower("HELLO")` → `"hello"` |
| `upper()` | 大文字化 | `upper("hello")` → `"HELLO"` |
| `replace()` | 置換 | `replace("hello", "l", "L")` |
| `trimspace()` | 空白除去 | `trimspace("  hello  ")` → `"hello"` |

</details>

<details>
<summary>コレクション関数</summary>

| 関数 | 説明 | 例 |
|------|------|-----|
| `length()` | 要素数 | `length(["a", "b"])` → `2` |
| `element()` | インデックス参照 | `element(["a", "b"], 0)` → `"a"` |
| `concat()` | リスト結合 | `concat(["a"], ["b"])` → `["a", "b"]` |
| `flatten()` | ネスト解除 | `flatten([["a"], ["b"]])` → `["a", "b"]` |
| `merge()` | マップ結合 | `merge({a=1}, {b=2})` → `{a=1, b=2}` |
| `lookup()` | マップ検索 | `lookup({a=1}, "a", 0)` → `1` |
| `keys()` | キー一覧 | `keys({a=1, b=2})` → `["a", "b"]` |
| `values()` | 値一覧 | `values({a=1, b=2})` → `[1, 2]` |
| `contains()` | 要素存在確認 | `contains(["a", "b"], "a")` → `true` |
| `distinct()` | 重複除去 | `distinct(["a", "a", "b"])` → `["a", "b"]` |

</details>

<details>
<summary>ファイル関数</summary>

| 関数 | 説明 | 例 |
|------|------|-----|
| `file()` | ファイル読み込み | `file("./scripts/init.sh")` |
| `pathexpand()` | `~`をホームパスに展開 | `pathexpand("~/.ssh/id_rsa.pub")` |
| `filebase64()` | Base64で読み込み | `filebase64("image.png")` |
| `templatefile()` | テンプレート適用 | `templatefile("user_data.sh", {name = "web"})` |

</details>

<details>
<summary>条件・型変換関数</summary>

| 関数 | 説明 | 例 |
|------|------|-----|
| `coalesce()` | 最初の非null値 | `coalesce(null, "default")` → `"default"` |
| `try()` | エラー時のフォールバック | `try(var.optional, "default")` |
| `tostring()` | 文字列変換 | `tostring(123)` → `"123"` |
| `tonumber()` | 数値変換 | `tonumber("123")` → `123` |
| `tobool()` | 真偽値変換 | `tobool("true")` → `true` |
| `tolist()` | リスト変換 | `tolist(toset(["a", "b"]))` |
| `toset()` | セット変換 | `toset(["a", "a", "b"])` |

</details>

---

### 条件分岐・ループ

<details>
<summary>三項演算子・count</summary>
```hcl
# 三項演算子
instance_type = var.environment == "prod" ? "t3.large" : "t3.micro"

# count（インデックスベース）
resource "aws_instance" "web" {
  count = 3
  tags = {
    Name = "web-${count.index}"
  }
}

# 条件付き作成
resource "aws_eip" "nat" {
  count = var.create_nat ? 1 : 0
}
```

</details>

<details>
<summary>for_each</summary>
```hcl
# マップ
resource "aws_subnet" "private" {
  for_each = {
    "a" = "10.0.1.0/24"
    "c" = "10.0.2.0/24"
  }

  availability_zone = "ap-northeast-1${each.key}"
  cidr_block        = each.value
}

# セット
resource "aws_security_group_rule" "ports" {
  for_each = toset(["80", "443", "22"])

  from_port = tonumber(each.value)
  to_port   = tonumber(each.value)
}
```

</details>

<details>
<summary>for式・dynamic ブロック</summary>
```hcl
# for式
locals {
  upper_names = [for name in var.names : upper(name)]
  instance_ids = {for inst in aws_instance.web : inst.tags.Name => inst.id}
  prod_instances = [for inst in var.instances : inst if inst.env == "prod"]
}

# dynamic ブロック
resource "aws_security_group" "main" {
  name = "main"

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

</details>

---

### ディレクトリ構成例

<details>
<summary>シンプル構成</summary>
```
project/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
└── terraform.tfvars
```

</details>

<details>
<summary>モジュール構成</summary>
```
project/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── ec2/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── backend.tf
│   │   └── terraform.tfvars
│   └── prod/
└── backend-setup/
    └── main.tf
```

</details>

---

### よく使うパターン

<details>
<summary>タグの共通化</summary>
```hcl
locals {
  common_tags = {
    Project     = "my-project"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_instance" "web" {
  tags = merge(local.common_tags, {
    Name = "web-server"
    Role = "web"
  })
}
```

</details>

<details>
<summary>条件付きリソース作成</summary>
```hcl
resource "aws_nat_gateway" "main" {
  count = var.enable_nat_gateway ? 1 : 0

  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public.id
}

output "nat_gateway_id" {
  value = var.enable_nat_gateway ? aws_nat_gateway.main[0].id : null
}
```

</details>

<details>
<summary>user_data / セキュリティグループ参照</summary>
```hcl
# user_data
resource "aws_instance" "web" {
  user_data = <<-EOF
              #!/bin/bash
              dnf update -y
              dnf install -y httpd
              systemctl start httpd
              EOF
}

# SGをソースに指定
resource "aws_vpc_security_group_ingress_rule" "rds" {
  security_group_id            = aws_security_group.rds.id
  referenced_security_group_id = aws_security_group.web.id
  from_port                    = 3306
  to_port                      = 3306
  ip_protocol                  = "tcp"
}
```

</details>

---

### 注意点・ベストプラクティス

#### やるべきこと

- `terraform fmt` でコード整形
- `terraform validate` で構文チェック
- `.terraform.lock.hcl` をGit管理（Providerバージョン固定）
- `terraform.tfvars` はGit管理外（機密情報含む場合）
- `sensitive = true` でパスワード等をマスク
- リモートバックエンド（S3 + DynamoDB）で状態管理

#### 避けるべきこと

- 本番環境で `-auto-approve` を使わない
- ハードコードされたAMI ID（data sourceで取得）
- ハードコードされたパスワード（variables or Secrets Manager）
- `terraform state rm` の安易な使用
- `force-unlock` は他の操作がないことを確認してから

## まとめ

| 用途 | 参照セクション |
|------|---------------|
| コマンドを調べたい | 基本コマンド |
| 書き方を確認したい | ブロック構文 |
| 関数の使い方を調べたい | よく使う関数 |
| ループの書き方を確認したい | 条件分岐・ループ |
| 実装パターンを参考にしたい | よく使うパターン |

- `terraform init` → `plan` → `apply` が基本フロー
- `count`はインデックス、`for_each`はキーでリソースを識別
- `locals`で共通値を定義、`merge()`でタグを結合

## 参考

- [Terraform公式ドキュメント](https://developer.hashicorp.com/terraform/docs)
- [AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform関数一覧](https://developer.hashicorp.com/terraform/language/functions)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)