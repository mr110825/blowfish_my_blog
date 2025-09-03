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

---

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