+++
id = "251210212221"
date = '2025-12-10T21:22:21+09:00'
draft = false
title = 'EC2 + Security GroupをTerraformで構築'
tags = ["インフラ", "AWS", "Terraform", "ハンズオン・チュートリアル"]
+++
## 今日学んだこと

「Amazon Web Services 基礎からのネットワーク&サーバー構築」のハンズオンをTerraformで再構築しました。Security Groupでは「SGをソースに指定する」設計パターン、EC2ではdata sourceを使った最新AMIの動的取得を学びました。

## 学習内容

### 構築するリソース

| リソース | 名前 | 用途 |
|----------|------|------|
| Security Group | practice-web-sg | Webサーバー用（SSH, HTTP） |
| Security Group | practice-db-sg | 踏み台経由DB接続用（SSH, ICMP, MySQL） |
| Security Group | practice-rds-sg | RDS用（MySQLをWebサーバーからのみ許可） |
| EC2 | practice-web | パブリックサブネットに配置 |
| EC2 | practice-db | プライベートサブネットに配置（踏み台） |

### Security Groupの作成

#### 基本構造
```hcl
resource "aws_security_group" "web" {
  name        = "practice-web-sg"
  description = "Security group for practice web server"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "practice-web-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "web_ssh" {
  security_group_id = aws_security_group.web.id
  description       = "SSH access"
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "web_http" {
  security_group_id = aws_security_group.web.id
  description       = "HTTP access"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "web_all" {
  security_group_id = aws_security_group.web.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}
```

`aws_vpc_security_group_ingress_rule` はAWS Provider 5.xで推奨される新しいリソースタイプです。ルールごとに個別リソースになるため、変更時に他ルールへ影響しません。`ip_protocol = "-1"` は全プロトコル許可を意味します。

> **注意**: 上記の `cidr_ipv4 = "0.0.0.0/0"` は学習用の設定です。本番環境ではSSHアクセスを自分のIPアドレスに制限してください。

#### SGをソースに指定する

RDSへの接続元をIPではなくSGで指定することで、柔軟なアクセス制御を実現します。

```hcl
resource "aws_security_group" "rds" {
  name        = "practice-rds-sg"
  description = "Security group for practice RDS"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "practice-rds-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "rds_mysql" {
  security_group_id            = aws_security_group.rds.id
  description                  = "MySQL from web server"
  from_port                    = 3306
  to_port                      = 3306
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.web.id
}
```

`referenced_security_group_id` でIPアドレスではなくSGをソースに指定しています。

| 方法 | メリット | デメリット |
|------|----------|-----------|
| IPアドレス指定 | シンプル | EC2のIP変更時にSG更新が必要 |
| SG指定 | IP変更に強い、スケーリングに対応 | 設計の理解が必要 |

Auto ScalingでEC2が増減しても、同じSGが付与されていれば自動的にアクセス許可されます。

#### ICMPルール（ping用）
```hcl
resource "aws_vpc_security_group_ingress_rule" "db_icmp" {
  security_group_id = aws_security_group.db.id
  description       = "Ping"
  from_port         = -1
  to_port           = -1
  ip_protocol       = "icmp"
  cidr_ipv4         = "0.0.0.0/0"
}
```

ICMPは `from_port = -1`, `to_port = -1` で全ICMPタイプを許可します。

### EC2の作成

#### 最新AMIを動的取得
```hcl
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}
```

AMI IDをハードコードしない理由は以下のとおりです。

- AMI IDはリージョンごとに異なる
- 新しいAMIがリリースされると古いIDは非推奨になる
- data sourceで常に最新を取得すればメンテナンス不要

#### EC2インスタンス
```hcl
resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.web.id]
  key_name               = aws_key_pair.main.key_name

  tags = {
    Name = "practice-web"
  }
}

resource "aws_instance" "db" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.private_1.id
  vpc_security_group_ids = [aws_security_group.db.id]
  key_name               = aws_key_pair.main.key_name

  tags = {
    Name = "practice-db"
  }
}
```

`vpc_security_group_ids` はリスト形式で、複数SGを付与できます。パブリックサブネットのEC2は自動でパブリックIPを取得し、プライベートサブネットのEC2はパブリックIPなしとなります。

#### キーペア
```hcl
resource "aws_key_pair" "main" {
  key_name   = "practice-keypair"
  public_key = file("~/.ssh/practice-keypair.pub")

  tags = {
    Name = "practice-keypair"
  }
}
```

事前にローカルでSSH鍵を生成しておきます。
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/practice-keypair -N ""
```

Terraformには公開鍵のみ登録し、秘密鍵はローカルで管理します。

## まとめ

| トピック | 内容 |
|----------|------|
| 新しいSGリソース | `aws_vpc_security_group_ingress_rule` が推奨（ルール個別管理） |
| SGをソースに指定 | `referenced_security_group_id` でIP変更・スケーリングに強い設計 |
| data source | `data "aws_ami"` で最新AMIを動的取得 |
| ICMPルール | `from_port = -1`, `to_port = -1` で全ICMP許可 |
| キーペア | 公開鍵のみAWSに登録、秘密鍵はローカル管理 |

## 参考

- [Amazon Web Services 基礎からのネットワーク＆サーバー構築 改訂4版](https://www.nikkeibp.co.jp/atclpubmkt/book/22/295640/)
- [Terraform AWS Provider - Security Group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group)
- [Terraform AWS Provider - EC2 Instance](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance)
- [AWS Security Group ドキュメント](https://docs.aws.amazon.com/ja_jp/vpc/latest/userguide/vpc-security-groups.html)