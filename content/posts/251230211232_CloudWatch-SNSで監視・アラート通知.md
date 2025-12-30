---
id: "251230211232"
title: "【Hugo×AWS】CloudWatch+SNSで監視・アラート通知"
date: 2025-12-30T21:12:32+09:00
draft: false
tags: ["学習・作業ログ", "AWS", "Terraform", "Hugo"]
series: [Hugo-S3-CloudFrontで技術ブログを公開する]
series_order: 3
---

## はじめに

この記事では、CloudFrontで配信している技術ブログに監視・アラート通知の仕組みを構築します。
CloudWatchでメトリクスを可視化し、エラー率が閾値を超えた場合にSNS経由でメール通知を送信します。
また、AWS Budgetsでコスト監視も設定します。

### この記事で構築するもの

- CloudWatchダッシュボード（リクエスト数、エラー率、キャッシュヒット率の可視化）
- CloudWatchアラーム（エラー率が閾値を超えたらメール通知）
- AWS Budgets（月額コストが閾値を超えたらメール通知）

### 想定する読者

- 前回までの記事でS3 + CloudFront + GitHub Actionsを構築済みの方
- サイトの監視・アラートを設定したい方
- AWS初心者〜中級者

## 完成イメージ

![CloudWatch+SNSで監視・アラート通知](/img/hugo-aws-3.png)

「何か問題があったらメールで知らせてくれる」仕組みを構築します。

## シリーズ全体像

【Hugo×AWS】シリーズ全体で5記事投稿予定です。今回の記事は3本目です。

| # | タイトル | 内容 |
|---|----------|------|
| 1 | Hugo + S3 + CloudFrontで技術ブログを公開する | Hugo環境構築〜手動デプロイまで |
| 2 | GitHub Actions + OIDCで自動デプロイ | CI/CD構築、アクセスキー不要の認証 |
| **3** | **CloudWatch + SNSで監視・アラート通知** | **ダッシュボード、エラー率アラーム** |
| 4 | Athenaでアクセスログを分析する | CloudFrontログのSQL分析 |
| 5 | 独自ドメインを設定する（Route53 + ACM） | カスタムドメイン、HTTPS |

## なぜ監視が必要なのか

個人ブログでも監視は重要です。

| 監視しないと... | 監視していれば... |
|----------------|------------------|
| エラーに気づかない | 即座にメールで通知される |
| 原因調査に時間がかかる | ダッシュボードで状況を把握 |
| 予想外のコストが発生 | 閾値超過で早期に検知 |

特にCloudFrontは「動いているように見えて実はエラーが出ている」ことがあります。
定期的にダッシュボードを確認し、異常時にはアラートで検知できる仕組みを作りましょう。

## 前提条件

### 必要な環境

本記事は、これまでの記事で以下が構築済みであることを前提としています。

- S3バケット（コンテンツ用）
- CloudFront Distribution
- Terraformプロジェクト

### 必要な情報

Terraformの出力値から以下を確認してください。

```bash
cd hugo-s3-demo-infra/prod
terraform output
```

```text
cloudfront_distribution_id = "E2XXXXXXXXXX"
```

### us-east-1 provider の追加

CloudFrontのメトリクスは `us-east-1` リージョンにのみ存在します。
CloudWatch AlarmとSNS Topicも同じリージョンに作成する必要があるため、`main.tf` に以下を追記します。

```hcl
# CloudFront metrics are only available in us-east-1
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}
```

:::message alert
この設定がないと、CloudWatch Alarmがメトリクスを取得できず、アラームが機能しません。
CloudFrontメトリクスは `us-east-1` 固定であり、他リージョンのCloudWatch Alarmからは参照できないためです。
:::

## SNSトピックの作成

まず、アラート通知の送信先となるSNSトピックを作成します。

### SNSとは

Amazon SNS（Simple Notification Service）は、メッセージの配信を行うフルマネージドサービスです。
Pub/Sub（発行/購読）モデルで、1つのトピックに対して複数の購読者（メール、SMS、Lambda等）を設定できます。

```
CloudWatch Alarm → SNS Topic → Email
                           → SMS
                           → Lambda
                           → etc...
```

### ディレクトリ構成

前回までのTerraformプロジェクトに `sns.tf` を追加します。

