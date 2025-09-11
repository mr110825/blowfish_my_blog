+++
date = '2025-09-07T12:08:59+09:00'
draft = false
title = 'requirements.txt入門'
tags = ["python"]
+++
## requirements.txtとは
requirements.txtはPythonプロジェクトで使用しているパッケージ名とバージョンを記述したテキストファイルです。
「requirements」は英語で「要件」や「必要条件」を意味します。

## requirements.txtの書き方

```txt
# パッケージ名のみ記述すると、その時点での最新版がインストールされます
requests
numpy
pandas

# バージョンを指定する場合は「==」で完全一致、「>=」「<」などで範囲を指定します
Flask==3.0.3
SQLAlchemy>=2.0.0,<3.0.0
```

## requirements.txtを実行するコマンド

```bash
# 既存の環境からrequirements.txtを作成する場合、pipのfreezeコマンドを使用
pip freeze > requirements.txt

# requirements.txtからパッケージをインストール
pip install -r requirements.txt
```

## 参考リンク
- [エンべーダー：requirements.txtの使い方](https://envader.plus/course/8/scenario/1073)