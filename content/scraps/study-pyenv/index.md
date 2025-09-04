+++
date = '2025-09-04T20:22:08+09:00'
draft = false
title = '勉強メモ：pyenv'
+++
## pyenvとは？
pyenvは、Pythonの複数のバージョンを簡単に切り替えて管理するためのツールです。プロジェクトごとに異なるPythonバージョンを利用したい場合などに役立ちます。

## インストール手順 (Ubuntu)

### 1. 依存関係のインストール
Pythonのビルドに必要なパッケージをあらかじめインストールします。
```bash
sudo apt update
sudo apt install build-essential libffi-dev libssl-dev zlib1g-dev liblzma-dev libbz2-dev libreadline-dev libsqlite3-dev tk-dev git
```
※[参考記事：Ubuntuにpyenvをインストール](https://zenn.dev/hr0t15/articles/8ae3564bde2cce)

### 2. pyenvのインストール
GitHubからpyenvのリポジトリをクローンします。
```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
```

### 3. 環境変数の設定（パスを通す）
`~/.bashrc`（Zshの場合は `~/.zshrc`）に以下の3行を追記します。
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
```
設定を反映させるため、ターミナルを再起動するか、`source ~/.bashrc` を実行します。

## 基本的な使い方

### Pythonのインストール
```bash
# インストール可能なバージョンの一覧を表示
pyenv install --list

# 指定したバージョンをインストール
pyenv install 3.10.4
```

### 使用するPythonのバージョンを切り替える
pyenvでは、`global` と `local` の2つの方法でバージョンを指定できます。

- `global`: システム全体でデフォルトとして使用するバージョンを設定します。
- `local`: 現在のディレクトリ（プロジェクト）でのみ有効なバージョンを設定します。

```bash
# インストール済みのバージョン一覧を確認
pyenv versions

# 全体で使うバージョンを設定
pyenv global 3.10.4

# 現在のディレクトリで使うバージョンを設定（.python-versionファイルが作成される）
pyenv local 3.9.13
```

### Pythonのアンインストール
```bash
pyenv uninstall 3.10.4
```

## pyenvのアップデート

### 方法1: pyenv-updateプラグインを使う
`pyenv-update`というプラグインを導入すると、`pyenv update`コマンドで簡単に更新できます。

```bash
# 1. プラグインをインストール（初回のみ）
git clone https://github.com/pyenv/pyenv-update.git $(pyenv root)/plugins/pyenv-update

# 2. pyenvをアップデート
pyenv update
```

### 方法2: gitで直接アップデートする
pyenv本体はgitリポジトリなので、`git pull`で直接更新することも可能です。
```bash
cd $(pyenv root)
git pull
```

## インストール時のトラブルシューティング
`pyenv install` 時にエラーが出た場合の対処法です。多くは依存パッケージ不足が原因です。

#### `configure: error: no acceptable C compiler found in $PATH`
Cコンパイラが見つからないエラーです。`build-essential`をインストールします。
```bash
sudo apt install build-essential
```

#### `zipimport.ZipImportError: can't decompress data; zlib not available`
zlibライブラリがないエラーです。`zlib1g-dev`をインストールします。
```bash
sudo apt install zlib1g-dev
```
