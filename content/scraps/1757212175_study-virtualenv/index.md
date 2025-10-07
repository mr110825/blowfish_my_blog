+++
id = "1757212175"
date = '2025-09-07T11:29:35+09:00'
draft = false
title = 'virtualenv入門'
tags = ["python"]
+++
## virtualenvとは？

virtualenvは、Pythonで複数の仮想環境を作成・管理できるツールです。これにより、異なるアプリやプロジェクトごとにパッケージ・バージョンの設定を分離できます

## Pythonにおける仮想環境とは？

仮想環境とは、一時的・独立したPythonの実行環境です。これを使うことで、システムのPython設定に影響を与えず、個別にパッケージ導入や、Pythonバージョンの切替ができます。

## venvとvirtualenvの違い

venvはPython3.3以降で標準搭載されている機能ですが、Python本体のバージョン管理はできません。

virtualenvは、仮想環境ごとに異なるPythonバージョンを指定して管理可能です。これにより、特定の旧バージョンPythonでの動作検証など柔軟に対応できます。

## virtualenvのinstall

```bash
# virtualenvは標準ではインストールされていないため、pipで導入が必要
sudo pip install virtualenv
```

## virtualenvコマンドで新しい環境の作成

```bash
# プロジェクト用ディレクトリを準備
mkdir プロジェクトディレクトリ名 
cd プロジェクトディレクトリ名

# 通常の仮想環境作成
python3 -m virtualenv 仮想環境名

# 特定バージョンのPythonを指定する場合（要事前インストール）
python3 -m virtualenv -p 利用したいPythonのバージョン(例: python3.6) 環境名
```

### 仮想環境の起動(activate)・停止(deactivate)

```bash
# 仮想環境を有効化
source 仮想環境名/bin/activate
# コマンドライン先頭に(仮想環境名)が表示されたら正常起動

# 仮想環境を終了
deactivate
# (仮想環境名)表示が消えたら仮想環境解除
```

## 参考リンク

[エンべーダー：venvの使い方](https://envader.plus/course/8/scenario/1074)