+++
id = "251202082522"
date = '2025-12-02T08:25:22+09:00'
draft = false
title = 'Terraformループの基礎：countとfor_eachの使い分け'
tags = ["インフラ", "Terraform", "入門", "まとめ"]
+++
## 今日学んだこと

Terraform で同じようなリソースを複数作成する際に使う `count` と `for_each` について学びました。両者の違いと、途中の要素を削除する際に発生する問題、そして `for_each` がその問題をどう解決するかを理解しました。

## 学習内容

### count と for_each の違い

| 項目 | count | for_each |
|------|-------|----------|
| 識別方法 | インデックス（番号） | キー（名前） |
| 対応データ型 | 数値のみ | 集合（set）・マップ（map） |
| 途中要素の削除 | インデックスずれ問題あり | 他の要素に影響なし |
| インラインブロック | 使用不可 | 使用可能（dynamic ブロック） |

### count パラメータによるループ

count は Terraform の初期から存在する基本的な機能です。`count.index` を使ってリソースに一意の名前を付けます。

```hcl
resource "aws_iam_user" "example" {
  count = 3
  name  = "user.${count.index}"
}
```

作成されるユーザー名は `user.0`, `user.1`, `user.2` となります。`count.index` は 0 から始まる点に注意が必要です。

より実践的なパターンとして、リストと `length()` 関数を組み合わせる方法があります。

```hcl
variable "user_names" {
  type    = list(string)
  default = ["user1", "user2", "user3"]
}

resource "aws_iam_user" "example" {
  count = length(var.user_names)
  name  = var.user_names[count.index]
}
```

この方法のメリットは、変数を変更するだけでユーザー数を増減でき、main.tf を編集する必要がない点です。

#### count 使用時のリソース参照

count を使うとリソースは配列として扱われるため、インデックスを指定して参照します。

```hcl
# 特定のユーザーを参照
aws_iam_user.example[0].arn  # → user1 の ARN

# 全ユーザーの ARN を出力（スプラット式）
output "user_arns" {
  value = aws_iam_user.example[*].arn
}
```

### count の制限事項

count には大きな制限事項が2つあります。

**制限1：インラインブロックには利用不可**

ingress や egress などのインラインブロック内で count は使えません。インラインブロックを動的に生成したい場合は dynamic ブロックを使用します。

**制限2：途中の要素削除で問題が発生**

これが count の最大の問題点です。`["user1", "user2", "user3"]` から `user2` を削除しようとすると、以下のような意図しない動作が発生します。

| インデックス | 期待 | 実際の動作 |
|-------------|------|-----------|
| [0] | user1（維持） | user1（維持） |
| [1] | user3（維持） | user2 → user3 に変更 |
| [2] | - | user3 を削除 |

count はインデックスでリソースを識別するため、途中の要素を抜くとインデックスがずれてしまいます。結果として、user2 ではなく user3 が削除されてしまいます。

### for_each 式によるループ

for_each はキー（名前）でリソースを識別するため、途中の要素を削除しても他のリソースに影響しません。

```hcl
resource "aws_iam_user" "example" {
  for_each = toset(var.user_names)
  name     = each.value
}
```

リストを使う場合は `toset()` で集合に変換する必要があります。

> **注意**: `toset()` は重複する値を自動的に除去します。リストに重複値がある場合、意図しない結果になる可能性があるため、入力データの一意性を確認してください。

#### each.key と each.value の動作

| データ型 | each.key | each.value |
|----------|----------|------------|
| 集合（set） | 値そのもの | 値そのもの（key と同じ） |
| マップ（map） | キー | 値 |

#### for_each による途中要素の削除

`["user1", "user2", "user3"]` から `user2` を削除した場合の動作を比較します。

**for_each の場合（正しく動作）**：

| キー | 変更前 | 変更後 | 動作 |
|------|--------|--------|------|
| "user1" | user1 | user1 | 維持 |
| "user2" | user2 | - | 削除（意図通り） |
| "user3" | user3 | user3 | 維持 |

for_each はキーで識別するため、user2 のみが正しく削除されます。

#### for_each で作成したリソースの参照

for_each で作成するとリソースはマップ形式になります。ARN を取り出すには `values()` 関数を使います。

```hcl
output "all_arns" {
  value = values(aws_iam_user.example)[*].arn
}
```

### dynamic ブロックによるインラインブロックの動的生成

for_each を使用するとリソース内のインラインブロックを複数作成できます。

```hcl
dynamic "tag" {
  for_each = var.custom_tags

  content {
    key                 = tag.key
    value               = tag.value
    propagate_at_launch = true
  }
}
```

## まとめ

| 状況 | 推奨 |
|------|------|
| 単純な数による繰り返し | count |
| 途中の要素を削除する可能性がある | for_each |
| インラインブロックを動的生成 | for_each（dynamic ブロック） |
| キー/名前でリソースを管理したい | for_each |

- count はインデックスで管理、for_each はキーで管理
- 途中の要素削除が想定される場合は for_each を使う
- インラインブロックの動的生成には dynamic ブロックと for_each を組み合わせる

## 参考

- [詳解 Terraform 第3版](https://www.oreilly.co.jp/books/9784814400522/) - Yevgeniy Brikman著、松浦隼人訳、オライリージャパン、2023年
- [The count Meta-Argument](https://developer.hashicorp.com/terraform/language/meta-arguments/count)
- [The for_each Meta-Argument](https://developer.hashicorp.com/terraform/language/meta-arguments/for_each)
- [Dynamic Blocks](https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks)