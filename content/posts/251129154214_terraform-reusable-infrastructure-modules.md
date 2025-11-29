+++
id = "251129154214"
date = '2025-11-29T15:42:14+09:00'
draft = false
title = 'Terraformモジュールで再利用可能なインフラを作る'
tags = ["インフラ", "Terraform", "AWS", "実践"]
+++

## 今日学んだこと

[前回の記事]({{< ref "/posts/251128193149_terraform-file-layout-separation" >}})でファイルレイアウトによる環境分離を学んだが、ステージングと本番で**同じコードを重複して書く**問題が残っていた。今回は**Terraformモジュール**を使って、DRY原則をインフラコードに適用する方法を学んだ。

### モジュール化で得られるメリット

| メリット | 説明 |
|---------|------|
| **DRY原則** | 同じコードを複数環境で再利用 |
| **保守性** | 1箇所の修正で全環境に反映 |
| **柔軟性** | 入力変数で環境ごとのカスタマイズ |
| **安全性** | バージョン管理でテスト済みコードのみ本番適用 |

---

## モジュールとは

> **フォルダ内にあるTerraform設定ファイル（.tfファイル）の集まり = モジュール**

つまり、これまで作成してきたディレクトリも「モジュール」といえる。

| 種類 | 説明 |
|------|------|
| **ルートモジュール** | `terraform apply`を直接実行するフォルダ |
| **再利用可能なモジュール** | 他のモジュールから呼び出されるフォルダ |

### 基本構文

```hcl
module "<NAME>" {
  source = "<SOURCE>"
  # 設定（入力変数など）
}
```

`source`にはローカルパス、GitHub URL、Terraform Registryなどを指定できる。

---

## ディレクトリ構成の変更

前回の`stage/`のみの構成から、モジュールを分離した構成に変更。

```
├── modules/                      # 再利用可能なモジュール
│   └── services/
│       └── webserver-cluster/
│           ├── main.tf
│           ├── variables.tf
│           ├── outputs.tf
│           └── user-data.sh
│
└── live/
    ├── stage/                    # ステージング環境
    │   └── services/
    │       └── webserver-cluster/
    │           └── main.tf
    └── prod/                     # 本番環境
        └── services/
            └── webserver-cluster/
                └── main.tf
```

| ディレクトリ | 役割 |
|-------------|------|
| `modules/` | 環境に依存しない再利用可能コード |
| `live/stage/` | ステージング環境のルートモジュール |
| `live/prod/` | 本番環境のルートモジュール |

---

## モジュールの構成要素

プログラミングの関数と対比すると理解しやすい。

| Terraformモジュール | プログラミング | 説明 |
|---------------------|---------------|------|
| モジュール | 関数 | 再利用可能なコードの塊 |
| `variable` | 引数 | モジュールに値を渡す |
| `locals` | ローカル変数 | モジュール内部の計算・定数 |
| `output` | 戻り値 | モジュールから値を返す |

以降のセクションで、それぞれの詳細と使い方を見ていく。

---

## 入力変数（variable）

### なぜ必要か

前回のコードにはハードコードされた値が多い。

| ハードコード | 問題 |
|--------------|------|
| `instance_type = "t2.micro"` | prodでは大きいインスタンスが必要 |
| `min_size = 2` | 環境ごとにスケールを変えたい |
| `key = "stage/..."` | prodで使うとstageのDBを参照 |

### 定義例

**modules/services/webserver-cluster/variables.tf**

```hcl
variable "cluster_name" {
  description = "クラスターリソースの名前"
  type        = string
}

variable "instance_type" {
  description = "起動するEC2タイプの種類"
  type        = string
}

variable "min_size" {
  description = "EC2インスタンスのASGの最小値"
  type        = number
}

variable "max_size" {
  description = "EC2インスタンスのASGの最大値"
  type        = number
}

variable "db_remote_state_bucket" {
  description = "S3バケットの名前（データベースのリモートステート）"
  type        = string
}

variable "db_remote_state_key" {
  description = "S3でのデータベースのリモートステートのパス"
  type        = string
}
```

### 呼び出し側での値の指定

