+++
id = "251202083121"
date = '2025-12-02T08:31:21+09:00'
draft = false
title = 'Terraform のつまずきポイントと回避策'
tags = ["インフラ", "Terraform", "実践", "トラブルシューティング"]
+++
## 今日学んだこと

Terraform を使う上でのつまずきポイントと回避策について学びました。count/for_each の制限事項、plan が成功しても apply が失敗するケース、そしてリファクタリング時の注意点を理解しました。

## 学習内容

### count と for_each の制限事項

#### リソース出力を参照できない

Terraform は **plan フェーズ中**に count と for_each を計算できる必要があります。リソースが作成・変更される前に値が決まっていなければなりません。

| 値の種類 | 例 | count/for_each で使用 |
|----------|-----|----------------------|
| ハードコード | `3`, `["a", "b"]` | ✅ 可能 |
| 変数 | `var.user_names` | ✅ 可能 |
| データソース（静的） | `data.aws_ami.example.id` | ✅ 可能（場合による） |
| リソース出力 | `aws_instance.example.id` | ❌ 不可 |

リソース出力が使えない理由は、以下の処理順序にあります。

```
plan フェーズ
    ↓
count/for_each を計算（この時点で値が必要）
    ↓
apply フェーズ
    ↓
リソースが作成される（出力値が決まる）← 遅すぎる！
```

### 有効なプランも失敗することがある

`terraform validate` や `terraform plan` で問題なしと判定されても、`terraform apply` でエラーになることがあります。

#### 具体例：IAM ユーザーの重複

```hcl
resource "aws_iam_user" "example" {
  name = "user1"
}
```

| コマンド | 結果 |
|----------|------|
| `terraform validate` | ✅ Success |
| `terraform plan` | ✅ 1 to add |
| `terraform apply` | ❌ エラー |

実際のエラーメッセージ：

```
│ Error: creating IAM User (user1): EntityAlreadyExists: User with name user1 already exists.
```

#### なぜ起こるのか

- Terraform は**自身が管理しているリソース**（ステートファイル）しか把握していない
- AWS コンソールや別の Terraform プロジェクトで作成されたリソースは検知できない
- plan 時点では AWS に問い合わせないため、重複を検出できない

#### 対策

| 対策 | 説明 |
|------|------|
| Terraform だけを使う | インフラの管理方法を Terraform に統一し、手動作成を禁止 |
| `import` コマンドを使用 | 既存のインフラを Terraform のステートに取り込む |

```bash
terraform import aws_iam_user.example user1
```

### リファクタリングは難しい

リファクタリングとは、外部的なふるまいは変更せず、既存コードの内部構造を整理することです。

#### Terraform での問題

Terraform はリソースを**識別子**（リソースタイプ + リソース名）で管理しています。

```hcl
# 変更前
resource "aws_instance" "example" { }

# 変更後（リソース名を変更）
resource "aws_instance" "web_server" { }
```

| 変更 | 人間の意図 | Terraform の解釈 |
|------|-----------|------------------|
| `example` → `web_server` | 名前を整理しただけ | `example` を削除して `web_server` を新規作成 |

本番環境で実行すると、EC2 インスタンスが削除されてしまいます。

### リファクタリングの4つの教訓

#### 教訓1：いつも plan コマンドを利用する

変更や作成される内容を事前に確認します。予期しない削除・作成がないかチェックしましょう。

#### 教訓2：削除する前に作成

リソースの置き換え時は、先に置き換え先を作成してから、古いリソースを削除します。

```hcl
lifecycle {
  create_before_destroy = true
}
```

#### 教訓3：リファクタリングにはステートの変更が必要な場合がある

ダウンタイムを起こさずにリファクタリングしたいなら、Terraform ステートも更新します。

| 方法 | 説明 |
|------|------|
| `terraform state mv` | コマンドでステートを移動 |
| `moved` ブロック | コード内でステートの移行を自動実行 |

**terraform state mv の例**：

```bash
terraform state mv aws_instance.example aws_instance.web_server
```

**moved ブロックの例**：

```hcl
moved {
  from = aws_instance.example
  to   = aws_instance.web_server
}
```

**moved ブロックの応用例**：

```hcl
# モジュール名の変更
moved {
  from = module.webserver_cluster
  to   = module.web
}

# モジュール内のリソースをモジュール外に移動
moved {
  from = module.webserver_cluster.aws_security_group.instance
  to   = aws_security_group.instance
}
```

moved ブロックのメリットは、コードとして残るためチームメンバーが変更履歴を追跡できること、そして `terraform plan` で移動が正しく検出されることを確認できる点です。

#### 教訓4：イミュータブルなパラメータもある

一部のパラメータは変更すると**リソースの再作成**が必要になります（インプレース更新ができない）。例えば EC2 の `ami` や RDS の `engine` などがこれに該当します。

## まとめ

| つまずきポイント | 回避策 |
|-----------------|--------|
| count/for_each でリソース出力を参照 | ハードコードや変数を使う |
| plan 成功でも apply 失敗 | Terraform に統一、または import を使用 |
| リソース名変更で削除される | `moved` ブロックや `terraform state mv` を使う |
| イミュータブルなパラメータの変更 | `create_before_destroy` で対応 |

- count/for_each は plan フェーズで計算されるため、リソース出力を参照できない
- Terraform は自身が管理しているリソースしか把握していない
- リファクタリング時は `moved` ブロックを活用してステートを更新する
- いつも plan コマンドで変更内容を事前確認する

## 参考

- [詳解 Terraform 第3版](https://www.oreilly.co.jp/books/9784814400522/) - Yevgeniy Brikman著、松浦隼人訳、オライリージャパン、2023年
- [Refactoring (moved blocks)](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)
- [State: terraform state mv](https://developer.hashicorp.com/terraform/cli/commands/state/mv)
- [Import](https://developer.hashicorp.com/terraform/cli/import)
- [The lifecycle Meta-Argument](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle)