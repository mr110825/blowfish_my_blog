+++
id = "251203194906"
date = '2025-12-03T19:49:06+09:00'
draft = false
title = 'CloudFront + ACM証明書でハマるus-east-1制約'
tags = ["インフラ", "AWS", "CloudFront", "実践"]
+++
## 今日学んだこと

CloudFrontでACM証明書を使う場合、証明書は**必ずus-east-1（バージニア北部）で作成する必要がある**ことを学びました。東京リージョンで作成すると、CloudFrontの設定画面で選択肢に表示されません。

## 学習内容

### なぜus-east-1なのか

CloudFrontは**グローバルサービス**です。グローバルサービスはus-east-1のACM証明書しか参照できない仕様になっています。
公式ドキュメントにも明記されています

> 「Amazon CloudFrontでACM証明書を使用するには、米国東部（バージニア北部）リージョンで証明書をリクエストまたはインポートする必要があります。」
> — [Supported Regions - AWS Certificate Manager](https://docs.aws.amazon.com/acm/latest/userguide/acm-regions.html)

### 「なぜus-east-1なのか」の背景

#### 1. CloudFrontのコントロールプレーンがus-east-1にある

CloudFrontはグローバルサービスですが、**APIエンドポイントはus-east-1に存在**します。

| エンドポイント | リージョン |
|---------------|-----------|
| `cloudfront.amazonaws.com` | 米国東部（バージニア北部） |
| `cloudfront-fips.amazonaws.com` | 米国東部（バージニア北部） |
| `cloudfront.global.api.aws` | 米国東部（バージニア北部） |

> — [Amazon CloudFront endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/cf_region.html)

#### 2. グローバルサービスのAPIリクエストはus-east-1にルーティングされる

AWSの公式ドキュメントでは、グローバルエンドポイントについて以下のように説明されています：

> 「汎用エンドポイントを使用すると、AWSはAPIリクエストを米国東部（バージニア北部）（`us-east-1`）にルーティングします。これはAPI呼び出しのデフォルトリージョンです。」
> — [AWS service endpoints](https://docs.aws.amazon.com/general/latest/gr/rande.html)

CloudFront、IAM、Route 53などの**グローバルサービスはus-east-1を管理基盤**としています。

#### 3. ACM証明書はリージョナルリソース

ACM証明書は**作成したリージョン内でのみ参照可能**です：

```
us-east-1で作成した証明書 → us-east-1のリソースからのみ参照可能
ap-northeast-1で作成した証明書 → ap-northeast-1のリソースからのみ参照可能
```

CloudFrontのコントロールプレーン（API）がus-east-1にあるため、**同じus-east-1にあるACM証明書しか「見えない」** のです。

#### 4. 証明書配布の仕組み

```
1. us-east-1でACM証明書を作成
2. CloudFrontディストリビューションに証明書を関連付け
3. CloudFrontが証明書を全エッジロケーションに内部配布
4. 世界中のユーザーがHTTPSでアクセス可能に
```

CloudFrontは世界中に **400以上のエッジロケーション（PoP）** を持ち、us-east-1で設定された証明書を各エッジに配布します。

> — [Amazon CloudFront features](https://aws.amazon.com/cloudfront/features/)

### サービス別のACM証明書リージョン

| サービス | ACM証明書のリージョン | 理由 |
|----------|----------------------|------|
| CloudFront | **us-east-1のみ** | グローバルサービスのため |
| ALB | ALBと同じリージョン | リージョナルサービスのため |
| API Gateway（Edge最適化） | **us-east-1のみ** | CloudFront経由のため |
| API Gateway（リージョナル） | API Gatewayと同じリージョン | リージョナルサービスのため |

## まとめ

- CloudFrontでACM証明書を使う場合は**us-east-1で作成必須**
- ALBは同じリージョンのACM証明書を使用
- API Gateway（Edge最適化）もus-east-1が必要

## 参考

- [Supported Regions - AWS Certificate Manager](https://docs.aws.amazon.com/acm/latest/userguide/acm-regions.html)
- [AWS Certificate Manager Overview](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html)
- [Amazon CloudFront endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/cf_region.html)
- [AWS service endpoints](https://docs.aws.amazon.com/general/latest/gr/rande.html)
- [Amazon CloudFront features](https://aws.amazon.com/cloudfront/features/)
