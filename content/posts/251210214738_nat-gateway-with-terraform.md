+++
id = "251210214738"
date = '2025-12-10T21:47:38+09:00'
draft = false
title = 'NAT GatewayをTerraformで構築'
tags = ["インフラ", "AWS", "Terraform", "ハンズオン・チュートリアル"]
+++
## 今日学んだこと

プライベートサブネットのEC2からインターネットにアクセスするためのNAT GatewayをTerraformで構築しました。NAT Gatewayはパブリックサブネットに配置する必要があること、`depends_on` で暗黙的な依存関係を明示する必要があることを学びました。

## 学習内容

### NAT Gatewayの役割
```
プライベートサブネットのEC2
    ↓ (送信)
NAT Gateway（パブリックサブネット）
    ↓
Internet Gateway
    ↓
インターネット
```

- **アウトバウンド**: プライベート → インターネット（許可）
- **インバウンド**: インターネット → プライベート（拒否）

プライベートサブネットのEC2からyum/dnf update等を実行したいが、インターネットからの直接アクセスは許可したくない場合に使用します。

### 構築するリソース

| リソース | 名前 | 説明 |
|----------|------|------|
| Elastic IP | practice-nat-eip | NAT Gateway用の固定IP |
| NAT Gateway | practice-nat | パブリックサブネットに配置 |
| Route | - | プライベートRT → NAT Gateway |

### Elastic IPの作成
```hcl
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "practice-nat-eip"
  }

  depends_on = [aws_internet_gateway.main]
}
```

`domain = "vpc"` でVPC用のElastic IPを作成します。旧構文の `vpc = true` は非推奨です。

### NAT Gatewayの作成
```hcl
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id

  tags = {
    Name = "practice-nat"
  }

  depends_on = [aws_internet_gateway.main]
}
```

NAT GatewayはInternet Gateway（IGW）経由でインターネットに接続するため、IGWがアタッチされたVPC内のパブリックサブネットに配置する必要があります。

### プライベートルートテーブルにルート追加
```hcl
resource "aws_route" "private_nat" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main.id
}
```

| ルートテーブル | 0.0.0.0/0 の宛先 | 結果 |
|---------------|-----------------|------|
| パブリック | Internet Gateway | 直接インターネット通信 |
| プライベート | NAT Gateway | NAT経由でインターネット通信 |

### depends_onの意味
```hcl
depends_on = [aws_internet_gateway.main]
```

Terraformは通常、リソース間の依存関係を自動検出します。しかし、NAT Gateway → IGWの依存関係は暗黙的（コード上の参照がない）なため、明示的に指定する必要があります。

| 状況 | depends_onの要否 |
|------|-----------------|
| `subnet_id = aws_subnet.public.id` | 不要（参照あり） |
| IGWが存在しないとNATが動作しない | 必要（参照なし） |

### コストに注意

| 項目 | 料金（東京リージョン、2024年12月時点） |
|------|---------------------|
| NAT Gateway時間料金 | 約$0.062/時（約$45/月） |
| データ処理料金 | $0.062/GB |

学習環境では使わない時間帯は `terraform destroy` で削除することを推奨します。

### 代替手段との比較

| 方法 | コスト | 管理負担 | 可用性 |
|------|--------|---------|--------|
| NAT Gateway | 高 | 低（マネージド） | 高 |
| NATインスタンス | 低 | 高（自前EC2） | 中 |
| VPCエンドポイント | 低 | 低 | 高（AWSサービスのみ） |

本番環境ではNAT Gateway推奨、学習/開発でコスト重視ならNATインスタンスも選択肢になります。S3/DynamoDB等のAWSサービスのみならVPCエンドポイントで十分です。

### 動作確認

プライベートサブネットのEC2にSSH接続（踏み台経由）して確認します。
```bash
# インターネット接続確認
ping -c 3 google.com

# NAT Gateway経由で通信していることを確認
curl ifconfig.me
# → Elastic IPが表示されればNAT Gateway経由

# パッケージ更新が可能か確認
sudo dnf check-update
```

## まとめ

| トピック | 内容 |
|----------|------|
| NAT Gatewayの配置 | パブリックサブネット（IGWへのルートが必要） |
| depends_on | 暗黙的な依存関係を明示的に指定 |
| Elastic IP | `domain = "vpc"` で作成 |
| コスト | 約$45/月。学習時は削除推奨 |
| 代替手段 | NATインスタンス、VPCエンドポイント |

## 参考

- [Amazon Web Services 基礎からのネットワーク＆サーバー構築 改訂4版](https://www.nikkeibp.co.jp/atclpubmkt/book/22/295640/)
- [Terraform AWS Provider - NAT Gateway](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/nat_gateway)
- [AWS NAT Gateway ドキュメント](https://docs.aws.amazon.com/ja_jp/vpc/latest/userguide/vpc-nat-gateway.html)
- [NAT Gateway 料金](https://aws.amazon.com/jp/vpc/pricing/)