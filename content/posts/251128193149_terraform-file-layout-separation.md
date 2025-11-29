+++
id = "251128193149"
date = '2025-11-28T19:31:49+09:00'
draft = false
title = 'Terraformステート管理 Part2 - ファイルレイアウトとterraform_remote_state'
tags = ["インフラ", "Terraform", "AWS", "ハンズオン・チュートリアル"]
+++

## 今日学んだこと

前回の記事でワークスペースによるステート分離を学んだが、本番環境の分離には不十分だった。今回は**ファイルレイアウトによる分離**を実践し、RDSとWebサーバーを別々に管理しながら`terraform_remote_state`で連携させる方法を学んだ。

## 前回の振り返り: ワークスペースの限界

[Part1]({{< ref "/posts/251128185824_terraform-state-management-intro" >}})でワークスペースの欠点を確認した。

| 欠点 | 説明 |
|------|------|
| 同一バックエンド | 全環境が同じS3/DynamoDBを使用（権限分離が困難） |
| 可視性が低い | 今どのワークスペースにいるか分かりにくい |
| 誤操作リスク | `terraform workspace select prod` を忘れて本番を破壊する可能性 |

これらの問題を解決するのが**ファイルレイアウトによる分離**。

---

## ファイルレイアウトによる分離とは

環境ごと・コンポーネントごとに**別のディレクトリで管理**する方法。

```
terraform-project/
├── stage/                            # ステージング環境
│   ├── data-stores/mysql/            # DB層（変更頻度: 低）
│   └── services/webserver-cluster/   # App層（変更頻度: 高）
└── prod/                             # 本番環境（完全に別管理）
    ├── data-stores/mysql/
    └── services/webserver-cluster/
```

### なぜコンポーネントも分離するのか

| レイヤー | 変更頻度 | リスク |
|---------|---------|--------|
| VPC/ネットワーク | 月1回程度 | 高（全体に影響） |
| データベース | 週1回程度 | 高（データ損失） |
| Webサーバー | 1日数回 | 低（再デプロイ可能） |

頻繁に変更するWebサーバーと、めったに変更しないDBを同じステートで管理すると、**Webサーバーの変更時に誤ってDBを破壊するリスク**がある。

### 分離されたコンポーネント間の連携

問題: RDSとWebサーバーが別プロジェクトになると、WebサーバーはRDSの接続情報をどうやって知るのか？

解決: **terraform_remote_state**で別プロジェクトのステートからoutputを参照する。

```
[mysql/]                              [webserver-cluster/]
   │                                         │
   └── outputs.tf で address/port を出力    │
              │                              │
              └──────────────────────────────┼──→ terraform_remote_state で参照
```

---

## Step 1: RDSの構築

### ディレクトリ構成

```bash
mkdir -p stage/data-stores/mysql
cd stage/data-stores/mysql
```

### variables.tf

```hcl
variable "db_name" {
  description = "データベース名"
  type        = string
  default     = "example_database"
}

variable "db_username" {
  description = "データベースのユーザー名"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "データベースのパスワード"
  type        = string
  sensitive   = true
}
```

`sensitive = true`を指定すると、`terraform plan`や`terraform apply`の出力でマスクされる。

### main.tf

```hcl
provider "aws" {
  region = "ap-northeast-1"
}

terraform {
  backend "s3" {
    # 重要: keyはRDS専用のパスにする
    key            = "stage/data-stores/mysql/terraform.tfstate"
    bucket         = "tf-state-backend-20251128"
    region         = "ap-northeast-1"
    dynamodb_table = "tf-state-locks"
    encrypt        = true
  }
}

resource "aws_db_instance" "example" {
  identifier_prefix   = "terraform-up-and-running"
  engine              = "mysql"
  allocated_storage   = 10
  instance_class      = "db.t3.micro"
  skip_final_snapshot = true
  db_name             = var.db_name

  username = var.db_username
  password = var.db_password
}
```

### outputs.tf（重要）

Webサーバーから参照するために、接続情報を**output**として公開する。

```hcl
output "address" {
  value       = aws_db_instance.example.address
  description = "データベースの接続エンドポイント"
}

output "port" {
  value       = aws_db_instance.example.port
  description = "データベースのポート番号"
}
```

### デプロイ

```bash
terraform init
terraform apply
# var.db_username: admin
# var.db_password: yourpassword123
```

