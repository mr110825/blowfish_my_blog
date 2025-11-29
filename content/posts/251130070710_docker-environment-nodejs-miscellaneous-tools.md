+++
id = "251130070710"
date = '2025-11-30T07:07:10+09:00'
draft = false
title = 'Docker環境でNode.jsを学ぼう_Part4_その他ツール編'
tags = ["ツール", "yarn", "Sass", "チュートリアル"]
+++
## はじめに

### 🎯 このメモで理解すべき3つの要点

1. **yarn：npmの代替パッケージマネージャー**
   - npmより高速で厳密なバージョン管理
   - yarn.lockによる依存関係の固定

2. **Sass：CSSの拡張言語**
   - ネスト構文、変数、ミックスインでCSS開発を効率化
   - SCSSファイルからCSSファイルへコンパイル

3. **nvm/nodenv：Node.jsバージョン管理**
   - プロジェクトごとに異なるNode.jsバージョンを使用
   - チーム内でバージョンを統一

### ⚠️ よくある初心者の間違い

- ❌ npmとyarnを同じプロジェクトで混用してしまう
- ❌ SassとSCSS、node-sassとDart Sassの違いを理解していない
- ❌ `nvm use`の設定が新しいターミナルで引き継がれない

---

## 前提条件

- **Part 1** を完了していること（Docker基礎、Node.js/npm基礎）
- Docker Desktopがインストールされていること

---

## Section 1: yarn（パッケージマネージャー）

### 1.1 yarnとは？

**yarn**は、Meta（旧Facebook）が開発したパッケージマネージャーです。

#### npmとyarnの比較

| 項目 | npm | yarn |
|------|-----|------|
| **開発元** | npm, Inc. | Meta（旧Facebook） |
| **登場年** | 2010年 | 2016年 |
| **速度** | 標準的 | 高速（並列インストール） |
| **ロックファイル** | package-lock.json | yarn.lock |
| **オフラインキャッシュ** | あり | より強力 |

#### yarn登場の背景

npmの問題点（特に2016年当時）を解決するために開発されました：
- インストール速度の遅さ
- 依存関係の不安定さ
- セキュリティの懸念

**現在のnpm**は大幅に改善されており、どちらを使うかはチームの方針次第です。

### 1.2 ハンズオン：yarn環境構築

#### 学習用ディレクトリの作成

```bash
# ローカルで作業ディレクトリを作成
mkdir yarn-study && cd yarn-study

# Dockerコンテナを起動
docker run -it --rm -v $(pwd):/work -w /work node:20 bash
```

#### yarnのバージョン確認

```bash
# Node.js 20にはyarnが含まれている（Corepack経由）
corepack enable
yarn --version
```

**Corepack**：Node.js 16.10以降に含まれるパッケージマネージャー管理ツール

### 1.3 yarnでプロジェクト初期化

```bash
# プロジェクト初期化
yarn init -y

# package.jsonを確認
cat package.json
```

#### 生成されるpackage.json

```json
{
  "name": "work",
  "version": "1.0.0",
  "main": "index.js",
  "license": "MIT"
}
```

### 1.4 パッケージのインストール

```bash
# パッケージを追加
yarn add lodash

# 開発用パッケージを追加
yarn add --dev jest

# パッケージを確認
cat package.json
```

#### yarnとnpmのコマンド対比

| npm | yarn | 説明 |
|-----|------|------|
| `npm init -y` | `yarn init -y` | 初期化 |
| `npm install` | `yarn` または `yarn install` | 依存関係インストール |
| `npm install <pkg>` | `yarn add <pkg>` | パッケージ追加 |
| `npm install -D <pkg>` | `yarn add --dev <pkg>` | 開発用パッケージ追加 |
| `npm uninstall <pkg>` | `yarn remove <pkg>` | パッケージ削除 |
| `npm run <script>` | `yarn <script>` | スクリプト実行 |
| `npm update` | `yarn upgrade` | パッケージ更新 |

### 1.5 yarn.lockの役割

```bash
# yarn.lockを確認
cat yarn.lock
```

#### yarn.lockの特徴

- インストールされた**正確なバージョン**を記録
- チームメンバー全員が**同じバージョン**を使用
- **必ずGitにコミット**する

### 1.6 スクリプトの実行