```text
hugo-s3-demo-infra/
└── prod/
    ├── versions.tf
    ├── backend.tf
    ├── variables.tf
    ├── main.tf          ← us-east-1 provider追記
    ├── iam.tf
    ├── outputs.tf
    ├── sns.tf           ← 新規作成
    └── terraform.tfvars ← 新規作成
```

### sns.tf

```hcl
# ===========================================
# SNS Topic（通知の送信先）
# us-east-1に作成（CloudFrontメトリクスと同じリージョン）
# ===========================================
resource "aws_sns_topic" "alerts" {
  provider = aws.us_east_1
  name     = "${var.project_name}-alerts"

  tags = {
    Name = "${var.project_name}-alerts"
  }
}

# ===========================================
# メールアドレス変数
# ===========================================
variable "alert_email" {
  description = "Email address for alerts"
  type        = string
  sensitive   = true
}

# ===========================================
# SNS Subscription（メール通知設定）
# ===========================================
resource "aws_sns_topic_subscription" "email" {
  provider  = aws.us_east_1
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ===========================================
# Output
# ===========================================
output "sns_topic_arn" {
  description = "SNS Topic ARN for CloudWatch Alarms"
  value       = aws_sns_topic.alerts.arn
}
```

### コード解説

#### SNS Topic

```hcl
resource "aws_sns_topic" "alerts" {
  provider = aws.us_east_1
  name     = "${var.project_name}-alerts"
}
```

SNSトピックは、通知メッセージの送信先を束ねる「トピック」です。
CloudWatchアラームやAWS Budgetsからこのトピックに通知を送信し、購読者（メール等）に配信します。

`provider = aws.us_east_1` を指定することで、CloudFrontメトリクスと同じリージョンにSNSトピックを作成します。

#### sensitive変数

```hcl
variable "alert_email" {
  description = "Email address for alerts"
  type        = string
  sensitive   = true
}
```

`sensitive = true` を設定すると、`terraform plan/apply` の出力でメールアドレスがマスクされます。
機密情報を扱う変数には必ず設定しましょう。

#### SNS Subscription

```hcl
resource "aws_sns_topic_subscription" "email" {
  provider  = aws.us_east_1
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}
```

| 属性 | 説明 |
|------|------|
| `provider` | リソースを作成するリージョン（us-east-1） |
| `protocol` | 通知方式（email, sms, lambda, https等） |
| `endpoint` | 通知先（メールアドレス、電話番号等） |

### terraform.tfvars

機密情報を含む変数は `terraform.tfvars` に記載します。

```hcl
alert_email = "your-email@example.com"
```

:::message alert
`terraform.tfvars` には機密情報が含まれるため、`.gitignore` に追加してGit管理対象外にしてください。
:::

### 実行と購読確認

```bash
terraform plan
terraform apply
```

実行後、指定したメールアドレスに「AWS Notification - Subscription Confirmation」というメールが届きます。

:::message
メール内の「**Confirm subscription**」リンクをクリックして購読を確認してください。
「Unsubscribe」リンクをクリックすると購読が解除されてしまうので注意してください。
:::

### 動作確認

AWS CLIでテストメッセージを送信します。

```bash
aws sns publish \
  --region us-east-1 \
  --topic-arn "arn:aws:sns:us-east-1:123456789012:hugo-s3-demo-alerts" \
  --subject "テスト通知" \
  --message "SNS動作確認テストです。このメールが届けば成功です。"
```

メールが届けばSNSの設定は完了です。

## CloudWatchダッシュボードの作成

CloudFrontの主要メトリクスを可視化するダッシュボードを作成します。

### cloudwatch.tf

`cloudwatch.tf` を新規作成します。

:::details cloudwatch.tf の全体（ダッシュボード部分）

