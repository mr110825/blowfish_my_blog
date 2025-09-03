+++
date = '2025-09-03T07:52:57+09:00'
draft = false
title = 'Python勉強メモ'
+++

## はじめに
python用の勉強メモをスクラップとしてまとめます。

## Pythonとは
Pythonは1991年に開発された、シンプルで読みやすい文法が特徴のプログラミング言語です。

- インデント（字下げ）でコードのブロックを表現することが大きな特徴です。
- 文法が比較的シンプルなため、プログラミング初心者でも学習しやすい言語と言われています。
- 近年では、AI開発や機械学習、データ分析などの分野で特に広く活用されています。

## Pythonのインストール方法（Linux/Debian系）

Linux（DebianやUbuntuなど）環境でPython3をインストールする手順です。

```bash
sudo apt update
sudo apt install -y python3
```

**コマンドの解説**
- `sudo apt update`: インストール可能なパッケージのリストを最新の状態に更新します。
- `sudo apt install -y python3`: Python3をインストールします。
    - `-y`オプションは、インストール中の確認メッセージに対して自動的に「Yes」と回答するためのものです。

### インストール後の確認

インストールが正常に完了したかを確認するには、ターミナルで以下のコマンドを実行します。

```bash
python3 --version
```

次のように、インストールされたPythonのバージョンが表示されれば成功です。
```
Python 3.x.x
```
※ `x.x`の部分には、インストールされたバージョン番号が表示されます。

### Pythonの対話モード

Pythonのプログラムを実行するには、主に2つの方法があります。
- **対話モード:** ターミナルで直接コードを一行ずつ入力して実行する方法。
- **スクリプト実行:** `.py`ファイルにコードを記述し、そのファイルを一括で実行する方法。

対話モードは、ターミナルで`python3`コマンドを実行すると開始できます。コードを試したり、簡単な計算をしたりするのに便利です。

```
$ python3
Python 3.x.x (default, ...
Type "help", "copyright", "credits" or "license" for more information.
>>> print("Hello, Python!")
Hello, Python!
>>>
```

対話モードを終了するには、`exit()`と入力するか、`Ctrl + D`を押します。

## Numpy
{{< article link="/posts/study-numpy/">}}

## pyenvとは？
Pythonのバージョン管理を簡単にするツール。

## pyenvのインストール手順 (Ubuntu)

### 依存パッケージのインストール
Pythonのビルドに必要なパッケージをインストールします。
```bash
sudo apt update
sudo apt install build-essential libffi-dev libssl-dev zlib1g-dev liblzma-dev libbz2-dev libreadline-dev libsqlite3-dev tk-dev git
```
※[参考記事：Ubuntuにpyenvをインストール](https://zenn.dev/hr0t15/articles/8ae3564bde2cce)

### pyenvのインストール
```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
```

### パスを通す
`~/.bashrc` に以下を追記します。
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
```
ターミナルを再起動するか、`source ~/.bashrc` を実行して設定を反映させます。

### Pythonのインストール
```bash
# インストール可能なバージョン一覧を表示
pyenv install --list

# 指定したバージョンをインストール
pyenv install 3.10.4
```

### pyenvインストール時のトラブルシューティング
`pyenv install` 時にエラーが出た場合の対処法です。多くは依存パッケージ不足が原因です。

#### `configure: error: no acceptable C compiler found in $PATH`
Cコンパイラがありません。`build-essential`をインストールします。
```bash
sudo apt install build-essential
```

#### `zipimport.ZipImportError: can't decompress data; zlib not available`
zlibライブラリがありません。`zlib1g-dev`をインストールします。
```bash
sudo apt install zlib1g-dev
```