```bash
# package.jsonを更新
cat << 'EOF' > package.json
{
  "name": "yarn-study",
  "version": "1.0.0",
  "scripts": {
    "hello": "echo 'Hello from yarn!'",
    "test": "jest"
  },
  "dependencies": {
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
EOF

# スクリプト実行（runを省略可能）
yarn hello
```

### 1.7 便利なyarnコマンド

```bash
# インストール済みパッケージの一覧
yarn list --depth=0

# 特定パッケージの情報
yarn info lodash

# キャッシュのクリア
yarn cache clean

# アップグレード可能なパッケージを確認
yarn outdated
```

### 1.8 npmとyarnの混用に注意

**重要**：同じプロジェクトでnpmとyarnを混用しないでください。

| 状況 | 問題 |
|------|------|
| `package-lock.json`と`yarn.lock`が両方ある | 依存関係の不整合 |
| `npm install`後に`yarn add` | ロックファイルの競合 |

**対策**：チームで統一して、どちらか一方のみを使用する

### 1.9 コンテナ終了

```bash
exit
```

### ✅ このセクションで学んだこと

- yarnはnpmの代替パッケージマネージャー（高速、厳密なバージョン管理）
- `yarn add`でパッケージ追加、`yarn`で依存関係インストール
- `yarn.lock`でバージョンを固定し、チームで統一
- **重要**：npmとyarnを同じプロジェクトで混用しない

---

## Section 2: Sass（CSSプリプロセッサ）

### 2.1 Sassとは？

**Sass（Syntactically Awesome Style Sheets）**は、CSSを拡張したメタ言語です。

#### Sassの主な機能

| 機能 | 説明 | メリット |
|------|------|---------|
| **ネスト** | セレクタを入れ子で記述 | 構造が明確に |
| **変数** | 値を変数に格納 | 一括変更が容易 |
| **ミックスイン** | スタイルの再利用 | DRY原則 |
| **継承** | スタイルの継承 | コード削減 |
| **演算** | 計算式が使用可能 | 動的な値設定 |

#### SCSS vs Sass記法

| 記法 | 拡張子 | 特徴 |
|------|--------|------|
| **SCSS** | `.scss` | CSSと互換性あり（中括弧使用） |
| **Sass** | `.sass` | インデントベース（中括弧なし） |

**現在はSCSS記法が主流**です。

### 2.2 CSSとSCSSの比較

#### CSS（従来）

```css
/* 従来のCSS：セレクタが長くなりがち */
.navbar {
  background-color: #333;
}

.navbar ul {
  list-style: none;
}

.navbar ul li {
  display: inline-block;
}

.navbar ul li a {
  color: white;
  padding: 10px;
}

.navbar ul li a:hover {
  color: #007bff;
}
```

#### SCSS（Sass）

```scss
/* SCSS：ネストで構造が明確 */
$primary-color: #007bff;
$dark-bg: #333;

.navbar {
  background-color: $dark-bg;
  
  ul {
    list-style: none;
    
    li {
      display: inline-block;
      
      a {
        color: white;
        padding: 10px;
        
        &:hover {
          color: $primary-color;
        }
      }
    }
  }
}
```

### 2.3 ハンズオン：Sass環境構築

#### 学習用ディレクトリの作成

```bash
# ローカルで作業ディレクトリを作成
mkdir sass-study && cd sass-study

# Dockerコンテナを起動
docker run -it --rm -v $(pwd):/work -w /work node:20 bash
```

#### プロジェクト初期化とSassインストール

```bash
# コンテナ内で実行
npm init -y

# Sassをインストール（Dart Sass）
npm install --save-dev sass
```

**注意**：`node-sass`は非推奨です。公式の`sass`（Dart Sass）を使用してください。

### 2.4 ディレクトリ構造の作成

```bash
# ディレクトリを作成
mkdir -p src/scss dist/css
```

### 2.5 SCSSファイルの作成

#### 変数とベーススタイル

```bash
# 変数ファイル
cat << 'EOF' > src/scss/_variables.scss
// カラーパレット
$primary-color: #007bff;
$secondary-color: #6c757d;
$success-color: #28a745;
$danger-color: #dc3545;
$dark-color: #343a40;
$light-color: #f8f9fa;

// フォント
$font-family-base: 'Helvetica Neue', Arial, sans-serif;
$font-size-base: 16px;

// スペーシング
$spacing-unit: 8px;
EOF
```