```hcl
# ===========================================
# CloudWatch Dashboard
# CloudFrontの主要メトリクスを可視化
# ===========================================

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      # リクエスト数（時系列グラフ）
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "CloudFront リクエスト数"
          region = "us-east-1"
          metrics = [
            ["AWS/CloudFront", "Requests", "DistributionId", aws_cloudfront_distribution.main.id, "Region", "Global"]
          ]
          period = 300
          stat   = "Sum"
        }
      },
      # エラー率（時系列グラフ）
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "CloudFront エラー率 (%)"
          region = "us-east-1"
          metrics = [
            ["AWS/CloudFront", "4xxErrorRate", "DistributionId", aws_cloudfront_distribution.main.id, "Region", "Global"],
            [".", "5xxErrorRate", ".", ".", ".", "."]
          ]
          period = 300
          stat   = "Average"
        }
      },
      # バイト転送量（時系列グラフ）
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "CloudFront データ転送量 (Bytes)"
          region = "us-east-1"
          metrics = [
            ["AWS/CloudFront", "BytesDownloaded", "DistributionId", aws_cloudfront_distribution.main.id, "Region", "Global"],
            [".", "BytesUploaded", ".", ".", ".", "."]
          ]
          period = 300
          stat   = "Sum"
        }
      },
      # キャッシュヒット率（時系列グラフ）
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "CloudFront キャッシュヒット率 (%)"
          region = "us-east-1"
          metrics = [
            ["AWS/CloudFront", "CacheHitRate", "DistributionId", aws_cloudfront_distribution.main.id, "Region", "Global"]
          ]
          period = 300
          stat   = "Average"
        }
      }
    ]
  })
}

output "cloudwatch_dashboard_url" {
  description = "CloudWatch Dashboard URL"
  value       = "https://ap-northeast-1.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-1#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}
```

:::

### コード解説

#### ダッシュボードの構造

```hcl
dashboard_body = jsonencode({
  widgets = [
    {
      type   = "metric"
      x      = 0      # 左端からの位置
      y      = 0      # 上端からの位置
      width  = 12     # 幅（最大24）
      height = 6      # 高さ
      properties = {
        # ウィジェットの設定
      }
    }
  ]
})
```

ダッシュボードはJSON形式で定義します。`jsonencode()` 関数でHCLからJSONに変換します。

#### CloudFrontメトリクスのリージョン

```hcl
properties = {
  region = "us-east-1"
  # ...
}
```

CloudFrontはグローバルサービスですが、**メトリクスは `us-east-1` で取得する必要があります**。
これはCloudFrontの仕様です。

ダッシュボードは `properties.region` で他リージョンのメトリクスを参照できるため、ダッシュボード自体は `ap-northeast-1` に作成しても問題ありません。

#### 4つのウィジェット

| ウィジェット | メトリクス | 用途 |
|-------------|----------|------|
| リクエスト数 | `Requests` | アクセス量の把握 |
| エラー率 | `4xxErrorRate`, `5xxErrorRate` | エラー発生状況の監視 |
| データ転送量 | `BytesDownloaded`, `BytesUploaded` | 通信量の把握 |
| キャッシュヒット率 | `CacheHitRate` | CDNの効率確認 |

#### period と stat

| 属性 | 説明 | 設定値 |
|------|------|--------|
| `period` | メトリクスの集計間隔（秒） | 300（5分間隔） |
| `stat` | 集計方法 | Sum（合計）、Average（平均） |

### 実行と確認

```bash
terraform apply
```

出力されたURLでダッシュボードにアクセスし、4つのウィジェットが表示されることを確認します。

:::message
キャッシュヒット率は、アクセスが少ない場合「データがありません」と表示されることがあります。
これは正常です。アクセスが増えると表示されるようになります。
:::

## CloudWatchアラームの作成

エラー率が閾値を超えた場合にSNS経由でメール通知を送信するアラームを作成します。

### cloudwatch.tf に追記

:::details cloudwatch.tf に追記（アラーム部分）

```hcl
# ===========================================
# CloudWatch Alarms
# エラー率が閾値を超えたらSNS通知
# us-east-1に作成（CloudFrontメトリクスと同じリージョン）
# ===========================================

# 5xxエラー率アラーム（サーバーエラー）
resource "aws_cloudwatch_metric_alarm" "error_5xx" {
  provider            = aws.us_east_1
  alarm_name          = "${var.project_name}-5xx-error-rate"
  alarm_description   = "CloudFront 5xxエラー率が1%を超えた場合にアラート"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "5xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = 300
  statistic           = "Average"
  threshold           = 1
  treat_missing_data  = "notBreaching"

  dimensions = {
    DistributionId = aws_cloudfront_distribution.main.id
    Region         = "Global"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = {
    Name = "${var.project_name}-5xx-error-rate"
  }
}

# 4xxエラー率アラーム（クライアントエラー）
resource "aws_cloudwatch_metric_alarm" "error_4xx" {
  provider            = aws.us_east_1
  alarm_name          = "${var.project_name}-4xx-error-rate"
  alarm_description   = "CloudFront 4xxエラー率が5%を超えた場合にアラート"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "4xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = 300
  statistic           = "Average"
  threshold           = 5
  treat_missing_data  = "notBreaching"

  dimensions = {
    DistributionId = aws_cloudfront_distribution.main.id
    Region         = "Global"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = {
    Name = "${var.project_name}-4xx-error-rate"
  }
}
```

