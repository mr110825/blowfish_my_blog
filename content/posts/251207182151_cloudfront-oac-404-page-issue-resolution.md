+++
id = "251207182151"
date = '2025-12-07T18:21:51+09:00'
draft = false
title = 'CloudFront + OACで個別ページが404になる問題の解決'
tags = ["インフラ", "AWS", "トラブルシューティング", "実践"]
+++
## 今日学んだこと

GitHub PagesからAWS（S3 + CloudFront）へブログを移行した際、トップページは表示されるが個別記事ページで404エラーが発生しました。原因はOAC（Origin Access Control）使用時にS3の静的ウェブサイトホスティング機能が使えず、`/posts/article/` → `/posts/article/index.html` の自動補完が効かないことでした。CloudFront Functionでviewer-request時にURLリライトを実装して解決しました。

## 学習内容

### 問題の発生状況

GitHub Pagesで正常に動作していたHugoブログをAWSに移行したところ、以下の症状が発生しました。

| ページ | URL | 結果 |
|--------|-----|------|
| トップ | `https://example.com/` | ✅ 正常表示 |
| 記事一覧 | `https://example.com/posts/` | ❌ 404エラー |
| 個別記事 | `https://example.com/posts/article-name/` | ❌ 404エラー |

### 原因の特定

S3へのアクセス方式の違いが原因でした。

| 方式 | index.html自動補完 | セキュリティ |
|------|-------------------|-------------|
| 静的ウェブサイトホスティング | ✅ あり | ❌ パブリック公開が必要 |
| OAC経由（今回の構成） | ❌ なし | ✅ S3は非公開のまま |

OACを使用する場合、S3はREST APIエンドポイントとしてアクセスされます。この場合、`/posts/` というリクエストは「`posts/`というオブジェクト」を探しに行くため、`posts/index.html` は見つかりません。

### 解決策の比較

| 解決策 | 実行場所 | レイテンシ | コスト | 採用 |
|--------|----------|-----------|--------|------|
| CloudFront Function | エッジ | 極小 | 無料枠大 | ✅ |
| Lambda@Edge | リージョン | 小 | 従量課金 | - |
| S3静的ホスティング | - | - | - | ❌ OAC不可 |

CloudFront Functionを採用した理由は、単純なURLリライトには十分な機能があり、無料枠が大きく（月200万リクエスト）、エッジで実行されるためレイテンシへの影響が最小限だからです。

### 解決策：CloudFront FunctionによるURLリライト

viewer-requestイベントでURLを書き換え、末尾に `index.html` を付与します。

```javascript
function handler(event) {
  var request = event.request;
  var uri = request.uri;
  
  // 末尾が `/` の場合 → `/index.html` を付与
  if (uri.endsWith('/')) {
    request.uri += 'index.html';
  }
  // 拡張子がない場合 → `/index.html` を付与
  else if (!uri.includes('.')) {
    request.uri += '/index.html';
  }
  
  return request;
}
```

#### 処理フローの図解

```
リクエスト: /posts/article/
    ↓
CloudFront Function（viewer-request）
    ↓
URI書き換え: /posts/article/index.html
    ↓
S3からオブジェクト取得
    ↓
レスポンス: 200 OK
```

### Terraformでの実装

```hcl
resource "aws_cloudfront_function" "rewrite" {
  name    = "url-rewrite"
  runtime = "cloudfront-js-2.0"
  publish = true
  code    = <<-EOF
    function handler(event) {
      var request = event.request;
      var uri = request.uri;
      
      if (uri.endsWith('/')) {
        request.uri += 'index.html';
      }
      else if (!uri.includes('.')) {
        request.uri += '/index.html';
      }
      
      return request;
    }
  EOF
}
```

CloudFront Distributionの `default_cache_behavior` 内で、このFunctionを `viewer-request` イベントに関連付けます。

```hcl
resource "aws_cloudfront_distribution" "blog" {
  # ... 他の設定 ...

  default_cache_behavior {
    # ... 他の設定 ...

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.rewrite.arn
    }
  }
}
```

### デプロイと動作確認

#### 1. Terraformでデプロイ

```bash
terraform plan   # 変更内容を確認
terraform apply  # 適用
```

#### 2. CloudFrontキャッシュの無効化

設定変更後、キャッシュが残っていると古い挙動が続く場合があります。

```bash
aws cloudfront create-invalidation \
  --distribution-id <DISTRIBUTION_ID> \
  --paths "/*"
```

#### 3. 動作確認

```bash
# 末尾スラッシュありのURL
curl -I https://example.com/posts/

# 末尾スラッシュなしのURL
curl -I https://example.com/posts/article-name
```

いずれも `HTTP/2 200` が返れば成功です。

### CloudFront Function vs Lambda@Edge

| 項目 | CloudFront Function | Lambda@Edge |
|------|---------------------|-------------|
| 実行場所 | 全エッジロケーション | リージョンエッジキャッシュ |
| 最大実行時間 | 1ms | 5秒（viewer）/ 30秒（origin） |
| メモリ | 2MB | 128MB〜10GB |
| ネットワークアクセス | ❌ 不可 | ✅ 可能 |
| 対応イベント | viewer-request/response | 4種類すべて |
| 料金 | 月200万リクエスト無料 | リクエスト+実行時間課金 |

単純なURLリライトであればCloudFront Functionで十分です。外部APIへのアクセスや複雑な処理が必要な場合はLambda@Edgeを検討してください。

## まとめ

- OAC使用時はS3の「index.html自動補完」が効かない
- CloudFront Functionでviewer-request時にURLリライトを実装して解決
- 単純なURL書き換えにはCloudFront Functionが最適（低コスト・低レイテンシ）
- 設定変更後はキャッシュ無効化を忘れずに実行

## 参考

- [CloudFront Functions を使用して URL の末尾から index.html ファイルを表示する｜AWS re:Post](https://repost.aws/ja/knowledge-center/cloudfront-index-html)
- [CloudFront Functions の作成 - Amazon CloudFront](https://docs.aws.amazon.com/ja_jp/AmazonCloudFront/latest/DeveloperGuide/create-function.html)