RDSの作成には5-10分かかる。完了したら`terraform output`で接続情報を確認できる。

---

## Step 2: Webサーバークラスタの構築

### ディレクトリ構成

```bash
mkdir -p stage/services/webserver-cluster
cd stage/services/webserver-cluster
```

### terraform_remote_stateとは

#### なぜ必要なのか

ファイルレイアウトで分離すると、RDSとWebサーバーは**別々のTerraformプロジェクト**になる。それぞれが独自のステートファイルを持つため、通常の方法では互いのリソース情報にアクセスできない。

```
[mysql/]                         [webserver-cluster/]
terraform.tfstate                terraform.tfstate
    │                                │
    └── RDSのaddress/portを保持      └── RDSの情報が必要だが...？
```

WebサーバーがRDSに接続するには、RDSのエンドポイント（address/port）が必要。これを解決するのが`terraform_remote_state`。

#### 仕組み

`terraform_remote_state`は**読み取り専用のデータソース**で、別プロジェクトのステートファイルから`output`で公開された値を取得する。

```
[mysql/]                                    [webserver-cluster/]
    │                                              │
    ├── outputs.tf で address/port を公開          │
    │       │                                      │
    │       ▼                                      │
    │   S3に保存されたステート ◀─────────────────────┤
    │   (stage/data-stores/mysql/                  │
    │    terraform.tfstate)                        │
    │       │                                      │
    │       │  terraform_remote_state で読み取り   │
    │       └──────────────────────────────────────▶ db_address, db_port として使用
```

**重要**: `terraform_remote_state`で読み取れるのは`output`で明示的に公開された値のみ。ステートファイル内の全リソース情報にアクセスできるわけではない。

#### 基本構文

```hcl
data "terraform_remote_state" "db" {
  backend = "s3"  # バックエンドの種類

  config = {
    bucket = "tf-state-backend-20251128"
    key    = "stage/data-stores/mysql/terraform.tfstate"  # RDSのステートのkey
    region = "ap-northeast-1"
  }
}
```

| 属性 | 説明 |
|-----|------|
| `backend` | 参照先のバックエンド種類（s3, gcs, azurerm等） |
| `config.bucket` | S3バケット名 |
| `config.key` | 参照先プロジェクトのステートファイルのkey |
| `config.region` | S3バケットのリージョン |

#### 参照方法

```hcl
# outputs.address を参照
data.terraform_remote_state.db.outputs.address

# outputs.port を参照
data.terraform_remote_state.db.outputs.port
```

#### ハードコードとの比較

| 方式 | コード例 | 問題点 |
|------|---------|--------|
| ハードコード | `db_address = "terraform-xxx.rds.amazonaws.com"` | RDS再作成時に手動更新が必要 |
| terraform_remote_state | `db_address = data.terraform_remote_state.db.outputs.address` | 自動的に最新値を取得 |

```hcl
# NG: ハードコード
db_address = "terraform-xxx.rds.amazonaws.com"
# → RDSを再作成するとアドレスが変わり、手動更新が必要
# → 複数環境で異なる値を管理する必要がある

# OK: terraform_remote_state
db_address = data.terraform_remote_state.db.outputs.address
# → RDSが変わっても terraform plan/apply 時に最新のアドレスを取得
# → 環境ごとにkeyを変えるだけで対応可能
```

#### 注意点

| 注意点 | 説明 |
|-------|------|
| **keyの一致** | `terraform_remote_state`の`key`は、参照先プロジェクトの`backend`設定と完全に一致させること |
| **outputの公開** | 参照したい値は参照先で`output`として定義する必要がある |
| **依存関係** | 参照先（RDS）を先にデプロイしてからWebサーバーをデプロイすること |
| **読み取り専用** | ステートの読み取りのみ可能。変更はできない |

### templatefile関数

外部ファイルを読み込み、変数を埋め込む関数。

```hcl
user_data = base64encode(templatefile("user-data.sh", {
  server_port = var.server_port
  db_address  = data.terraform_remote_state.db.outputs.address
  db_port     = data.terraform_remote_state.db.outputs.port
}))
```

HCLとbashを分離することで可読性が向上し、スクリプト単体でのテストも可能になる。

### user-data.sh

