+++
id = "251207175353"
date = '2025-12-07T17:53:53+09:00'
draft = false
title = 'AWS Budgetsアラートを受信したときの対応フロー'
tags = ["インフラ", "AWS", "実践", "トラブルシューティング"]
+++
## 今日学んだこと

AWS Budgetsでアラートを受信した際の対応フローを整理しました。実際にFORECASTEDアラートを受信して対応した経験から、今後も使えるベストプラクティスとしてまとめました。

## 学習内容

### この記事を書いた経緯

AWS Budgetsから予算超過のアラートメールを受信しました。調査の結果、過去のハンズオン環境のコストと一括費用（ドメイン購入）が原因と判明し、対応不要と判断できました。この対応フローは今後も役立つと考え、ベストプラクティスとして整理しました。

### AWS Budgetsとは

AWS Budgetsは、AWSの利用コストを監視し、設定した予算を超えそうな場合にアラートを通知するサービスです。月額の予算を設定しておくと、実績や予測がしきい値を超えた際にメールで通知を受け取れます。

### AWS Budgetsのアラート種別

AWS Budgetsには2種類のアラートがあります。

| 種別 | 意味 |
|------|------|
| ACTUAL | 実際にその金額を使った |
| FORECASTED | 月末にその金額になりそう（予測） |

**出典**: [AWS公式ドキュメント - Best practices for AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-best-practices.html)

### FORECASTED予測の限界

FORECASTEDは「現在のペースが月末まで続く」と仮定した線形予測です。この予測方法には限界があります。

| 状況 | 予測の問題点 |
|------|-------------|
| リソースを月の途中で削除した | 削除後もコストが継続する前提で計算される |
| ドメイン購入など一括費用が発生した | 毎日同額が発生する前提で計算される |
| ハンズオン環境を短期間だけ使用した | 月末まで使い続ける前提で計算される |

このため、FORECASTEDアラートは「参考程度」に捉え、ACTUALアラートを重視することをおすすめします。

### アラート対応フロー

#### Step 1: アラート種別の確認

受信したメールでACTUAL/FORECASTEDを確認。

#### Step 2: Cost Explorerで原因特定

1. Cost Explorerにアクセス
2. 期間を「今月（Month-to-date）」に設定
3. Group byで「Service」を選択
4. 異常に高いサービスを特定

#### Step 3: 原因の分類と対応

| 原因 | 対応 |
|------|------|
| 一時的な費用（ドメイン購入等） | 対応不要、予測は無視 |
| 削除済みリソースの残存コスト | 対応不要、来月から減る |
| 起動中のリソース | 不要なら即削除 |
| 想定内の増加 | 予算設定を見直し |

#### Step 4: リソース確認（必要な場合のみ）

原因が「起動中のリソース」の場合、以下のサービスを優先的に確認します。

| 優先度 | サービス | 確認場所 |
|--------|----------|---------|
| 高 | NAT Gateway | VPCコンソール |
| 高 | EC2（全リージョン） | AWS Global View |
| 高 | RDS | RDSコンソール |
| 高 | ALB/ELB | EC2 → ロードバランサー |
| 中 | Elastic IP（未使用） | EC2 → Elastic IP |

これらのサービスは起動しているだけで課金が発生するため、不要であれば削除します。

### AWS Global Viewを使った全リージョン確認

EC2インスタンスは通常、リージョンごとにしか確認できません。しかし、**AWS Global View**を使えば、全リージョンのリソースを一画面で確認できます。今回の対応で実際に使用し、非常に便利だと感じました。

#### AWS Global Viewとは

AWS Global Viewは、複数のAWSリージョンにまたがるEC2およびVPC関連リソースを単一のコンソールで表示できる機能です。

#### 確認できるリソース

- EC2インスタンス
- VPC
- サブネット
- セキュリティグループ
- EBSボリューム
- NAT Gateway
- Elastic IP

#### アクセス方法

1. AWSコンソールで「AWS Global View」を検索
2. または直接アクセス: https://console.aws.amazon.com/ec2globalview/home

#### 使い方

1. 「リージョンエクスプローラー」タブを開く
2. 「リソースの概要」で全リージョンのインスタンス数を確認
3. インスタンス数のリンクをクリックすると、全リージョンのインスタンス一覧が表示される
4. 不要なインスタンスがあれば、リソースIDをクリックして該当リージョンのコンソールに移動し、削除

リージョンを切り替えながら確認する手間が省けるため、コスト調査の際に非常に便利です。

### 運用上のポイント

| ポイント | 内容 |
|----------|------|
| ハンズオン後の確認 | リソース削除を忘れないこと |
| 古い設定の整理 | 不要なBudgetは削除する |
| アラートの使い分け | ACTUALを重視、FORECASTEDは参考程度 |

## まとめ

- AWS Budgetsのアラートは ACTUAL（実績）と FORECASTED（予測）の2種類がある
- FORECASTED は線形予測のため、リソース削除や一括費用を考慮しない
- アラート受信時は Cost Explorer でサービス別に原因を特定する
- AWS Global View を使えば全リージョンのリソースを一画面で確認できる
- ハンズオン環境は使用後に必ずリソースを削除する

## 参考

- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [Best practices for AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-best-practices.html)
- [Budgets API Reference - Notification](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_budgets_Notification.html)
- [AWS Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html)
- [AWS Global View](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/global-view.html)