#### ミックスイン

```bash
# ミックスインファイル
cat << 'EOF' > src/scss/_mixins.scss
// フレックスボックスセンタリング
@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

// ボタンスタイル
@mixin button-style($bg-color, $text-color: white) {
  background-color: $bg-color;
  color: $text-color;
  padding: $spacing-unit * 1.5 $spacing-unit * 3;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: opacity 0.2s;
  
  &:hover {
    opacity: 0.9;
  }
}

// レスポンシブブレークポイント
@mixin respond-to($breakpoint) {
  @if $breakpoint == 'sm' {
    @media (max-width: 576px) { @content; }
  } @else if $breakpoint == 'md' {
    @media (max-width: 768px) { @content; }
  } @else if $breakpoint == 'lg' {
    @media (max-width: 992px) { @content; }
  }
}
EOF
```

#### メインスタイル

```bash
# メインSCSSファイル
cat << 'EOF' > src/scss/style.scss
// パーシャルファイルをインポート
@use 'variables' as *;
@use 'mixins' as *;

// リセット
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

// ベーススタイル
body {
  font-family: $font-family-base;
  font-size: $font-size-base;
  line-height: 1.6;
  color: $dark-color;
  background-color: $light-color;
}

// ヘッダー
.header {
  background-color: $dark-color;
  padding: $spacing-unit * 2;
  
  &__title {
    color: white;
    font-size: $font-size-base * 1.5;
  }
  
  &__nav {
    margin-top: $spacing-unit;
    
    ul {
      list-style: none;
      @include flex-center;
      gap: $spacing-unit * 2;
      
      li a {
        color: $light-color;
        text-decoration: none;
        
        &:hover {
          color: $primary-color;
        }
      }
    }
  }
}

// メインコンテンツ
.main {
  padding: $spacing-unit * 4;
  max-width: 1200px;
  margin: 0 auto;
  
  @include respond-to('md') {
    padding: $spacing-unit * 2;
  }
}

// カード
.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: $spacing-unit * 3;
  margin-bottom: $spacing-unit * 3;
  
  &__title {
    color: $primary-color;
    margin-bottom: $spacing-unit * 2;
  }
  
  &__content {
    color: $secondary-color;
  }
}

// ボタン
.btn {
  &--primary {
    @include button-style($primary-color);
  }
  
  &--secondary {
    @include button-style($secondary-color);
  }
  
  &--success {
    @include button-style($success-color);
  }
  
  &--danger {
    @include button-style($danger-color);
  }
}
EOF
```

### 2.6 Sassのコンパイル

```bash
# SCSSをCSSにコンパイル
npx sass src/scss/style.scss dist/css/style.css

# 生成されたCSSを確認
cat dist/css/style.css
```

### 2.7 ウォッチモード（変更監視）

```bash
# package.jsonを更新
cat << 'EOF' > package.json
{
  "name": "sass-study",
  "version": "1.0.0",
  "scripts": {
    "sass": "sass src/scss/style.scss dist/css/style.css",
    "sass:watch": "sass --watch src/scss/style.scss:dist/css/style.css",
    "sass:compressed": "sass src/scss/style.scss dist/css/style.min.css --style=compressed"
  },
  "devDependencies": {
    "sass": "^1.69.0"
  }
}
EOF

# ウォッチモードで起動（変更を自動検知）
npm run sass:watch
```

**Ctrl + C** で停止

### 2.8 圧縮版CSSの生成

```bash
# 圧縮版を生成（本番用）
npm run sass:compressed

# 圧縮版を確認
cat dist/css/style.min.css
```

### 2.9 HTMLファイルで確認

```bash
# HTMLファイルを作成
cat << 'EOF' > dist/index.html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sass Study</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header class="header">
        <h1 class="header__title">Sass Study</h1>
        <nav class="header__nav">
            <ul>
                <li><a href="#">Home</a></li>
                <li><a href="#">About</a></li>
                <li><a href="#">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main">
        <div class="card">
            <h2 class="card__title">Sassの特徴</h2>
            <p class="card__content">
                ネスト、変数、ミックスインなどの機能でCSSの開発効率が向上します。
            </p>
        </div>
        
        <div class="card">
            <h2 class="card__title">ボタンサンプル</h2>
            <div class="card__content">
                <button class="btn btn--primary">Primary</button>
                <button class="btn btn--secondary">Secondary</button>
                <button class="btn btn--success">Success</button>
                <button class="btn btn--danger">Danger</button>
            </div>
        </div>
    </main>
</body>
</html>
EOF
```

