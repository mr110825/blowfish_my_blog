+++
id = "251210215023"
date = '2025-12-10T21:50:23+09:00'
draft = false
title = 'RDS（MySQL）をTerraformで構築'
tags = ["インフラ", "AWS", "Terraform", "ハンズオン・チュートリアル"]
+++
## 今日学んだこと

TerraformでRDS（MySQL）を構築しました。DBサブネットグループにはシングルAZ構成でも2つの異なるAZのサブネットが必須であること、パスワード管理の本番向け手法を学びました。

## 学習内容

### 背景

「Amazon Web Services 基礎からのネットワーク&サーバー構築」ではEC2上にMariaDBを構築していましたが、実務ではマネージドサービスのRDSを使うことが多いため、Terraformで構築しました。

### 構築するリソース

| リソース | 名前 | 説明 |
|----------|------|------|
| DB Subnet Group | practice-db-subnet-group | RDS配置用（2AZ必須） |
| RDS Instance | practice-db-instance | MySQL 8.0 |

### DBサブネットグループの作成
```hcl
resource "aws_db_subnet_group" "main" {
  name       = "practice-db-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "practice-db-subnet-group"
  }
}
```

RDSはDBサブネットグループに最低2つの異なるAZのサブネットを要求します。これはマルチAZ配置でなくても必須です。

| 設定 | サブネット要件 | 理由 |
|------|---------------|------|
| シングルAZ | 2AZ必須 | 将来のマルチAZ化に備えた設計 |
| マルチAZ | 2AZ必須 | スタンバイを別AZに配置 |

### RDSインスタンスの作成
```hcl
resource "aws_db_instance" "main" {
  identifier     = "practice-db-instance"
  engine         = "mysql"
  engine_version = "8.0"

  instance_class    = "db.t3.micro"
  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = "wordpress"
  username = "admin"
  password = "YourPassword123!"  # 学習用

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible = false
  skip_final_snapshot = true  # 学習用

  tags = {
    Name = "practice-db-instance"
  }
}
```

### 設定項目の解説

#### 基本設定

| 項目 | 値 | 説明 |
|------|-----|------|
| identifier | practice-db-instance | RDSの識別子（エンドポイント名に使用） |
| engine | mysql | DBエンジン（mysql, postgres, mariadb等） |
| engine_version | 8.0 | メジャーバージョン指定（マイナーは自動） |

#### インスタンス設定

| 項目 | 値 | 説明 |
|------|-----|------|
| instance_class | db.t3.micro | インスタンスタイプ（無料枠対象） |
| allocated_storage | 20 | ストレージ容量（GB） |
| storage_type | gp2 | 汎用SSD（gp3も選択可） |

#### セキュリティ設定

| 項目 | 値 | 説明 |
|------|-----|------|
| publicly_accessible | false | インターネットから直接アクセス不可 |
| vpc_security_group_ids | [rds-sg] | SGでアクセス制御 |

`publicly_accessible = false` を設定するとパブリックIPが付与されず、VPC内からのみ接続可能になります。本番環境では基本的にfalseを設定します。

### 学習用と本番用の設定の違い

| 項目 | 学習用 | 本番推奨 |
|------|--------|---------|
| password | 直書き | Secrets Manager or 変数 |
| skip_final_snapshot | true | false（削除時にスナップショット作成） |
| deletion_protection | なし | true（誤削除防止） |
| multi_az | false | true（高可用性） |
| backup_retention_period | 0 | 7以上（自動バックアップ） |

### パスワード管理（本番向け）

#### 方法1: 変数で外部化
```hcl
variable "db_password" {
  type      = string
  sensitive = true
}

resource "aws_db_instance" "main" {
  # ...
  password = var.db_password
}
```
```bash
# 実行時に指定
terraform apply -var="db_password=SecurePassword123!"
```

#### 方法2: Secrets Manager（推奨）
```hcl
data "aws_secretsmanager_secret_version" "db" {
  secret_id = "prod/db/password"
}

resource "aws_db_instance" "main" {
  # ...
  password = jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)["password"]
}
```

### Security Group設計（復習）
```hcl
resource "aws_vpc_security_group_ingress_rule" "rds_mysql" {
  security_group_id            = aws_security_group.rds.id
  description                  = "MySQL from web server"
  from_port                    = 3306
  to_port                      = 3306
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.web.id
}
```

WebサーバーのSGをソースに指定することで、Webサーバーからのみ接続を許可します。

### 作成にかかる時間

RDSは作成に5〜10分かかります。`terraform apply` 実行後、気長に待ちます。
```
aws_db_instance.main: Still creating... [5m0s elapsed]
aws_db_instance.main: Still creating... [5m10s elapsed]
aws_db_instance.main: Creation complete after 5m15s
```

### 接続確認

WebサーバーからRDSに接続します。
```bash
# WebサーバーにSSH接続後
mysql -h practice-db-instance.xxxxx.ap-northeast-1.rds.amazonaws.com \
      -u admin -p
# パスワード入力後
mysql> use wordpress;
```

エンドポイントは `terraform output` またはAWSコンソールで確認できます。

```hcl
output "rds_endpoint" {
  value = aws_db_instance.main.endpoint
}
```

### EC2上のDB vs RDS

| 観点 | EC2上のDB | RDS |
|------|----------|-----|
| 管理負担 | 高（パッチ、バックアップ自前） | 低（マネージド） |
| 可用性 | 自前で構築 | マルチAZオプションあり |
| コスト | 低め | 高め |
| 柔軟性 | 高（何でもできる） | 制限あり |

基本はRDS推奨です。特殊な要件がある場合のみEC2を検討します。

## まとめ

| トピック | 内容 |
|----------|------|
| DBサブネットグループ | 2AZ必須（シングルAZ構成でも） |
| publicly_accessible | false でVPC内からのみ接続 |
| skip_final_snapshot | 学習用はtrue、本番はfalse |
| パスワード管理 | 直書きは学習のみ。本番はSecrets Manager |
| 作成時間 | 5〜10分かかる |

## 参考

- [Amazon Web Services 基礎からのネットワーク＆サーバー構築 改訂4版](https://www.nikkeibp.co.jp/atclpubmkt/book/22/295640/)
- [Terraform AWS Provider - RDS Instance](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_instance)
- [Terraform AWS Provider - DB Subnet Group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_subnet_group)
- [AWS RDS ドキュメント](https://docs.aws.amazon.com/ja_jp/AmazonRDS/latest/UserGuide/Welcome.html)