```bash
#!/bin/bash
cd /home/ec2-user
cat > index.html <<EOF
<h1>Hello, World</h1>
<p>DB address: ${db_address}</p>
<p>DB port: ${db_port}</p>
EOF
nohup python3 -m http.server ${server_port} &
```

> **注意**: このコードは `terraform_remote_state` の動作確認用サンプルです。ブラウザでアクセスするとDBの接続情報が画面に表示されます。実際の運用環境では、このような機密情報をHTMLページに表示せず、アプリケーション内部でのみ使用してください。

### variables.tf

```hcl
variable "server_port" {
  description = "HTTPリクエストを受け付けるポート番号"
  type        = number
  default     = 8080
}

variable "alb_name" {
  description = "ALBの名前"
  type        = string
  default     = "terraform-asg-example"
}

variable "alb_security_group_name" {
  description = "ALB用セキュリティグループの名前"
  type        = string
  default     = "terraform-example-alb"
}

variable "instance_security_group_name" {
  description = "EC2インスタンス用セキュリティグループの名前"
  type        = string
  default     = "terraform-example-instance"
}
```

### main.tf

```hcl
provider "aws" {
  region = "ap-northeast-1"
}

terraform {
  backend "s3" {
    bucket         = "tf-state-backend-20251128"
    key            = "stage/services/webserver-cluster/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "tf-state-locks"
    encrypt        = true
  }
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# RDSの状態をリモートステートから取得
data "terraform_remote_state" "db" {
  backend = "s3"

  config = {
    bucket = "tf-state-backend-20251128"
    key    = "stage/data-stores/mysql/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

# -----------------------------------------------------------------------------
# Launch Template & Auto Scaling Group
# -----------------------------------------------------------------------------

resource "aws_launch_template" "example" {
  image_id      = "ami-03852a41f1e05c8e4"
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.instance.id]

  user_data = base64encode(templatefile("user-data.sh", {
    server_port = var.server_port
    db_address  = data.terraform_remote_state.db.outputs.address
    db_port     = data.terraform_remote_state.db.outputs.port
  }))
}

resource "aws_autoscaling_group" "example" {
  vpc_zone_identifier = data.aws_subnets.default.ids

  launch_template {
    id      = aws_launch_template.example.id
    version = "$Latest"
  }

  target_group_arns = [aws_lb_target_group.asg.arn]
  health_check_type = "ELB"

  min_size = 2
  max_size = 10

  tag {
    key                 = "Name"
    value               = "terraform-asg-example"
    propagate_at_launch = true
  }
}

# -----------------------------------------------------------------------------
# Security Groups
# -----------------------------------------------------------------------------

resource "aws_security_group" "instance" {
  name = var.instance_security_group_name

  ingress {
    from_port   = var.server_port
    to_port     = var.server_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "alb" {
  name = var.alb_security_group_name

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# -----------------------------------------------------------------------------
# Application Load Balancer
# -----------------------------------------------------------------------------

resource "aws_lb" "example" {
  name               = var.alb_name
  load_balancer_type = "application"
  subnets            = data.aws_subnets.default.ids
  security_groups    = [aws_security_group.alb.id]
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.example.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "fixed-response"

    fixed_response {
      content_type = "text/plain"
      message_body = "404: page not found"
      status_code  = 404
    }
  }
}

resource "aws_lb_target_group" "asg" {
  name     = var.alb_name
  port     = var.server_port
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.default.id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 15
    timeout             = 3
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener_rule" "asg" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  condition {
    path_pattern {
      values = ["*"]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.asg.arn
  }
}
```

### outputs.tf

```hcl
output "alb_dns_name" {
  value       = aws_lb.example.dns_name
  description = "ロードバランサーのDNS名"
}

output "asg_name" {
  value       = aws_autoscaling_group.example.name
  description = "Auto Scaling Groupの名前"
}
```

### デプロイ

```bash
terraform init
terraform apply
```

---

## Step 3: 動作確認

### terraform consoleで確認

```bash
terraform console
```

```hcl
> data.terraform_remote_state.db.outputs
{
  "address" = "terraform-up-and-running-xxx.rds.amazonaws.com"
  "port" = 3306
}
> exit
```

### ブラウザで確認

```bash
# ALBのDNS名を取得
terraform output alb_dns_name

# curlで確認
curl http://<ALB_DNS_NAME>
```

「Hello, World」と「DB address」「DB port」が表示されれば成功。