**live/stage/services/webserver-cluster/main.tf**

```hcl
provider "aws" {
  region = "ap-northeast-1"
}

module "webserver_cluster" {
  source = "../../../modules/services/webserver-cluster"

  cluster_name           = "webservers-stage"
  db_remote_state_bucket = "tf-state-backend-20251128"
  db_remote_state_key    = "stage/data-stores/mysql/terraform.tfstate"

  instance_type = "t2.micro"
  min_size      = 2
  max_size      = 2
}
```

**live/prod/services/webserver-cluster/main.tf**

```hcl
module "webserver_cluster" {
  source = "../../../modules/services/webserver-cluster"

  cluster_name           = "webservers-prod"
  db_remote_state_bucket = "tf-state-backend-20251128"
  db_remote_state_key    = "prod/data-stores/mysql/terraform.tfstate"

  instance_type = "m4.large"  # より大きいインスタンス
  min_size      = 2
  max_size      = 10          # スケールアウト可能
}
```

---

## ローカル値（locals）

### variable との違い

| 種類 | 外部から設定 | 用途 |
|------|:-----------:|------|
| `variable` | 可能 | モジュールのAPI（外部に公開） |
| `locals` | 不可 | モジュール内部の定数・計算 |

ポート番号など**変更されたくない値**は`locals`で定義する。

```hcl
locals {
  http_port    = 80
  any_port     = 0
  any_protocol = "-1"
  tcp_protocol = "tcp"
  all_ips      = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "allow_http_inbound" {
  type              = "ingress"
  security_group_id = aws_security_group.alb.id
  from_port         = local.http_port  # 80
  to_port           = local.http_port
  protocol          = local.tcp_protocol
  cidr_blocks       = local.all_ips
}
```

マジックナンバー `80` より `local.http_port` の方が意図が明確。

---

## 出力（output）

### なぜ必要か

本番環境のみにスケジュール設定を追加したい場合、モジュール内のASG名を外部から参照する必要がある。

**modules/services/webserver-cluster/outputs.tf**

```hcl
output "asg_name" {
  value       = aws_autoscaling_group.example.name
  description = "The name of the Auto Scaling Group"
}

output "alb_security_group_id" {
  value       = aws_security_group.alb.id
  description = "ALBのセキュリティグループID"
}
```

**live/prod/main.tf**（本番のみスケジュール追加）

```hcl
resource "aws_autoscaling_schedule" "scale_out_during_business_hours" {
  scheduled_action_name  = "scale-out-during-business-hours"
  min_size               = 2
  max_size               = 10
  desired_capacity       = 10
  recurrence             = "0 9 * * *"  # 毎日9時

  autoscaling_group_name = module.webserver_cluster.asg_name  # 出力を参照
}
```

---

## 注意点1: ファイルパス

### 問題

相対パス `"user-data.sh"` は**ルートモジュールからの相対パス**として解釈される。モジュール内のファイルを参照できない。

### 解決策: path.module

```hcl
# Before（動かない）
user_data = base64encode(templatefile("user-data.sh", { ... }))

# After（正しく動く）
user_data = base64encode(templatefile("${path.module}/user-data.sh", { ... }))
```

| パス参照 | 指す場所 |
|---------|---------|
| `path.module` | モジュール定義があるディレクトリ |
| `path.root` | ルートモジュールのディレクトリ |
| `path.cwd` | `terraform apply`を実行したディレクトリ |

---

## 注意点2: インラインブロック

### 問題

セキュリティグループの`ingress`/`egress`には2つの書き方がある。

**インラインブロック**
```hcl
resource "aws_security_group" "alb" {
  name = "${var.cluster_name}-alb"

  ingress {  # リソース内に直接書く
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

**別リソース**
```hcl
resource "aws_security_group" "alb" {
  name = "${var.cluster_name}-alb"
}

