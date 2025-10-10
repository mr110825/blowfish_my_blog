+++
id = "250906221225"
date = '2025-09-06T22:12:25+09:00'
draft = false
title = 'pipコマンド入門'
tags = ["python"]
+++
## pipとは何か？
- **pip**はPythonの公式パッケージ管理ツールで、Pythonコミュニティで広く採用されています。  
- Pythonの標準ライブラリに含まれているか、Python 3.4以降は `ensurepip` によって容易にインストールできるようになりました。  
- 目的は、Pythonの外部モジュールやライブラリ（パッケージ）を簡単に導入し、依存関係も自動管理することです。

## パッケージと依存関係の理解
- **パッケージ**とは：
  - Pythonのコード・データを1つにまとめ配布できる単位。機能ごとに分かれている。  
  - 例：Web開発用の`Flask`、HTTP通信を助ける`requests`など。  

- **依存関係**とは：
  - あるパッケージが動作するために必要な、他のパッケージのこと。  
  - 例えば`Flask`は`Werkzeug`や`Jinja2`など使っているため、それらが事前にインストールされている必要がある。  
  - pipは依存関係も自動的に解決し、必要なパッケージを連鎖的にインストールしてくれる。

## 仮想環境（venv）を使う理由
- システム全体に影響を与えず、プロジェクト単位でパッケージを管理できる。  
- 依存関係の衝突を避け、異なるプロジェクトで別バージョンのパッケージを共存可能にする。  
- 開発・テスト用のクリーンな環境を手軽に作られる。

```bash
mkdir my_project      # プロジェクトディレクトリ作成
cd my_project

python3 -m venv venv  # 仮想環境作成

source venv/bin/activate  # 仮想環境有効化 (Linux/macOS)
# Windowsの場合
# venv\Scripts\activate.bat  # cmd
# または
# venv\Scripts\Activate.ps1   # PowerShell
```

## pipの基本操作

### バージョン確認・インストール確認
```bash
pip -V  # pipのバージョンとPython環境を確認
```

もしpipがない場合や更新したい場合は、以下：
```bash
python3 -m ensurepip --default-pip  # pipをインストール
pip install --upgrade pip            # pipのアップグレード
```

### パッケージのインストール
```bash
pip install Flask               # 最新版をインストール
pip install Flask==2.3.3       # バージョン指定してインストール
pip install "Flask>=2.2,<3.0"  # 範囲指定インストール
```

### パッケージのアンインストール
```bash
pip uninstall Flask             # パッケージ削除
```

### インストール済みパッケージの確認

- ライブラリ一覧を見たい時は以下コマンドを使う。

```bash
pip list     # パッケージとバージョンの一覧
pip freeze   # requirements.txt形式でパッケージ＋バージョンを表示
```

- `pip freeze` は環境の再現性を確保するのに役立つ。  

### パッケージの詳細情報
```bash
pip show Flask

# 表示される例:
# Name: Flask
# Version: 2.3.3
# Summary: A simple framework for building complex web applications.
# Home-page: https://palletsprojects.com/p/flask/
# Author: Armin Ronacher
# Author-email: armin.ronacher@active-4.com
# License: BSD-3-Clause
# Location: /path/to/venv/lib/python3.12/site-packages
# Requires: Werkzeug, Jinja2
# Required-by: 
```

## requirements.txt の利用
- 複数パッケージをまとめて管理・共有できるテキストファイル。  
- チーム開発やCI/CD環境での環境再現に必須。

```bash
# 現在の環境のパッケージをファイル化
pip freeze > requirements.txt

# ファイルから環境を再現
pip install -r requirements.txt
```

## ベストプラクティス・注意点

- **仮想環境を必ず使う**  
  システム環境に影響を与えず複数プロジェクトを管理できる  

- **バージョン固定を行い再現性を担保**  
  `requirements.txt`や`pip freeze`を活用し、同じバージョンセットを共有・再利用する  

- **C拡張モジュールの依存に注意**  
  MySQLクライアントや画像処理ライブラリなどは、Python依存に加えシステム側にもライブラリが必要な場合がある。  

- **pip のアップグレードを定期的に**  
  セキュリティやバグ修正、新機能のために最新版を利用する  

## まとめ コマンド一覧（代表例）

| コマンド                         | 説明                                      |
|----------------------------------|-------------------------------------------|
| `pip install <pkg>`              | パッケージを最新バージョンでインストール             |
| `pip install <pkg>==<version>`   | 指定バージョンでインストール                          |
| `pip uninstall <pkg>`            | パッケージをアンインストール                          |
| `pip list`                       | インストール済みパッケージの一覧表示                   |
| `pip freeze`                     | 環境再現用のrequirements.txt形式で一覧出力             |
| `pip show <pkg>`                 | パッケージの詳細情報（依存・場所など）                  |
| `pip install -r requirements.txt` | requirements.txtファイルに基づいて一括インストール       |
| `pip install --upgrade pip`      | pip自身のアップデート                                |
