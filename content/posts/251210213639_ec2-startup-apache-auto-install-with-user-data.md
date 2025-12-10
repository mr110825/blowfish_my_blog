+++
id = "251210213639"
date = '2025-12-10T21:36:39+09:00'
draft = false
title = 'user_dataでEC2起動時にApacheを自動インストール'
tags = ["インフラ", "AWS", "Terraform", "実践", "ハンズオン・チュートリアル"]
+++
## 今日学んだこと

Terraformの `user_data` を使って、EC2起動時にApacheを自動インストールする方法を学びました。手動でSSH接続してセットアップする手間を省き、インフラ構築を完全に自動化できます。

## 学習内容

### user_dataとは

EC2インスタンスの**初回起動時**に実行されるスクリプトです。OSの初期設定やソフトウェアのインストールを自動化できます。

### Terraformコード
```hcl
resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.web.id]
  key_name               = aws_key_pair.main.key_name

  user_data = <<-EOF
              #!/bin/bash
              dnf update -y
              dnf install -y httpd
              systemctl start httpd
              systemctl enable httpd
              EOF

  tags = {
    Name = "practice-web"
  }
}
```

### ヒアドキュメント構文
```hcl
user_data = <<-EOF
            #!/bin/bash
            コマンド1
            コマンド2
            EOF
```

| 要素 | 説明 |
|------|------|
| `<<-EOF` | ヒアドキュメント開始。`-` があると先頭のタブを除去 |
| `#!/bin/bash` | シェバン。Bashで実行することを指定 |
| `EOF` | ヒアドキュメント終了（任意の文字列でOK） |

#### `<<EOF` と `<<-EOF` の違い
```hcl
# <<EOF（ハイフンなし）: インデントがそのまま含まれる
user_data = <<EOF
#!/bin/bash
echo "hello"
EOF

# <<-EOF（ハイフンあり）: 先頭のタブを除去
user_data = <<-EOF
              #!/bin/bash
              echo "hello"
              EOF
```

Terraformコードのインデントを揃えたい場合は `<<-EOF` を使います。

> 💡 補足：標準のシェルでは `-` はタブのみ除去しますが、Terraform/HCLでは独自処理でインデントを適切に処理します。

### スクリプトの内容
```bash
#!/bin/bash
dnf update -y          # パッケージを最新化
dnf install -y httpd   # Apacheをインストール
systemctl start httpd  # Apacheを起動
systemctl enable httpd # OS再起動時に自動起動
```

Amazon Linux 2023ではパッケージマネージャーが `dnf` になっています（旧Amazon Linux 2は `yum`）。

### 動作確認

EC2作成後、パブリックIPにHTTPアクセスします。
```
http://<パブリックIP>
```

「It works!」が表示されれば成功です。

### トラブルシューティング

接続できない場合の確認ポイント：

1. **セキュリティグループ**: ポート80（HTTP）が許可されているか
2. **user_dataログ**: SSH接続して以下で確認
   ```bash
   sudo cat /var/log/cloud-init-output.log
   ```
3. **Apache状態**: `systemctl status httpd` で起動状態を確認

### user_dataの注意点

| 注意点 | 詳細 |
|--------|------|
| 初回起動時のみ | 再起動しても再実行されない |
| 変更時は再作成 | user_dataを変更すると、EC2はdestroy→createになる |
| ログ確認 | `/var/log/cloud-init-output.log` で実行結果を確認可能 |
| 実行完了を待たない | EC2が「running」でもスクリプト実行中の場合がある |

### 応用：変数を埋め込む
```hcl
variable "app_name" {
  default = "myapp"
}

resource "aws_instance" "web" {
  # ...

  user_data = <<-EOF
              #!/bin/bash
              echo "Deploying ${var.app_name}" > /var/www/html/index.html
              EOF
}
```

ヒアドキュメント内でも `${var.xxx}` で変数展開が可能です。

## まとめ

| トピック | 内容 |
|----------|------|
| user_data | EC2初回起動時に実行されるスクリプト |
| ヒアドキュメント | `<<-EOF ... EOF` で複数行文字列を記述 |
| `-` の意味 | 先頭のタブを除去（Terraformではスペースも処理される） |
| 初回のみ | 再起動では再実行されない。変更時はEC2再作成 |

## 参考

- [Amazon Web Services 基礎からのネットワーク＆サーバー構築 改訂4版](https://www.nikkeibp.co.jp/atclpubmkt/book/22/295640/)
- [Terraform AWS Provider - EC2 Instance user_data](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#user_data)
- [AWS EC2 User Data ドキュメント](https://docs.aws.amazon.com/ja_jp/AWSEC2/latest/UserGuide/user-data.html)