:::

### コード解説

#### アラームの主要設定

```hcl
resource "aws_cloudwatch_metric_alarm" "error_5xx" {
  provider            = aws.us_east_1               # us-east-1に作成
  comparison_operator = "GreaterThanThreshold"      # 閾値を超えたらアラート
  evaluation_periods  = 2                           # 2回連続で閾値超過したらアラート
  period              = 300                         # 5分間隔で評価
  threshold           = 1                           # 1%を閾値とする
  treat_missing_data  = "notBreaching"              # データなしは正常扱い
}
```

| 属性 | 説明 |
|------|------|
| `provider` | リソースを作成するリージョン（us-east-1必須） |
| `evaluation_periods` | 何回連続で閾値超過したらアラートにするか |
| `treat_missing_data` | データがない場合の扱い |

:::message alert
`provider = aws.us_east_1` を指定しないと、CloudWatch AlarmがCloudFrontメトリクスを取得できず、アラームが機能しません。
:::

:::message
`evaluation_periods = 2` とすることで、一時的なスパイクでアラートが発火するのを防ぎます。
:::

#### 閾値の設定根拠

| アラーム | 閾値 | 根拠 |
|----------|------|------|
| 5xxエラー率 | 1% | サーバーエラーは重大。低い閾値で早期検知 |
| 4xxエラー率 | 5% | 404等のクライアントエラーは一定量発生するため緩めに設定 |

#### 通知アクション

```hcl
alarm_actions = [aws_sns_topic.alerts.arn]  # アラート発火時
ok_actions    = [aws_sns_topic.alerts.arn]  # アラート解消時
```

`ok_actions` を設定することで、アラートが解消した際にも通知を受け取れます。

### 実行

```bash
terraform apply
```

## AWS Budgetsの設定

月額コストが閾値を超えた場合にメール通知を送信します。

### budgets.tf

`budgets.tf` を新規作成します。

```hcl
# ===========================================
# AWS Budgets
# 月額コストが閾値を超えたらメール通知
# ===========================================

resource "aws_budgets_budget" "monthly" {
  name         = "${var.project_name}-monthly-budget"
  budget_type  = "COST"
  limit_amount = "5"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  # 80%到達で通知
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.alert_email]
  }

  # 100%到達で通知
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.alert_email]
  }

  # 予測で100%超過しそうな場合に通知
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.alert_email]
  }
}
```

### コード解説

#### 予算設定

```hcl
limit_amount = "5"      # $5/月
limit_unit   = "USD"
time_unit    = "MONTHLY"
```

月額$5を予算として設定します。個人ブログであれば十分な金額です。

#### 3種類の通知

| 通知タイプ | 閾値 | 意味 |
|-----------|------|------|
| ACTUAL 80% | $4 | 予算の80%に到達したら警告 |
| ACTUAL 100% | $5 | 予算を超過したら通知 |
| FORECASTED 100% | $5（予測） | 月末に予算超過しそうなら早期警告 |

`FORECASTED` を設定することで、月初の段階で「このペースだと予算超過しそう」という警告を受け取れます。

### 実行

```bash
terraform apply
```

## 動作確認

### 作成したリソースの確認

```bash
terraform output
```

以下が出力されることを確認します。

```text
sns_topic_arn = "arn:aws:sns:us-east-1:123456789012:hugo-s3-demo-alerts"
cloudwatch_dashboard_url = "https://ap-northeast-1.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-1#dashboards:name=hugo-s3-demo-dashboard"
```

### AWSコンソールでの確認

