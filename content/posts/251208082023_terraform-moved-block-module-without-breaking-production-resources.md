+++
id = "251208082023"
date = '2025-12-08T08:20:23+09:00'
draft = false
title = 'Terraform movedブロックでリソースを壊さずにmodule化する'
tags = ["インフラ", "Terraform", "AWS", "実践"]
+++
## 今日学んだこと

Terraform movedブロックを使って、既存のTerraformリソースをダウンタイムなしでmodule化しました。movedブロックはStateの参照先だけを変更し、実リソースには触れずにリファクタリングできる機能です。

## 学習内容

### 背景と課題

個人プロジェクトで構築したAWSインフラ（S3、CloudFront、IAM等）をTerraform module化したいと考えました。最初は`environments/prod/`に全リソースをベタ書きしていましたが、再利用性と可読性のためにmodule構成に移行することにしました。

しかし、単純にmoduleに移動すると、Terraformは「旧リソースを削除 → 新規作成」と判断します。本番稼働中のサイトでダウンタイムが発生してしまう問題がありました。

### movedブロックとは

Terraform 1.1で導入された機能です。Stateの参照先だけを変更し、実リソースには触らずにリファクタリングできます。

```hcl
moved {
  from = aws_s3_bucket.content                    # 旧パス
  to   = module.s3_content.aws_s3_bucket.this     # 新パス
}
```

### 実践：S3バケットのmodule化

#### Step 1: moduleと呼び出し元の構成

```
├── environments/prod/
│   └── main.tf              ← movedブロックを記述
└── modules/s3-content/
    ├── main.tf
    ├── outputs.tf
    └── variables.tf
```

#### Step 2: module呼び出しとmovedブロックを記述

```hcl
# environments/prod/main.tf

module "s3_content" {
  source      = "../../modules/s3-content"
  bucket_name = "example-content"
}

# State移行
moved {
  from = aws_s3_bucket.content
  to   = module.s3_content.aws_s3_bucket.this
}

moved {
  from = aws_s3_bucket_public_access_block.content
  to   = module.s3_content.aws_s3_bucket_public_access_block.this
}
```

#### Step 3: terraform planで確認

```bash
$ terraform plan
# Terraform will perform the following actions:
#   # aws_s3_bucket.content has moved to module.s3_content.aws_s3_bucket.this
# Plan: 0 to add, 0 to change, 0 to destroy.
```

`0 to add, 0 to change, 0 to destroy`と表示されれば成功です。Stateの参照が変わるだけで、S3バケット自体は変更されません。

#### Step 4: terraform apply

```bash
$ terraform apply
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
```

### ハマったポイント

#### 動的な名前生成による再作成

module内でリソース名を動的生成すると、既存リソースと名前が変わって再作成が発生することがあります。

```hcl
# ❌ これだと再作成が発生する可能性
resource "aws_cloudfront_function" "this" {
  name = "${var.name_prefix}-url-rewrite"
}
```

解決策として、変数で既存の名前を明示的に渡します。

```hcl
# ✅ 既存名を変数で渡す
variable "function_name" {
  type = string
}

resource "aws_cloudfront_function" "this" {
  name = var.function_name
}
```

#### movedブロックはapply後に削除可能

movedブロックはapply後、Stateに反映済みであれば削除して問題ありません。残しておくとコードが煩雑になるため、適宜整理します。

#### data sourceはmovedブロック不要

既存リソースを参照するだけの`data source`はState移行が不要です。そのままmodule化できます。

```hcl
# 参照のみなのでmovedブロック不要
data "aws_acm_certificate" "this" {
  domain      = var.domain_name
  statuses    = ["ISSUED"]
  most_recent = true
}
```

## まとめ

| ポイント | 内容 |
|----------|------|
| movedブロックの用途 | 既存リソースを壊さずにmodule化・リネーム |
| 成功の確認方法 | `Plan: 0 to add, 0 to change, 0 to destroy` |
| apply後の扱い | movedブロックは削除可能 |
| data sourceの扱い | 参照のみなのでState移行不要 |
| 名前変更に注意 | 動的生成で名前が変わると再作成される |

## 補足：個人開発でmodule化は必要だったか？

正直、現段階のプロジェクトでは不要だったと思います。\
今回はブログ環境をAWSへ移行するプロジェクトでmovedブロックを使用しました。\
ただ、以下の理由でmodule化を選択しました。

| 観点 | 理由 |
|------|------|
| 将来の拡張性 | テスト実装やセキュリティスキャン導入時、module単位で検証できる |
| 実務経験の代替 | 実務ではmodule化が一般的。設計パターンを経験しておきたかった |
| 学習効果 | movedブロック、マルチリージョンprovider、依存関係設計を一度に学べた |

「今必要か」だけでなく「将来拡張しやすいか」「学習として価値があるか」も判断軸に入れました。

## 参考

- [Refactoring - Terraform](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)
- [Terraform のつまずきポイントと回避策](/posts/251202083121_terraform-stumbling-points-and-solutions/)