+++
id = "251203194515"
date = '2025-12-03T19:45:15+09:00'
draft = false
title = 'Terraform tfstate管理の鶏と卵問題'
tags = ["インフラ", "Terraform", "AWS", "実践"]
+++
## 今日学んだこと

Terraformでリモートバックエンド（S3 + DynamoDB）を使う場合、
「tfstate用のS3/DynamoDBだけは先に別で作る」必要があることを学びました。
これは「鶏と卵問題」と呼ばれます。

## 学習内容

### 鶏と卵問題とは

```
Terraformで S3, CloudFront, Route53... を作りたい
↓
tfstateをS3に保存したい
↓
でも、そのS3自体をTerraformで作ると...
↓
「tfstate用S3のtfstate」はどこに保存する？ ← 無限ループ
```

この循環参照を断ち切るため、**tfstate用のS3/DynamoDBだけは最初に別で作成**します。

### 各リソースの役割

| サービス | 役割 |
|----------|------|
| S3 | tfstateファイルの保存場所 |
| DynamoDB | ロック機構（同時編集防止） |

### 解決策：backend-setupディレクトリ

```
fumi-til-infrastructure/
├── backend-setup/          ← 最初にこれだけ実行
│   ├── main.tf
│   └── terraform.tfstate   ← ローカルに残る
└── environments/
    └── prod/               ← backend-setup完了後に実行
        └── main.tf
```

### 注意点

- `backend-setup`自体のtfstateは**ローカルに残る**
- `.gitignore`で除外しつつ、ローカルで大切に保管

## 補足：この方法は唯一の正解ではない

本記事で紹介した「backend-setupディレクトリでtfstate用インフラを作成する」方法は、**よく使われる方法の一つ**ですが、唯一の正解ではありません。

Terragruntの開発元であるGruntworkの公式ディスカッションでは、以下の方法が並列で紹介されています。

| 方法 | 概要 | メリット | デメリット |
|------|------|----------|------------|
| 手動作成（コンソール/CLI） | AWSコンソールやCLIで直接作成 | シンプル、鶏と卵問題なし | IaC原則に反する、手順が残らない |
| Terraformで作成（本記事の方式） | 別ディレクトリでTerraform管理 | IaCで管理可能 | ローカルtfstateの管理が課題 |
| CloudFormation/CDK | AWSネイティブツールで作成 | AWS内で完結 | ツール混在 |
| Terragrunt | 自動でバックエンド作成 | DRY、環境管理が楽 | 学習コスト |
| Terraform Cloud/Enterprise | マネージドサービス | 運用が楽 | 有料 |

### Gruntworkの見解

Gruntworkのディスカッションでは、手動作成について以下のように述べられています。

> 「これは始めるための簡単な方法です。管理するバックエンドが少数（例：会社全体で1〜3個のS3バケットのみ）であれば、このアプローチで十分うまくいきます。」

一方で、手動作成のデメリットとして「手動プロセスである」「すべてのインフラをコードで管理できていない」「バックエンドのセットアップ方法がドキュメント化されない」も指摘されています。

ディスカッションの内容を自分なり解釈すると「規模が小さい場合はS3/DynamoDBなどを使用する。開発規模が大きくなり、自動化などが必要の場合はTerragruntによる自動作成がおすすめ」という印象でした。

### 状況別の推奨

| 状況 | 推奨方法 |
|------|----------|
| 個人開発・学習 | 手動作成 or Terraform（本記事の方式） |
| 小規模チーム | Terraform + tfstateをS3に手動コピー |
| 中規模以上 | Terragrunt or Terraform Cloud |
| エンタープライズ | Terraform Cloud/Enterprise |

重要なのは、**チームの規模やスキルセットに合った方法を選ぶこと**です。

## まとめ

- tfstate用のS3/DynamoDBは「先に別で作る」必要がある（鶏と卵問題）
- backend-setup自体のtfstateはローカル管理となる
- S3は保存、DynamoDBはロックの役割
- 本記事の方法は「よく使われる方法の一つ」であり、状況に応じて他の方法も検討すべき

## 参考

- [Terraformステート管理 Part1 - S3リモートバックエンドとワークスペース](/posts/251128185824_terraform-state-management-intro/)
- [Backend Configuration - Terraform](https://developer.hashicorp.com/terraform/language/settings/backends/configuration)
- [How should I create the backend for storing Terraform state? - Gruntwork Discussion](https://github.com/orgs/gruntwork-io/discussions/769)
- [Initial setup of terraform backend using terraform - Stack Overflow](https://stackoverflow.com/questions/47913041/initial-setup-of-terraform-backend-using-terraform)
