+++
id = "251203194354"
date = '2025-12-03T19:43:54+09:00'
draft = false
title = 'ACM証明書とは？SSL/TLS証明書の基礎からCloudFront連携まで'
tags = ["インフラ", "AWS", "ACM", "入門"]
+++
## 今日学んだこと

ACM（AWS Certificate Manager）はSSL/TLS証明書を無料で発行・自動更新できるAWSサービス。
CloudFrontと組み合わせることで、カスタムドメインでのHTTPS通信を実現できます。

## 学習内容

### ACMとは

**ACM = AWS Certificate Manager**

SSL/TLS証明書を管理するAWSサービスです。

### SSL/TLS証明書の役割

SSL/TLS証明書には2つの役割があります：

| 役割 | 説明 |
|------|------|
| 通信の暗号化 | HTTPS通信を実現（HTTP = 暗号化なし、HTTPS = 暗号化あり） |
| サイトの証明 | 「このサイトは本物です」を保証 |

### ACMのメリット

従来の方法と比較すると、ACMのメリットが明確です
- 無料
- AWS側で自動設定
- 有効期限切れに対して自動更新

### CloudFrontでの構成

```
ユーザー
  ↓ HTTPS（暗号化通信）
CloudFront ← ACM証明書で「example.com」を証明
  ↓
S3（コンテンツ）
```

ACM証明書がないと `https://example.com` でアクセスできず、ブラウザに警告が出ます。

### 重要な制約

CloudFrontでACM証明書を使用する場合、証明書は**必ずus-east-1（バージニア北部）で作成する必要があります**。

> CloudFrontでの利用：Amazon CloudFrontでACM証明書を使用する場合、証明書は必ずUS East (N. Virginia) リージョンでリクエストまたはインポートする必要があります。
> — [AWS Certificate Manager Overview](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html)

## まとめ

- ACMはSSL/TLS証明書を無料で発行・自動更新できるサービス
- 従来の証明書管理と比べて、コスト・手間が大幅に削減される
- CloudFrontと組み合わせてHTTPS通信を実現
- CloudFrontで使用する場合はus-east-1で発行が必要

## 参考

- [AWS Certificate Manager Overview](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html)
- [Supported Regions - AWS Certificate Manager](https://docs.aws.amazon.com/acm/latest/userguide/acm-regions.html)