---

## クリーンアップ: 依存関係と削除順序

### なぜ削除順序が重要なのか

Terraformリソースには**依存関係**がある。依存されているリソースを先に削除しようとするとエラーになる。

```
[Webサーバー] ──依存──→ [RDS]
      │                    │
      │                    └── 接続情報（address/port）を参照
      │
      └── terraform_remote_state でRDSのステートを参照

[S3/DynamoDB]
      │
      └── 全プロジェクトのステートを保管・ロック
```

**正しい削除順序**: 依存する側 → 依存される側

```bash
# 1. Webサーバー（RDSに依存）
cd stage/services/webserver-cluster
terraform destroy

# 2. RDS
cd ../../../stage/data-stores/mysql
terraform destroy

# 3. S3/DynamoDB（全体のバックエンド）- 必要な場合のみ
```

**逆順で削除しようとした場合**:
- S3を先に削除 → Webサーバーのステートにアクセスできずエラー
- RDSを先に削除 → Webサーバーの `terraform_remote_state` がエラー

---

## 構築したアーキテクチャ

```
┌─────────────────────────────────────────────────────────────────┐
│                         S3 Backend                               │
│  ├── stage/data-stores/mysql/terraform.tfstate    ← RDSの状態    │
│  └── stage/services/webserver-cluster/terraform.tfstate          │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ terraform_remote_state で参照
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Webサーバー                               │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │   ALB (port 80)   │───▶│   ASG (EC2 x2)   │                   │
│  └──────────────────┘    └──────────────────┘                   │
│                                   │                              │
│                                   │ DB接続情報を取得             │
│                                   ▼                              │
│                          ┌──────────────────┐                   │
│                          │   RDS (MySQL)     │                   │
│                          └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 完成形のコード

### ディレクトリ構成

```
stage/
├── data-stores/
│   └── mysql/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── services/
    └── webserver-cluster/
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        └── user-data.sh
```

<details>
<summary>stage/data-stores/mysql/</summary>

**main.tf**
```hcl
provider "aws" {
  region = "ap-northeast-1"
}

terraform {
  backend "s3" {
    key            = "stage/data-stores/mysql/terraform.tfstate"
    bucket         = "tf-state-backend-20251128"
    region         = "ap-northeast-1"
    dynamodb_table = "tf-state-locks"
    encrypt        = true
  }
}

resource "aws_db_instance" "example" {
  identifier_prefix   = "terraform-up-and-running"
  engine              = "mysql"
  allocated_storage   = 10
  instance_class      = "db.t3.micro"
  skip_final_snapshot = true
  db_name             = var.db_name

  username = var.db_username
  password = var.db_password
}
```

**variables.tf**
```hcl
variable "db_name" {
  description = "データベース名"
  type        = string
  default     = "example_database"
}

variable "db_username" {
  description = "データベースのユーザー名"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "データベースのパスワード"
  type        = string
  sensitive   = true
}
```

**outputs.tf**
```hcl
output "address" {
  value       = aws_db_instance.example.address
  description = "データベースの接続エンドポイント"
}

output "port" {
  value       = aws_db_instance.example.port
  description = "データベースのポート番号"
}
```

</details>

<details>
<summary>stage/services/webserver-cluster/</summary>

**main.tf**
```hcl
provider "aws" {
  region = "ap-northeast-1"
}