### 2.10 コンテナ終了

```bash
exit
```

### ✅ このセクションで学んだこと

- SassはCSSを拡張したメタ言語（ネスト、変数、ミックスインなど）
- SCSS記法（`.scss`）が現在の主流
- `npx sass <input> <output>`でコンパイル、`--watch`で変更監視
- `--style=compressed`で本番用の圧縮版CSSを生成

---

## Section 3: nvm / nodenv（Node.jsバージョン管理）

> **💡 Docker環境では不要**：このシリーズで学んでいるDocker環境では、`node:18`、`node:20`などイメージを変えるだけでバージョンを切り替えられるため、nvm/nodenvのインストールは**不要**です。このセクションは**ローカル環境を構築する場合の参考情報**として記載しています。

### 3.1 なぜバージョン管理が必要？

| 状況 | 問題 |
|------|------|
| プロジェクトAはNode.js 18が必要 | グローバルのNode.jsは1つだけ |
| プロジェクトBはNode.js 20が必要 | 切り替えが手動で面倒 |
| 古いプロジェクトのメンテナンス | 古いバージョンが必要 |

#### 解決策：バージョン管理ツール

| ツール | 特徴 |
|--------|------|
| **nvm** | 最も普及、シェルスクリプトベース |
| **nodenv** | rbenv系、`.node-version`ファイル |
| **volta** | Rustベース、高速 |
| **fnm** | Rustベース、クロスプラットフォーム |

### 3.2 Docker環境でのバージョン管理

Dockerでは**イメージを変えるだけ**でNode.jsバージョンを切り替えられます。

```bash
# Node.js 18
docker run -it --rm node:18 node -v
# 出力: v18.x.x

# Node.js 20
docker run -it --rm node:20 node -v
# 出力: v20.x.x

# Node.js 22
docker run -it --rm node:22 node -v
# 出力: v22.x.x
```

**メリット**：nvm/nodenvをインストールする必要がない

### 3.3 ハンズオン：nvm（ローカル環境向け）

**注意**：以下はローカルマシン（Mac/Linux）での手順です。Docker内では通常不要です。

#### nvmのインストール

