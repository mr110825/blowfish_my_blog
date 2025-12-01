+++
id = "251202082958"
date = '2025-12-02T08:29:58+09:00'
draft = false
title = 'Terraformゼロダウンタイムデプロイの実現方法'
tags = ["インフラ", "Terraform", "実践", "DevOps"]
+++
## 今日学んだこと

Terraform で ASG（Auto Scaling Group）を使ったゼロダウンタイムデプロイを実現する方法を学びました。`create_before_destroy` ライフサイクルと `min_elb_capacity` を組み合わせることで、サービスを停止せずにインフラを更新できます。

## 学習内容

### 背景と問題

webserver-cluster モジュールで `user-data.sh` の内容（`server_text` など）を変更した場合、以下のような動作になります。

- 新しい Launch Configuration が作成される
- ASG が新しい Launch Configuration を参照するようになる
- **しかし、既存の EC2 インスタンスはそのまま！**

Launch Configuration は**新しいインスタンスを起動する際のテンプレート**であり、既存のインスタンスには影響しません。

### 解決策の比較

| 方法 | 手順 | 問題点 |
|------|------|--------|
| ASG を削除して再作成 | 古い ASG 削除 → 新しい ASG 作成 | ダウンタイムが発生 |
| create_before_destroy | 新しい ASG 作成 → 古い ASG 削除 | ダウンタイムなし ✅ |

### ゼロダウンタイムデプロイに必要な3つの設定

| # | 設定 | 目的 |
|---|------|------|
| 1 | `name` を起動設定の名前に依存させる | 起動設定が変わると ASG 名も変わり、置き換えが発生 |
| 2 | `create_before_destroy = true` | 新しい ASG を先に作成してから古いものを削除 |
| 3 | `min_elb_capacity = min_size` | 新しいインスタンスが ELB のヘルスチェックに合格するまで待機 |

### コード例：ゼロダウンタイムデプロイ対応の ASG

```hcl
resource "aws_autoscaling_group" "example" {
  # 1. ASG名が起動設定の名前を参照（起動設定が変わるとASGも置き換え）
  name = "${var.cluster_name}-${aws_launch_configuration.example.name}"

  launch_configuration = aws_launch_configuration.example.name
  vpc_zone_identifier  = data.aws_subnets.default.ids
  target_group_arns    = [aws_lb_target_group.asg.arn]
  health_check_type    = "ELB"

  min_size = var.min_size
  max_size = var.max_size

  # 3. ヘルスチェックに合格するまで待機
  min_elb_capacity = var.min_size

  # 2. 新しいASGを先に作成してから古いASGを削除
  lifecycle {
    create_before_destroy = true
  }

  tag {
    key                 = "Name"
    value               = var.cluster_name
    propagate_at_launch = true
  }

  dynamic "tag" {
    for_each = {
      for key, value in var.custom_tags:
      key => upper(value)
      if key != "Name"
    }

    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }
}
```

### デプロイの流れ

```
server_text 変更
    ↓
user-data.sh の内容が変更
    ↓
新しい Launch Configuration 作成（名前が変わる）
    ↓
ASG の name が変わる → ASG の置き換えが必要と判断
    ↓
新しい ASG を作成（create_before_destroy）
    ↓
min_elb_capacity 台がヘルスチェック合格を待つ
    ↓
古い ASG を削除
    ↓
ゼロダウンタイムで完了！
```

### 動作確認方法

```bash
while true; do curl http://<load_balancer_url>; sleep 1; done
```

1秒ごとにリクエストを送り、デプロイ中もレスポンスが途切れないことを確認します。

| 状態 | レスポンス |
|------|-----------|
| デプロイ前 | 古いメッセージのみ |
| デプロイ中 | 古い/新しいが混在（両方の ASG が稼働） |
| デプロイ後 | 新しいメッセージのみ |

デプロイ中もレスポンスが途切れなければ、ゼロダウンタイム達成です。

### ゼロダウンタイムデプロイの制限事項

#### 制限1：Auto Scaling ポリシーとは組み合わせて使えない

デプロイのたびに ASG のサイズが `min_size` にリセットされてしまいます。

```
通常運用中：Auto Scaling により 10 台で稼働
    ↓
デプロイ実行（create_before_destroy）
    ↓
新しい ASG 作成時に min_size（例：2台）でスタート
    ↓
トラフィックに対してインスタンス数が不足！
```

回避策としては、`recurrence` パラメータの調整や `desired_capacity` パラメータの明示的な設定があります。

#### 制限2：ネイティブなデプロイ方法がない（なかった）

以前の Terraform にはゼロダウンタイムデプロイのようなネイティブなデプロイ方法がありませんでした。最近の Terraform ではネイティブなデプロイ方法がサポートされてきているため、適宜公式ドキュメントの確認が必要です。

## まとめ

- ゼロダウンタイムデプロイには3つの設定が必要：ASG名の依存、`create_before_destroy`、`min_elb_capacity`
- `create_before_destroy` で新しい ASG を先に作成してから古い ASG を削除する
- `min_elb_capacity` でヘルスチェック合格まで待機することで、サービス断を防ぐ
- Auto Scaling ポリシーとの併用には注意が必要

## 参考

- [詳解 Terraform 第3版](https://www.oreilly.co.jp/books/9784814400522/) - Yevgeniy Brikman著、松浦隼人訳、オライリージャパン、2023年
- [The lifecycle Meta-Argument](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle)
- [AWS Provider: aws_autoscaling_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/autoscaling_group)