terraform {
  backend "s3" {
    bucket         = "tf-state-backend-20251128"
    key            = "stage/services/webserver-cluster/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "tf-state-locks"
    encrypt        = true
  }
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "terraform_remote_state" "db" {
  backend = "s3"

  config = {
    bucket = "tf-state-backend-20251128"
    key    = "stage/data-stores/mysql/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

# -----------------------------------------------------------------------------
# Launch Template & Auto Scaling Group
# -----------------------------------------------------------------------------

resource "aws_launch_template" "example" {
  image_id      = "ami-03852a41f1e05c8e4"
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.instance.id]

  user_data = base64encode(templatefile("user-data.sh", {
    server_port = var.server_port
    db_address  = data.terraform_remote_state.db.outputs.address
    db_port     = data.terraform_remote_state.db.outputs.port
  }))
}

resource "aws_autoscaling_group" "example" {
  vpc_zone_identifier = data.aws_subnets.default.ids

  launch_template {
    id      = aws_launch_template.example.id
    version = "$Latest"
  }

  target_group_arns = [aws_lb_target_group.asg.arn]
  health_check_type = "ELB"

  min_size = 2
  max_size = 10

  tag {
    key                 = "Name"
    value               = "terraform-asg-example"
    propagate_at_launch = true
  }
}

# -----------------------------------------------------------------------------
# Security Groups
# -----------------------------------------------------------------------------

resource "aws_security_group" "instance" {
  name = var.instance_security_group_name

  ingress {
    from_port   = var.server_port
    to_port     = var.server_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "alb" {
  name = var.alb_security_group_name

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# -----------------------------------------------------------------------------
# Application Load Balancer
# -----------------------------------------------------------------------------

resource "aws_lb" "example" {
  name               = var.alb_name
  load_balancer_type = "application"
  subnets            = data.aws_subnets.default.ids
  security_groups    = [aws_security_group.alb.id]
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.example.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "fixed-response"

    fixed_response {
      content_type = "text/plain"
      message_body = "404: page not found"
      status_code  = 404
    }
  }
}

resource "aws_lb_target_group" "asg" {
  name     = var.alb_name
  port     = var.server_port
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.default.id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 15
    timeout             = 3
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener_rule" "asg" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  condition {
    path_pattern {
      values = ["*"]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.asg.arn
  }
}
```

**variables.tf**
```hcl
variable "server_port" {
  description = "HTTPリクエストを受け付けるポート番号"
  type        = number
  default     = 8080
}

variable "alb_name" {
  description = "ALBの名前"
  type        = string
  default     = "terraform-asg-example"
}

variable "alb_security_group_name" {
  description = "ALB用セキュリティグループの名前"
  type        = string
  default     = "terraform-example-alb"
}

variable "instance_security_group_name" {
  description = "EC2インスタンス用セキュリティグループの名前"
  type        = string
  default     = "terraform-example-instance"
}
```

**outputs.tf**
```hcl
output "alb_dns_name" {
  value       = aws_lb.example.dns_name
  description = "ロードバランサーのDNS名"
}

output "asg_name" {
  value       = aws_autoscaling_group.example.name
  description = "Auto Scaling Groupの名前"
}
```

**user-data.sh**
```bash
#!/bin/bash
cd /home/ec2-user
cat > index.html <<EOF
<h1>Hello, World</h1>
<p>DB address: ${db_address}</p>
<p>DB port: ${db_port}</p>
EOF
nohup python3 -m http.server ${server_port} &
```

</details>

---

## まとめ

### 学んだこと

| 項目 | 内容 |
|------|------|
| ファイルレイアウト分離 | 環境・コンポーネントごとにディレクトリを分けて完全分離 |
| outputs.tf | 他プロジェクトに公開したい値を定義 |
| terraform_remote_state | 別プロジェクトのoutputを参照 |
| templatefile | 外部ファイルに変数を埋め込む |
| 削除順序 | 依存する側 → 依存される側の順で削除 |

### ワークスペース vs ファイルレイアウト

| 観点 | ワークスペース | ファイルレイアウト |
|------|--------------|------------------|
| 設定の手軽さ | 簡単 | ディレクトリ構成が必要 |
| 権限分離 | 困難（同一バックエンド） | 可能（別バックエンド） |
| 可視性 | 低い | 高い（ディレクトリ名で明確） |
| コード重複 | なし | あり（ch4のモジュールで解決） |
| 推奨用途 | 個人開発・実験 | 本番環境・チーム開発 |

### チェックリスト

- [ ] 各コンポーネントの`key`は一意か
- [ ] RDSの`outputs.tf`でaddress/portを出力しているか
- [ ] `terraform_remote_state`のkeyはRDSと一致しているか
- [ ] 削除は依存関係の逆順で行っているか

---

## 参考

- [詳解 Terraform 第3版 ―Infrastructure as Codeを実現する](https://www.oreilly.co.jp/books/9784814400522/)
  - 著者：Yevgeniy Brikman
  - 訳者：松浦 隼人
  - 出版社：オライリージャパン
  - 出版年：2023年
- [Terraform公式ドキュメント](https://developer.hashicorp.com/terraform/docs)
- [Terraformステート管理 Part1 - S3リモートバックエンドとワークスペース](/posts/251128185824_terraform-state-management-intro/)