**注意**：以下のバージョン（v0.40.1）は執筆時点のものです。最新バージョンは[nvm公式リポジトリ](https://github.com/nvm-sh/nvm)で確認してください。

```bash
# nvmをインストール（最新バージョンは公式リポジトリを確認）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# シェル設定を再読み込み
source ~/.bashrc  # または ~/.zshrc

# インストール確認
nvm --version
```

#### Node.jsバージョンの管理

```bash
# インストール可能なバージョン一覧
nvm ls-remote

# LTS版をインストール
nvm install --lts

# 特定バージョンをインストール
nvm install 18.19.0
nvm install 20.10.0

# インストール済みバージョン一覧
nvm ls

# バージョンを切り替え（現在のターミナルのみ）
nvm use 18.19.0

# デフォルトバージョンを設定（永続化）
nvm alias default 20.10.0
```

#### .nvmrcファイル

```bash
# プロジェクトにバージョンを固定
echo "20.10.0" > .nvmrc

# .nvmrcのバージョンを使用
nvm use
```

### 3.4 ハンズオン：nodenv（ローカル環境向け）

#### nodenvのインストール

```bash
# nodenvをクローン
git clone https://github.com/nodenv/nodenv.git ~/.nodenv

# node-buildプラグインをインストール
git clone https://github.com/nodenv/node-build.git ~/.nodenv/plugins/node-build

# パスを通す（~/.bashrcまたは~/.zshrcに追加）
echo 'export PATH="$HOME/.nodenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(nodenv init -)"' >> ~/.bashrc

# 再読み込み
source ~/.bashrc

# 確認
nodenv --version
```

#### Node.jsバージョンの管理

```bash
# インストール可能なバージョン一覧
nodenv install -l

# 特定バージョンをインストール
nodenv install 20.10.0

# グローバルバージョンを設定
nodenv global 20.10.0

# プロジェクトごとのバージョン設定（.node-versionファイル作成）
nodenv local 18.19.0

# インストール済みバージョン一覧
nodenv versions

# 現在のバージョン確認
nodenv version
node -v
```

### 3.5 nvmとnodenvの比較

| 項目 | nvm | nodenv |
|------|-----|--------|
| **設定ファイル** | `.nvmrc` | `.node-version` |
| **切り替え方法** | `nvm use` | 自動（ディレクトリ移動時） |
| **シェル統合** | 手動で`nvm use`が必要 | 自動切り替え |
| **プラットフォーム** | Mac/Linux（Windowsはnvm-windows） | Mac/Linux |

### 3.6 Docker環境での実践例

```bash
# プロジェクトごとに異なるNode.jsバージョンを使用

# プロジェクトA（Node.js 18）
cd project-a
docker run -it --rm -v $(pwd):/work -w /work node:18 bash

# プロジェクトB（Node.js 20）
cd project-b
docker run -it --rm -v $(pwd):/work -w /work node:20 bash

# プロジェクトC（Node.js 22）
cd project-c
docker run -it --rm -v $(pwd):/work -w /work node:22 bash
```

### 3.7 docker-compose.ymlでのバージョン指定

```bash
# プロジェクトルートにdocker-compose.ymlを作成
cat << 'EOF' > docker-compose.yml
services:
  app:
    image: node:20  # ここでバージョンを指定
    volumes:
      - .:/work
    working_dir: /work
    command: bash
    tty: true
    stdin_open: true
    ports:
      - "3000:3000"
EOF

# 起動
docker compose up -d

# コンテナに入る
docker compose exec app bash

# 終了
docker compose down
```

### ✅ このセクションで学んだこと

- nvm/nodenvはローカル環境でNode.jsバージョンを管理するツール
- **Docker環境ではイメージ指定（`node:18`、`node:20`など）で代替可能**
- `.nvmrc`や`.node-version`でプロジェクトごとにバージョンを固定
- `docker-compose.yml`でチーム全体のNode.jsバージョンを統一できる

---

## まとめ

### 🎯 学んだこと

#### yarn

| コマンド | 用途 |
|---------|------|
| `yarn init -y` | プロジェクト初期化 |
| `yarn add <pkg>` | パッケージ追加 |
| `yarn add --dev <pkg>` | 開発用パッケージ追加 |
| `yarn remove <pkg>` | パッケージ削除 |
| `yarn` | 依存関係インストール |
| `yarn <script>` | スクリプト実行 |

#### Sass

| コマンド | 用途 |
|---------|------|
| `npx sass <input> <output>` | コンパイル |
| `npx sass --watch <input>:<output>` | 監視モード |
| `npx sass <input> <output> --style=compressed` | 圧縮版生成 |

#### nvm/nodenv（ローカル環境）

| コマンド (nvm) | コマンド (nodenv) | 用途 |
|---------------|------------------|------|
| `nvm install <ver>` | `nodenv install <ver>` | バージョンインストール |
| `nvm use <ver>` | `nodenv local <ver>` | バージョン切り替え |
| `nvm alias default <ver>` | `nodenv global <ver>` | デフォルト設定 |
| `nvm ls` | `nodenv versions` | 一覧表示 |

#### Docker（推奨）

| 方法 | 用途 |
|------|------|
| `docker run node:18` | Node.js 18を使用 |
| `docker run node:20` | Node.js 20を使用 |
| `docker-compose.yml`でimage指定 | プロジェクト設定として管理 |

### 📚 シリーズ全体の振り返り

| Part | 内容 |
|------|------|
| **Part 1** | Docker環境構築、Node.js/npm基礎 |
| **Part 2** | Babel、Webpack、Vite（ビルドツール） |
| **Part 3** | ESLint、Prettier（コード品質） |
| **Part 4** | yarn、Sass、nvm/nodenv（その他ツール） |

### 🗑️ クリーンアップ

```bash
# すべての学習ディレクトリを削除
rm -rf yarn-study sass-study
```

---

## 参考資料

- [yarn公式ドキュメント](https://yarnpkg.com/)
- [Sass公式ドキュメント](https://sass-lang.com/)
- [nvm公式リポジトリ](https://github.com/nvm-sh/nvm)
- [nodenv公式リポジトリ](https://github.com/nodenv/nodenv)