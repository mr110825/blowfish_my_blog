+++
id = "251128004323"
date = '2025-11-28T00:43:23+09:00'
draft = false
title = 'TerraformでAWS環境を構築して削除するまで - 入門ハンズオン'
tags = ["インフラ", "Terraform", "AWS", "ハンズオン・チュートリアル", "入門"]
+++
## はじめに

本記事は「詳解Terraform」のch2で学んだ内容を参考にしてハンズオン形式でまとめたものです。
Terraformを使って、ゼロからAWS環境を構築し、最後にすべて削除するまでを一気に体験します。

### 最終的に作るもの

```
[ユーザー] → [ALB:80] → [ASG] → [EC2 × 2台:8080]
```

- ALB（Application Load Balancer）でトラフィックを受け付け
- Auto Scaling Group（ASG）で2台のEC2を管理
- 各EC2はポート8080でWebサーバを起動

---

## 1. 事前準備

### 1-1. AWSアカウントの作成

AWSアカウントがない場合は、[AWS公式サイト](https://aws.amazon.com/jp/)から作成してください。

作業用のIAMユーザーを作成し、適切な権限を付与することを推奨します。

### 1-2. AWS CLIの設定

```bash
# AWS CLIをインストール（Ubuntu/WSL）
sudo apt update
sudo apt install -y unzip curl
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# バージョン確認
aws --version

# 認証情報を設定
aws configure
# → Access Key ID, Secret Access Key, Region(ap-northeast-1)を入力
```

### 1-3. Terraformのインストール

```bash
# Ubuntu/WSL
sudo apt update && sudo apt install -y gnupg software-properties-common

# HashiCorpのGPGキーを追加
wget -O- https://apt.releases.hashicorp.com/gpg | \
  gpg --dearmor | \
  sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null

# リポジトリを追加
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
  https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
  sudo tee /etc/apt/sources.list.d/hashicorp.list

# Terraformをインストール
sudo apt update && sudo apt install -y terraform

# バージョン確認
terraform version
```

### 1-4. 作業ディレクトリの作成

```bash
mkdir terraform-handson
cd terraform-handson
```

---

## 2. サーバ1台だけデプロイ

まずは最もシンプルな構成から。EC2インスタンス1台をデプロイします。

> **なぜこの工程から始めるのか？**
> Terraformの基本である`provider`（どのクラウドを使うか）と`resource`（何を作るか）の概念を理解するため。また、`init → plan → apply`という基本ワークフローを体験することで、IaCの「コードでインフラを定義し、コマンドで構築する」流れを掴む。

### 2-1. main.tfを作成

```terraform
provider "aws" {
  region = "ap-northeast-1"
}

resource "aws_instance" "example" {
  ami           = "ami-03852a41f1e05c8e4"  # Amazon Linux 2023（2025年11月時点）
  instance_type = "t2.micro"

  tags = {
    Name = "terraform-example"
  }
}
```

### 2-2. Terraformの基本コマンド

```bash
# プロバイダのダウンロード（初回のみ）
terraform init

# 実行計画を確認（何が作られるか）
terraform plan

# 実際に作成
terraform apply
# → "yes" と入力
```

### 2-3. 確認

```bash
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=terraform-example" \
  --query "Reservations[].Instances[].{ID:InstanceId,State:State.Name}" \
  --output table
```

### ここまでで学んだこと

| 要素 | 説明 |
|------|------|
| `provider` | どのクラウドを使うか |
| `resource` | 何を作るか |
| `terraform init` | 初期化（プロバイダのダウンロード） |
| `terraform plan` | 実行計画の確認 |
| `terraform apply` | 実際に適用 |

---

## 3. Webサーバ1台のデプロイ

EC2を起動しただけではアクセスできません。セキュリティグループを追加し、Webサーバを動かします。

> **なぜセキュリティグループが必要なのか？**
> AWSのEC2はデフォルトでインバウンド・アウトバウンドの両方のトラフィックを許可していない。外部からWebサーバにアクセスするには、セキュリティグループで明示的にポートを開放する必要がある。
>
> **なぜポート8080を使うのか？**
> 1024以下のポート（80など）でリッスンするにはroot権限が必要。セキュリティ上、一般ユーザー権限で起動できる8080を使用する。
>
> **なぜuser_dataを使うのか？**
> EC2起動時に自動でスクリプトを実行できる。手動でSSH接続してコマンドを打つ必要がなく、インフラ構築を完全に自動化できる。

### 3-1. main.tfを更新

```terraform
provider "aws" {
  region = "ap-northeast-1"
}

resource "aws_instance" "example" {
  ami           = "ami-03852a41f1e05c8e4"  # Amazon Linux 2023（2025年11月時点）
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.instance.id]

  user_data = <<-EOF
            #!/bin/bash
            cd /home/ec2-user
            echo "Hello, World" > index.html
            nohup python3 -m http.server 8080 &
            EOF

  user_data_replace_on_change = true

  tags = {
    Name = "terraform-example"
  }
}

resource "aws_security_group" "instance" {
  name = "terraform-example-instance"

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### 3-2. 適用と確認

```bash
terraform apply

# パブリックIPを取得
PUBLIC_IP=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=terraform-example" "Name=instance-state-name,Values=running" \
  --query "Reservations[].Instances[].PublicIpAddress" \
  --output text)

# アクセス確認
curl http://$PUBLIC_IP:8080
# → "Hello, World" が表示されればOK
```

### ここまでで学んだこと

| 要素 | 説明 |
|------|------|
| `user_data` | 起動時に実行するスクリプト |
| `aws_security_group` | ファイアウォール設定 |
| リソース参照 | `aws_security_group.instance.id`のように他リソースを参照 |

---

## 4. 設定変更可能なWebサーバのデプロイ

ポート番号がコード内に散らばっています。変数化してDRY原則を守ります。

> **なぜ変数化が必要なのか？**
> 現状、ポート番号`8080`がセキュリティグループとuser_dataの2箇所に書かれている。これはDRY原則（Don't Repeat Yourself）に違反しており、変更時に片方だけ修正し忘れるリスクがある。変数化することで、1箇所の変更ですべてに反映される。
>
> **出力変数（output）の用途は？**
> `terraform apply`後にパブリックIPなどの情報を自動表示できる。AWS CLIで毎回確認する手間が省け、他のTerraform構成の入力としても利用可能。

### 4-1. 変数を追加

```terraform
variable "server_port" {
  description = "The port the server will use for HTTP requests"
  type        = number
  default     = 8080
}
```

### 4-2. 変数を使う

セキュリティグループを修正：

```terraform
resource "aws_security_group" "instance" {
  name = "terraform-example-instance"

  ingress {
    from_port   = var.server_port
    to_port     = var.server_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

user_dataも修正：

```terraform
user_data = <<-EOF
          #!/bin/bash
          cd /home/ec2-user
          echo "Hello, World" > index.html
          nohup python3 -m http.server ${var.server_port} &
          EOF
```

### 4-3. 出力変数を追加

```terraform
output "public_ip" {
  value       = aws_instance.example.public_ip
  description = "The public IP of the web server"
}
```

### 4-4. 適用と確認

```bash
terraform apply

# 出力変数を確認
terraform output public_ip
```

### ここまでで学んだこと

| 要素 | 説明 |
|------|------|
| `variable` | 入力変数の定義 |
| `var.xxx` | 変数の参照 |
| `${var.xxx}` | 文字列内での補間 |
| `output` | 出力変数（apply後に表示） |

---

## 5. Webサーバのクラスタのデプロイ

1台だけでは単一障害点です。Auto Scaling Group（ASG）で複数台を管理します。

> **なぜASGが必要なのか？**
> サーバ1台のみの運用は単一障害点（SPOF）となり、障害発生時にサービスが完全停止するリスクがある。ASGを使えば、複数台のEC2を自動管理し、障害時も自動復旧できる。
>
> **なぜデータソース（data）を使うのか？**
> ASGはEC2を複数のサブネット（アベイラビリティゾーン）に分散配置する。既存のVPC/サブネット情報をTerraformで取得するために`data`ブロックを使用する。これにより、1つのAZに障害が発生しても他のAZで稼働を継続できる。
>
> **Launch Templateとは？**
> ASGが新しいEC2を起動する際のテンプレート。AMI、インスタンスタイプ、セキュリティグループ、user_dataなどを定義する。

### 5-1. データソースを追加

VPCとサブネットの情報を取得：

```terraform
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}
```

### 5-2. Launch Templateを追加

ASGが起動するインスタンスの設定：

```terraform
resource "aws_launch_template" "example" {
  image_id      = "ami-03852a41f1e05c8e4"  # Amazon Linux 2023（2025年11月時点）
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.instance.id]

  user_data = base64encode(<<-EOF
            #!/bin/bash
            cd /home/ec2-user
            echo "Hello, World" > index.html
            nohup python3 -m http.server ${var.server_port} &
            EOF
  )
}
```

### 5-3. ASGを追加

```terraform
resource "aws_autoscaling_group" "example" {
  vpc_zone_identifier = data.aws_subnets.default.ids

  launch_template {
    id      = aws_launch_template.example.id
    version = "$Latest"
  }

  min_size = 2
  max_size = 10

  tag {
    key                 = "Name"
    value               = "terraform-asg-example"
    propagate_at_launch = true
  }
}
```

### 5-4. 古いEC2リソースを削除

`aws_instance "example"` ブロックは削除してください。ASGがEC2を管理するようになります。

### 5-5. 適用と確認

```bash
terraform apply

# 2台のインスタンスを確認
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=terraform-asg-example" "Name=instance-state-name,Values=running" \
  --query "Reservations[].Instances[].{ID:InstanceId,IP:PublicIpAddress}" \
  --output table
```

### ここまでで学んだこと

| 要素 | 説明 |
|------|------|
| `data` | 既存リソースの情報を取得（読み取り専用） |
| `aws_launch_template` | EC2の起動設定 |
| `aws_autoscaling_group` | 自動スケーリング設定 |

---

## 6. ロードバランサのデプロイ

複数台のEC2に1つのエンドポイントでアクセスできるよう、ALBを追加します。

> **なぜロードバランサが必要なのか？**
> ASGで複数台のEC2を起動しても、ユーザーは各EC2のIPアドレスを知らない。ロードバランサを使えば、ユーザーは1つのDNS名（エンドポイント）にアクセスするだけで、トラフィックが自動的に複数のEC2に分散される。
>
> **ALBの構成要素**
> - **リスナ**：特定のポート（80）とプロトコル（HTTP）でリクエストを受け付ける
> - **ターゲットグループ**：リクエストを転送する先のEC2群。ヘルスチェックで正常なインスタンスのみに転送
> - **リスナルール**：リクエストのパスやホストに基づいて、どのターゲットグループに転送するか決定
>
> **なぜALB用のセキュリティグループが別途必要なのか？**
> ALBもAWSリソースなので、デフォルトでトラフィックを許可しない。ユーザーからのHTTPアクセス（インバウンド80）と、EC2へのヘルスチェック（アウトバウンド全ポート）を許可する設定が必要。

### 6-1. ALB用の変数を追加

```terraform
variable "alb_name" {
  description = "The name of the ALB"
  type        = string
  default     = "terraform-asg-example"
}

variable "alb_security_group_name" {
  description = "The name of the security group for the ALB"
  type        = string
  default     = "terraform-example-alb"
}
```

### 6-2. ALB用セキュリティグループを追加

```terraform
resource "aws_security_group" "alb" {
  name = var.alb_security_group_name

  # インバウンド：HTTP許可
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # アウトバウンド：すべて許可
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### 6-3. ALB本体を追加

```terraform
resource "aws_lb" "example" {
  name               = var.alb_name
  load_balancer_type = "application"
  subnets            = data.aws_subnets.default.ids
  security_groups    = [aws_security_group.alb.id]
}
```

### 6-4. ターゲットグループを追加

```terraform
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
```

### 6-5. リスナとルールを追加

```terraform
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

### 6-6. ASGにターゲットグループを紐付け

ASGリソースに2行追加：

```terraform
resource "aws_autoscaling_group" "example" {
  vpc_zone_identifier = data.aws_subnets.default.ids

  launch_template {
    id      = aws_launch_template.example.id
    version = "$Latest"
  }

  target_group_arns = [aws_lb_target_group.asg.arn]  # 追加
  health_check_type = "ELB"                          # 追加

  min_size = 2
  max_size = 10

  tag {
    key                 = "Name"
    value               = "terraform-asg-example"
    propagate_at_launch = true
  }
}
```

### 6-7. 出力変数を追加

```terraform
output "alb_dns_name" {
  value       = aws_lb.example.dns_name
  description = "The domain name of the load balancer"
}
```

### 6-8. 適用と確認

```bash
terraform apply

# ALBのDNS名を取得
terraform output alb_dns_name

# アクセス確認（ALB起動に数分かかる）
curl http://$(terraform output -raw alb_dns_name)
# → "Hello, World" が表示されればOK
```

### ここまでで学んだこと

| 要素 | 説明 |
|------|------|
| `aws_lb` | Application Load Balancer |
| `aws_lb_listener` | どのポートでリクエストを受けるか |
| `aws_lb_target_group` | リクエスト転送先のグループ |
| `aws_lb_listener_rule` | ルーティングルール |

---

## 7. 後片付け（環境削除）

IaCの大きなメリット：作った環境を一発で削除できます。

> **なぜterraform destroyが重要なのか？**
> AWSリソースは起動している限り課金が発生する。学習やテスト後は必ず削除してコストを抑える。手動で削除すると関連リソースの削除漏れが発生しやすいが、`terraform destroy`ならTerraformが依存関係を考慮して正しい順序で全リソースを削除してくれる。
>
> **IaCの真価**
> `main.tf`さえあれば、`terraform apply`でいつでも同じ環境を再構築できる。「環境構築手順書」が不要になり、環境の作成・削除が数分で完了する。

### 7-1. 全リソースを削除

```bash
terraform destroy
# → "yes" と入力
```

### 7-2. 確認

```bash
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=terraform-asg-example" \
  --query "Reservations[].Instances[].{ID:InstanceId,State:State.Name}" \
  --output table
# → terminated または空
```

---

## まとめ

### Terraformの基本ワークフロー

```
terraform init  →  terraform plan  →  terraform apply  →  terraform destroy
 (初期化)          (計画確認)          (適用)            (削除)
```

### 今回構築したリソース

| リソース | 用途 |
|----------|------|
| EC2 | Webサーバ |
| Security Group | ファイアウォール |
| Launch Template | EC2の起動設定 |
| Auto Scaling Group | EC2の自動管理 |
| ALB | ロードバランサ |
| Target Group | ALBの転送先 |

### IaC（Infrastructure as Code）のメリット

1. **再現性**：main.tfがあればいつでも同じ環境を構築可能
2. **可視性**：インフラ構成がコードとして明確
3. **効率性**：環境の作成・削除が数分で完了
4. **バージョン管理**：Gitで変更履歴を管理可能

---

## コマンドチートシート

| コマンド | 用途 |
|---------|------|
| `terraform init` | 初期化 |
| `terraform plan` | 実行計画確認 |
| `terraform apply` | 適用 |
| `terraform destroy` | 全削除 |
| `terraform output` | 出力変数表示 |
| `terraform validate` | 構文チェック |

---

## 完成版コード

<details>

<summary>クリックして展開：最終的なmain.tf</summary>

```terraform
provider "aws" {
  region = "ap-northeast-1"
}

# --- 変数 ---
variable "server_port" {
  description = "The port the server will use for HTTP requests"
  type        = number
  default     = 8080
}

variable "alb_name" {
  description = "The name of the ALB"
  type        = string
  default     = "terraform-asg-example"
}

variable "alb_security_group_name" {
  description = "The name of the security group for the ALB"
  type        = string
  default     = "terraform-example-alb"
}

# --- データソース ---
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# --- セキュリティグループ ---
resource "aws_security_group" "instance" {
  name = "terraform-example-instance"

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

# --- Launch Template & ASG ---
resource "aws_launch_template" "example" {
  image_id      = "ami-03852a41f1e05c8e4"  # Amazon Linux 2023（2025年11月時点）
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.instance.id]

  user_data = base64encode(<<-EOF
            #!/bin/bash
            cd /home/ec2-user
            echo "Hello, World" > index.html
            nohup python3 -m http.server ${var.server_port} &
            EOF
  )
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

# --- ALB ---
resource "aws_lb" "example" {
  name               = var.alb_name
  load_balancer_type = "application"
  subnets            = data.aws_subnets.default.ids
  security_groups    = [aws_security_group.alb.id]
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

# --- 出力 ---
output "alb_dns_name" {
  value       = aws_lb.example.dns_name
  description = "The domain name of the load balancer"
}
```

</details>

---

## 参考

- [詳解 Terraform 第3版 ―Infrastructure as Codeを実現する](https://www.oreilly.co.jp/books/9784814400522/)
  - 著者：Yevgeniy Brikman
  - 訳者：松浦 隼人
  - 出版社：オライリージャパン
  - 出版年：2023年
- [Terraform公式ドキュメント](https://developer.hashicorp.com/terraform/docs)
- [AWSプロバイダドキュメント](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
