+++
id = "251202082829"
date = '2025-12-02T08:28:29+09:00'
draft = false
title = 'Terraform条件分岐パターン集'
tags = ["インフラ", "Terraform", "実践", "メモ"]
+++
## 今日学んだこと

Terraform で条件分岐を実現する3つの手法（count + 三項演算子、for_each + for の if、if 文字列ディレクティブ）について学びました。特に count を使った「作る/作らない」の制御パターンは実践で頻繁に使われます。

## 学習内容

### 条件分岐に使う手法

| 手法 | 用途 |
|------|------|
| count パラメータ | 条件付きリソースの作成（作る/作らない） |
| for_each 式 / for 式 | 条件付きリソース、インラインブロックの条件生成 |
| if 文字列ディレクティブ | 文字列内での条件分岐 |

### count パラメータを使った条件分岐

#### count を使った if 文

三項演算子と組み合わせて、リソースを「作成する/しない」を制御します。

```hcl
count = var.enable_autoscaling ? 1 : 0
```

| var.enable_autoscaling | count | 結果 |
|------------------------|-------|------|
| true | 1 | リソースを作成する |
| false | 0 | リソースを作成しない |

#### コード例：オートスケーリングスケジュール

```hcl
resource "aws_autoscaling_schedule" "scale_out_during_business_hours" {
  count = var.enable_autoscaling ? 1 : 0

  scheduled_action_name  = "${var.cluster_name}-scale-out-during-business-hours"
  min_size               = 2
  max_size               = 10
  desired_capacity       = 10
  recurrence             = "0 9 * * *"
  autoscaling_group_name = aws_autoscaling_group.example.name
}
```

本番環境では `enable_autoscaling = true`、ステージング環境では `enable_autoscaling = false` のように環境ごとに設定を切り替えられます。

#### count を使った if-else 文

count の値を反転させることで if-else を実現します。

```hcl
# if 文（true のとき作成）
resource "aws_iam_user_policy_attachment" "user1_cloudwatch_full_access" {
  count = var.give_user1_cloudwatch_full_access ? 1 : 0
  # ...
}

# else 文（false のとき作成）→ 三項演算子の値を反転
resource "aws_iam_user_policy_attachment" "user1_cloudwatch_read_only" {
  count = var.give_user1_cloudwatch_full_access ? 0 : 1
  # ...
}
```

| var.give_user1_cloudwatch_full_access | full_access の count | read_only の count |
|---------------------------------------|---------------------|-------------------|
| true | 1 | 0 |
| false | 0 | 1 |

#### 条件付きリソースの出力値を取得

count で作成したリソースは、条件によって存在したりしなかったりします。`concat` と `one` 関数を組み合わせて出力値を取得します。

```hcl
output "user1_cloudwatch_policy_arn" {
  value = one(concat(
    aws_iam_user_policy_attachment.user1_cloudwatch_full_access[*].policy_arn,
    aws_iam_user_policy_attachment.user1_cloudwatch_read_only[*].policy_arn
  ))
}
```

`one()` 関数は単一要素のリストから値を取り出します。空のリストの場合は `null` を返します。

### for_each と for を使った条件分岐

#### 基本的な考え方

| for_each に渡す集合 | 結果 |
|-------------------|------|
| 空の集合 `{}` / `[]` | リソースは作成されない |
| 空ではない集合 | リソースが作成される |

for 式の `if` でフィルタリングすることで、条件に合う要素のみを処理できます。

```hcl
dynamic "tag" {
  for_each = {
    for key, value in var.custom_tags:
    key => upper(value)
    if key != "Name"    # ← 条件分岐（フィルタリング）
  }

  content {
    key                 = tag.key
    value               = tag.value
    propagate_at_launch = true
  }
}
```

この例では `key != "Name"` の条件により、"Name" キーを除外しています。

### count vs for_each の使い分け（条件分岐）

| ユースケース | 推奨 | 理由 |
|-------------|------|------|
| 条件付きでリソース/モジュールを作成（作る or 作らない） | count | `? 1 : 0` がシンプル |
| リソース/モジュールを複数作成 | for_each | 途中要素削除の問題がない |
| それ以外のループや条件分岐 | for_each | 柔軟性が高い |

### if 文字列ディレクティブを使った条件分岐

文字列内で条件分岐を行うための構文です。

#### 基本構文

```hcl
%{ if <CONDITION> }<TRUE_VAL>%{ endif }
```

#### コード例：最後の要素だけカンマを付けない

```hcl
output "for_directive_index_if" {
  value = <<EOF
%{~ for i, name in var.names ~}
${name}%{ if i < length(var.names) - 1 }, %{ endif }
%{~ endfor ~}
EOF
}
```

| ループ | i | name | i < length - 1 | 出力 |
|--------|---|------|----------------|------|
| 1回目 | 0 | user1 | true | `user1, ` |
| 2回目 | 1 | user2 | true | `user2, ` |
| 3回目 | 2 | user3 | false | `user3` |

#### if-else 構文

```hcl
%{ if <CONDITION> }<TRUE_VAL>%{ else }<FALSE_VAL>%{ endif }
```

```hcl
output "for_directive_index_if_else_strip" {
  value = <<EOF
%{~ for i, name in var.names ~}
${name}%{ if i < length(var.names) - 1 }, %{ else }.%{ endif }
%{~ endfor ~}
EOF
}
```

出力結果は `user1, user2, user3.` となり、最後の要素にピリオドが付きます。

## まとめ

| 手法 | 用途 | 構文例 |
|------|------|--------|
| count + 三項演算子 | リソースを作る/作らない | `count = var.enable ? 1 : 0` |
| count（if-else） | 排他的なリソース作成 | `? 1 : 0` と `? 0 : 1` を反転 |
| for_each + for の if | 条件付きフィルタリング | `for k, v in map : k => v if condition` |
| if 文字列ディレクティブ | 文字列内の条件分岐 | `%{ if condition }...%{ endif }` |

- 「作る or 作らない」の2択なら count がシンプル
- 複数作成や複雑な条件なら for_each を使う
- `one()` と `concat()` で条件付きリソースの出力値を安全に取得できる

## 参考

- [詳解 Terraform 第3版](https://www.oreilly.co.jp/books/9784814400522/) - Yevgeniy Brikman著、松浦隼人訳、オライリージャパン、2023年
- [The count Meta-Argument](https://developer.hashicorp.com/terraform/language/meta-arguments/count)
- [The for_each Meta-Argument](https://developer.hashicorp.com/terraform/language/meta-arguments/for_each)
- [String Templates](https://developer.hashicorp.com/terraform/language/expressions/strings#string-templates)
- [Built-in Functions - one](https://developer.hashicorp.com/terraform/language/functions/one)