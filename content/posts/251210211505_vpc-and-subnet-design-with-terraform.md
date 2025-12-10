+++
id = "251210211505"
date = '2025-12-10T21:15:05+09:00'
draft = false
title = 'VPCとサブネット設計をTerraformで構築する'
tags = ["インフラ", "AWS", "Terraform", "ハンズオン・チュートリアル"]
+++
## 今日学んだこと

「Amazon Web Services 基礎からのネットワーク&サーバー構築」のハンズオンをTerraformで再構築しました。VPCとサブネットの設計から、パブリック/プライベートの違いがルートテーブルの設定で決まることを実践を通じて理解しました。

## 学習内容

### 構築するリソース

| リソース | 名前 | CIDR / AZ |
|----------|------|-----------|
| VPC | practice-vpc | 10.0.0.0/16 |
| パブリックサブネット | practice-public-subnet | 10.0.1.0/24 (ap-northeast-1a) |
| パブリックサブネット2 | practice-public-subnet-2 | 10.0.4.0/24 (ap-northeast-1c) |
| プライベートサブネット | practice-private-subnet | 10.0.2.0/24 (ap-northeast-1a) |
| プライベートサブネット2 | practice-private-subnet-2 | 10.0.3.0/24 (ap-northeast-1c) |
| Internet Gateway | practice-igw | - |
| ルートテーブル（パブリック） | practice-public-rt | 0.0.0.0/0 → IGW |
| ルートテーブル（プライベート） | practice-private-rt | ローカルのみ |

### VPCの作成
```hcl
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "practice-vpc"
  }
}
```

`enable_dns_hostnames = true` を設定することで、EC2にパブリックDNS名が割り当てられます。AWSコンソールでは「VPCの設定を編集」から有効化する操作が必要ですが、Terraformでは属性1つで完結します。

### サブネットの作成
```hcl
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "ap-northeast-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "practice-public-subnet"
  }
}

resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "ap-northeast-1a"

  tags = {
    Name = "practice-private-subnet"
  }
}
```

`map_public_ip_on_launch = true` はパブリックサブネットのみに設定します。プライベートサブネットにはパブリックIPが不要なため設定しません。

### Internet Gatewayの作成
```hcl
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "practice-igw"
  }
}
```

Terraformでは `vpc_id` を指定するだけでIGW作成とVPCへのアタッチが同時に実行されます。AWSコンソールでは「作成」→「VPCにアタッチ」の2ステップが必要な操作です。

### ルートテーブルの作成
```hcl
# パブリック用
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "practice-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# プライベート用
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "practice-private-rt"
  }
}

resource "aws_route_table_association" "private_1" {
  subnet_id      = aws_subnet.private_1.id
  route_table_id = aws_route_table.private.id
}
```

パブリックルートテーブルには `0.0.0.0/0 → IGW` のルートを設定し、プライベートルートテーブルにはローカルルート（10.0.0.0/16）のみを設定します。このIGWへのルートがあるかどうかがパブリック/プライベートの違いになります。

### なぜ2AZ構成にしたか

ALBは最低2つのAZが必要であり、RDSのDBサブネットグループも2AZ必須です。本番環境を意識した設計として、最初から2AZ構成にしました。

## まとめ

| トピック | 内容 |
|----------|------|
| パブリック/プライベートの違い | サブネット作成時点では同じ。ルートテーブルにIGWへのルートがあるかで決まる |
| DNS設定 | `enable_dns_hostnames = true` でパブリックDNS名が割り当てられる |
| IGWアタッチ | Terraformでは `vpc_id` 指定でアタッチまで完了 |
| 明示的な関連付け | ルートテーブルにサブネットを関連付けないと、メインルートテーブルが適用される |

## 参考

- [Amazon Web Services 基礎からのネットワーク＆サーバー構築 改訂4版](https://www.nikkeibp.co.jp/atclpubmkt/book/22/295640/)
- [Terraform AWS Provider - VPC](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc)
- [AWS VPC ドキュメント](https://docs.aws.amazon.com/ja_jp/vpc/latest/userguide/what-is-amazon-vpc.html)