resource "aws_security_group_rule" "allow_http" {
  type              = "ingress"
  security_group_id = aws_security_group.alb.id
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}
```

### モジュールでは別リソースを推奨

| 方法 | 柔軟性 | 理由 |
|------|:------:|------|
| インラインブロック | 低 | 呼び出し側でルール追加不可 |
| 別リソース | 高 | 呼び出し側で追加ルール定義可能 |

別リソースにすれば、ステージング環境のみテスト用ポートを追加、といったカスタマイズが可能。

```hcl
# live/stage/main.tf - テスト用ポートを追加
resource "aws_security_group_rule" "allow_testing" {
  type              = "ingress"
  security_group_id = module.webserver_cluster.alb_security_group_id
  from_port         = 12345
  to_port           = 12345
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}
```

---

## モジュールのバージョン管理

### 問題

ローカルパス参照では、モジュールを変更すると**全環境に即座に影響**する。

### 解決策: GitリポジトリとSemVer

1. モジュールを別リポジトリに分離
2. Gitタグでバージョンを付与

```bash
git tag -a "v0.0.1" -m "First release"
git push --follow-tags
```

3. 環境ごとに異なるバージョンを参照

```hcl
# stage: 新バージョンをテスト
source = "github.com/user/modules//services/webserver-cluster?ref=v0.0.2"

# prod: 安定版を維持
source = "github.com/user/modules//services/webserver-cluster?ref=v0.0.1"
```

**GitHubでソースURL指定方法**：`github.com/user/repo`

### セマンティックバージョニング

| 変更内容 | バージョン |
|----------|-----------|
| バグ修正 | PATCH（v0.0.1 → v0.0.2） |
| 後方互換のある機能追加 | MINOR（v0.0.2 → v0.1.0） |
| 破壊的変更 | MAJOR（v0.1.0 → v1.0.0） |

---

## エラー対応メモ

### terraform init の実行場所

```
Terraform initialized in an empty directory!
```

→ `.tf`ファイルがあるディレクトリ（ルートモジュール）で実行すること。

### backend設定がモジュール内に残っている

```
Error: Failed to get existing workspaces: S3 bucket does not exist.
```

→ `provider`と`terraform { backend }`はルートモジュールのみに書く。再利用可能なモジュールからは削除。

---

## モジュールに含めるべきもの

| 設定 | modules/ | live/ |
|------|:--------:|:-----:|
| `provider` | - | 必須 |
| `terraform { backend }` | - | 必須 |
| `resource` | 必須 | 任意 |
| `variable` | 必須 | 任意 |
| `output` | 必須 | 任意 |
| `locals` | 任意 | 任意 |

---

## 参照方法の比較

ここまで学んだ各要素の参照方法をまとめる。

| 種類 | 文法 | 例 |
|------|------|-----|
| 入力変数 | `var.<NAME>` | `var.cluster_name` |
| ローカル値 | `local.<NAME>` | `local.http_port` |
| モジュール出力 | `module.<MODULE>.<OUTPUT>` | `module.webserver_cluster.asg_name` |
| パス参照 | `path.<TYPE>` | `path.module` |

---

## まとめ

| 学んだこと | 内容 |
|----------|------|
| モジュールの基礎 | フォルダ = モジュール |
| 入力変数（variable） | 環境ごとの違いを吸収 |
| ローカル値（locals） | 変更されたくない内部定数 |
| 出力（output） | 外部から参照可能な値 |
| ファイルパス | `path.module`で正しく参照 |
| インラインブロック | 別リソースの方が柔軟 |
| バージョン管理 | Git + SemVerで安全なデプロイ |

### モジュール化のメリット

1. **DRY原則**: 同じコードを複数環境で再利用
2. **保守性**: 1箇所の修正で全環境に反映
3. **柔軟性**: 入力変数で環境ごとのカスタマイズ
4. **安全性**: バージョン管理でテスト済みコードのみ本番適用

---

## 参考

- [詳解 Terraform 第3版](https://www.oreilly.co.jp/books/9784814400522/) - Yevgeniy Brikman著、松浦隼人訳、オライリージャパン、2023年
- [Terraform公式ドキュメント](https://developer.hashicorp.com/terraform/docs)
- [前回の記事: ファイルレイアウトとterraform_remote_state]({{< ref "/posts/251128193149_terraform-file-layout-separation" >}})
