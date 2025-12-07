+++
id = "251207230407"
date = '2025-12-07T23:04:07+09:00'
draft = false
title = 'TerraformでGoogle Search ConsoleのDNS検証を管理する'
tags = ["インフラ", "AWS", "Terraform", "Google", "実践"]
+++
## 今日学んだこと

Google Search Consoleのドメイン所有権検証をTerraformで管理する方法を学びました。DNS検証（TXTレコード）を選択することで、IaCの一貫性を保ちながらSearch Consoleの設定を行えます。

## 前提条件

- AWSアカウントを持っている
- Route53でホストゾーンが作成済み
- Terraformの基本操作（init, plan, apply）を理解している

## 学習内容

### 検証方式の選択

Google Search Consoleには複数の所有権検証方式があります。

| 検証方式 | 概要 | Terraform管理 |
|----------|------|---------------|
| DNS検証（TXTレコード） | ドメインのDNSにTXTレコードを追加 | ✅ 可能 |
| HTMLファイル | 指定されたHTMLファイルをサイトに配置 | △ ビルドに含める必要あり |
| metaタグ | HTMLのheadにmetaタグを追加 | △ テンプレート修正が必要 |
| Google Analytics | 既存のGA設定を利用 | ❌ 不可 |

IaCの一貫性を保つため、DNS検証を採用しました。

### 実装手順

#### Step 1: Google Search ConsoleでTXTレコード値を取得

1. [Google Search Console](https://search.google.com/search-console)にアクセス
2. 「プロパティを追加」→「ドメイン」を選択
3. ドメイン名を入力
4. 表示されたTXTレコード値をコピー

取得できる値の形式：
```
google-site-verification=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### Step 2: Terraformコードの作成

以下は、Route53にGoogle Search Console検証用のTXTレコードを作成するコード例です。

> **注意**: このコードは個人プロジェクトで使用したものです。実際に利用する際は、ご自身の環境に合わせて調整してください。

**variables.tf**
```hcl
variable "domain_name" {
  description = "ドメイン名"
  type        = string
}

variable "google_site_verification" {
  description = "Google Search Console検証用のTXTレコード値"
  type        = string
}
```

**main.tf**
```hcl
data "aws_route53_zone" "this" {
  name = var.domain_name
}

resource "aws_route53_record" "google_site_verification" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = var.domain_name
  type    = "TXT"
  ttl     = 300
  records = [var.google_site_verification]
}
```

**terraform.tfvars**
```hcl
domain_name              = "example.com"
google_site_verification = "google-site-verification=XXXXXXXXXXXX"
```

#### Step 3: Terraform適用
```bash
terraform plan
terraform apply
```

#### Step 4: Search Consoleで検証完了

Google Search Consoleに戻り、「確認」ボタンをクリックします。DNSの反映には数分かかる場合があります。

## まとめ

- Google Search ConsoleのDNS検証はTerraformで管理可能
- TXTレコードをRoute53に追加することで所有権を証明
- DNS検証は一度設定すれば永続的に有効

## 参考

- [Search Console ヘルプ - ドメイン プロパティを追加する](https://support.google.com/webmasters/answer/9008080)
- [Terraform AWS Provider - aws_route53_record](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route53_record)
- [fumi-til-infrastructure - GitHub](https://github.com/mr110825/fumi-til-infrastructure)