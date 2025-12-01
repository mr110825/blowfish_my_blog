+++
id = "251202082701"
date = '2025-12-02T08:27:01+09:00'
draft = false
title = 'Terraform for式入門：リストとマップの変換テクニック'
tags = ["インフラ", "Terraform", "入門", "まとめ"]
+++
## 今日学んだこと

Terraform の for 式と for 文字列ディレクティブについて学びました。これらは count や for_each とは異なり、リソースを作成するのではなく、リストやマップを変換・加工するための機能です。

## 学習内容

### for 式の基本

for 式は count や for_each とは異なり、リストやマップを**変換・加工**するための式です。

#### リストを出力する構文

```hcl
[for <ITEM> in <LIST> : <OUTPUT>]
```

例として、名前のリストを大文字に変換してみます。

```hcl
variable "names" {
  type    = list(string)
  default = ["user1", "user2", "user3"]
}

output "upper_names" {
  value = [for name in var.names : upper(name)]
}
```

出力結果は `["USER1", "USER2", "USER3"]` となります。

#### マップに対するループ

マップをループする場合は、キーと値の両方を取得できます。

```hcl
[for <KEY>, <VALUE> in <MAP> : <OUTPUT>]
```

```hcl
variable "user_roles" {
  type = map(string)
  default = {
    user1 = "admin"
    user2 = "developer"
    user3 = "viewer"
  }
}

output "user_descriptions" {
  value = [for name, role in var.user_roles : "${name} is the ${role}"]
}
```

出力結果は `["user1 is the admin", "user2 is the developer", "user3 is the viewer"]` のようなリストになります。

> **注意**: マップの要素順序は保証されないため、出力順序は異なる場合があります。

### マップを出力する構文

`[]` と `{}` で出力形式が変わります。

| 括弧 | 出力形式 | 構文 |
|------|----------|------|
| `[]` | リスト | `[for ... : <OUTPUT>]` |
| `{}` | マップ | `{for ... : <KEY> => <VALUE>}` |

```hcl
output "upper_roles" {
  value = {for name, role in var.user_roles : upper(name) => upper(role)}
}
```

出力結果は以下のようなマップになります。

```hcl
{
  "USER1" = "ADMIN"
  "USER2" = "DEVELOPER"
  "USER3" = "VIEWER"
}
```

### for 式の出力パターンまとめ

| 入力 | 出力 | 構文例 |
|------|------|--------|
| リスト → リスト | `[]` | `[for x in list : upper(x)]` |
| マップ → リスト | `[]` | `[for k, v in map : "${k}=${v}"]` |
| リスト → マップ | `{}` | `{for x in list : x => upper(x)}` |
| マップ → マップ | `{}` | `{for k, v in map : upper(k) => upper(v)}` |

### for 文字列ディレクティブによるループ

文字列ディレクティブを使用すると、文字列内でループを展開できます。`%{...}` を使用します。

#### 基本構文

```hcl
%{for <ITEM> in <COLLECTION>} <BODY> %{endfor}
```

#### 例：名前のリストをカンマ区切りで出力

```hcl
output "for_directive" {
  value = "%{ for name in var.names }${name}, %{ endfor }"
}
```

出力結果は `"user1, user2, user3, "` となります。

#### インデックス付きの構文

```hcl
%{for <INDEX>, <ITEM> in <COLLECTION>} <BODY> %{endfor}
```

```hcl
output "for_directive_with_index" {
  value = "%{ for index, name in var.names }${index}: ${name}, %{ endfor }"
}
```

出力結果は `"0: user1, 1: user2, 2: user3, "` となります。

### ヒアドキュメント構文

文字列ディレクティブでは、複数行の文字列を扱うためにヒアドキュメント構文を使用することが多いです。

```hcl
<<EOF
複数行の
文字列を
ここに記述
EOF
```

`<<-EOF` を使うとインデントを自動除去できます。

### strip marker（`~`）による空白除去

文字列ディレクティブを使うと不要なスペースや改行が追加されることがあります。strip marker（`~`）で解決できます。

```hcl
output "for_directive_strip" {
  value = <<EOF
%{~ for i, name in var.names ~}
${name}%{ if i < length(var.names) - 1 }, %{ endif }
%{~ endfor ~}
EOF
}
```

出力結果は `user1, user2, user3` ときれいに整形されます。

| 記法 | 効果 |
|------|------|
| `%{~ ... }` | 左側の空白・改行を除去 |
| `%{ ... ~}` | 右側の空白・改行を除去 |
| `%{~ ... ~}` | 両側の空白・改行を除去 |

### for 式と文字列ディレクティブの比較

| 手法 | 構文 | 結果 |
|------|------|------|
| for 式 | `[for i, name in var.names : "${i}: ${name}"]` | リスト |
| 文字列ディレクティブ | `"%{for i, name in var.names}${i}: ${name}%{endfor}"` | 文字列 |

## まとめ

| 手法 | 用途 | 結果 |
|------|------|------|
| for 式 | リスト/マップの変換・加工 | 新しいリスト or マップ |
| for 文字列ディレクティブ | 文字列内でのループ展開 | 文字列 |

- for 式は `[]` でリスト、`{}` でマップを出力する
- 文字列ディレクティブは `%{for ...}...%{endfor}` で文字列内にループを展開する
- strip marker（`~`）を使うと不要な空白・改行を除去できる

## 参考

- [詳解 Terraform 第3版](https://www.oreilly.co.jp/books/9784814400522/) - Yevgeniy Brikman著、松浦隼人訳、オライリージャパン、2023年
- [for Expressions](https://developer.hashicorp.com/terraform/language/expressions/for)
- [String Templates](https://developer.hashicorp.com/terraform/language/expressions/strings#string-templates)
- [Built-in Functions](https://developer.hashicorp.com/terraform/language/functions)