1. **CloudWatchダッシュボード**
   - 4つのウィジェットが表示されている
   - メトリクスデータが表示されている（アクセスがあれば）

2. **CloudWatchアラーム**（us-east-1リージョンで確認）
   - 2つのアラームが「OK」状態になっている

3. **AWS Budgets**
   - 予算が作成されている
   - 現在のコストが表示されている

## トラブルシューティング

### SNS購読確認メールが届かない

**確認ポイント**:

1. 迷惑メールフォルダを確認
2. メールアドレスが正しいか確認（`terraform.tfvars`）
3. Terraformの実行が成功しているか確認

**対処法**: 購読を再作成する

```bash
terraform destroy -target=aws_sns_topic_subscription.email
terraform apply
```

### アラームが「INSUFFICIENT_DATA」のまま（アクセスなし）

**原因**: CloudFrontにアクセスがなく、メトリクスデータがない

**対処法**: サイトに何度かアクセスしてメトリクスを生成する。`treat_missing_data = "notBreaching"` を設定していれば、データがなくてもアラートは発火しません。

### アラームが「INSUFFICIENT_DATA」のまま（リージョン問題）

**原因**: SNSトピックやCloudWatch Alarmを `ap-northeast-1` に作成している

CloudFrontメトリクスは `us-east-1` にのみ存在するため、他リージョンのCloudWatch Alarmからは参照できません。

**確認方法**:

```bash
# アラームのリージョンを確認
aws cloudwatch describe-alarms \
  --alarm-names "hugo-s3-demo-5xx-error-rate" \
  --region us-east-1 \
  --query 'MetricAlarms[0].StateValue'
```

**対処法**:

1. `main.tf` に `us-east-1` provider を追加
2. SNSとAlarmに `provider = aws.us_east_1` を指定
3. `terraform apply` でリソースを再作成

### State lockエラー

**症状**:

```
Error: Error acquiring the state lock
Lock Info:
  ID:        xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**原因**: 前回の操作のロックが残っている

**対処法**:

```bash
terraform force-unlock {LOCK_ID}
```

:::message alert
`force-unlock` は、他の人が操作中でないことを確認してから実行してください。
:::

## まとめ

本記事では、以下を構築しました。

- **SNS**: アラート通知の送信先（us-east-1）
- **CloudWatchダッシュボード**: リクエスト数、エラー率、キャッシュヒット率の可視化
- **CloudWatchアラーム**: 5xxエラー率1%、4xxエラー率5%で通知（us-east-1）
- **AWS Budgets**: 月額$5の予算、80%/100%/予測100%で通知

### 作成したリソース

| リソース | リージョン | 用途 |
|----------|-----------|------|
| SNS Topic | us-east-1 | 通知の送信先 |
| SNS Subscription | us-east-1 | メール通知設定 |
| CloudWatch Dashboard | ap-northeast-1 | メトリクス可視化（4ウィジェット） |
| CloudWatch Alarm (5xx) | us-east-1 | 5xxエラー率監視 |
| CloudWatch Alarm (4xx) | us-east-1 | 4xxエラー率監視 |
| AWS Budgets | グローバル | コスト監視 |

### 監視のポイント

| 項目 | 設定値 | 理由 |
|------|--------|------|
| リージョン | us-east-1 | CloudFrontメトリクスはus-east-1固定 |
| 5xxエラー閾値 | 1% | サーバーエラーは重大なため低めに |
| 4xxエラー閾値 | 5% | 404等は一定量発生するため緩めに |
| evaluation_periods | 2 | 一時的なスパイクを除外 |
| treat_missing_data | notBreaching | データなしは正常扱い |

## 参考資料

- [Amazon SNS - AWS公式](https://docs.aws.amazon.com/ja_jp/sns/latest/dg/welcome.html)
- [Amazon CloudWatch - AWS公式](https://docs.aws.amazon.com/ja_jp/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html)
- [AWS Budgets - AWS公式](https://docs.aws.amazon.com/ja_jp/cost-management/latest/userguide/budgets-managing-costs.html)
- [Terraform aws_sns_topic](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic)
- [Terraform aws_cloudwatch_dashboard](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_dashboard)
- [Terraform aws_cloudwatch_metric_alarm](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_metric_alarm)
