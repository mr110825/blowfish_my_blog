+++
id = "251130070132"
date = '2025-11-30T07:01:32+09:00'
draft = false
title = 'Docker環境でNode.jsを学ぼう_Part2_フロントエンド開発ツール編'
tags = ["ツール", "Babel", "Webpack", "Vite", "ハンズオン・チュートリアル"]
series = ["Docker環境でNode.jsを学ぼう"]
series_order = 2
+++
## はじめに

### 🎯 このメモで理解すべき3つの要点

1. **Babel：JavaScriptトランスパイラ**
   - 最新のJavaScript（ES2015+）を古いブラウザでも動くコードに変換
   - プリセットで変換ルールを管理

2. **Webpack：モジュールバンドラー**
   - 複数のファイル（JS、CSS、画像）を1つにまとめる
   - ローダーで様々なファイル形式に対応

3. **Vite：次世代ビルドツール**
   - Webpackより高速な開発サーバー
   - ESModulesを活用したモダンな設計

### ⚠️ よくある初心者の間違い

- ❌ Babelの設定ファイル（`.babelrc`）を作り忘れてトランスパイルが動かない
- ❌ Webpackのローダーの処理順序（右から左）を理解していない
- ❌ 開発用（dev）と本番用（build）の違いを意識していない

### 🔄 ツールの関係性

```
【開発時の流れ】
  ES2015+ JavaScript
        ↓
  [Babel] トランスパイル（変換）
        ↓
  ES5 JavaScript（古いブラウザ対応）
        ↓
  [Webpack/Vite] バンドル（まとめる）
        ↓
  bundle.js（本番用ファイル）
```

---

## 前提条件

- **Part 1** を完了していること（Docker基礎、Node.js/npm基礎）
- Docker Desktopがインストールされていること

---

## Section 1: Babel（トランスパイラ）

### 1.1 Babelとは？

**Babel**は、JavaScriptのトランスパイラ（変換ツール）です。

#### なぜBabelが必要？

```javascript
// ES2015+（モダンな書き方）
const greet = (name) => `Hello, ${name}!`;
const numbers = [1, 2, 3];
const doubled = numbers.map(n => n * 2);

// ES5（古いブラウザ対応）に変換後
var greet = function(name) {
  return "Hello, " + name + "!";
};
var numbers = [1, 2, 3];
var doubled = numbers.map(function(n) {
  return n * 2;
});
```

#### 主な用途

| 用途 | 説明 |
|------|------|
| **ブラウザ互換性** | 古いブラウザでも最新構文を使用可能に |
| **React JSX** | JSX構文を通常のJavaScriptに変換 |
| **TypeScript** | TypeScriptからJavaScriptへの変換（※） |

**※TypeScript変換の注意点**：Babelでの変換はトランスパイル（構文変換）のみで、型チェックは行われません。型チェックが必要な場合は`tsc`（TypeScriptコンパイラ）と併用するか、`tsc`単体での変換を検討してください。

### 1.2 ハンズオン：Babel環境構築

#### 学習用ディレクトリの作成

```bash
# ローカルで作業ディレクトリを作成
mkdir babel-study && cd babel-study

# Dockerコンテナを起動
docker run -it --rm -v $(pwd):/work -w /work node:20 bash
```

#### プロジェクト初期化とBabelインストール

```bash
# コンテナ内で実行
npm init -y

# Babel関連パッケージをインストール
npm install --save-dev @babel/cli @babel/core @babel/preset-env
```

#### パッケージの説明

| パッケージ | 役割 |
|-----------|------|
| `@babel/core` | Babel本体（変換エンジン） |
| `@babel/cli` | コマンドラインツール |
| `@babel/preset-env` | 環境に応じた変換ルールセット |

### 1.3 Babel設定ファイルの作成

```bash
# .babelrcファイルを作成
cat << 'EOF' > .babelrc
{
  "presets": ["@babel/preset-env"]
}
EOF
```

#### プリセット（preset）とは？

変換に必要なプラグインの集合体です。

| プリセット | 用途 |
|-----------|------|
| `@babel/preset-env` | 最新JS→ターゲット環境対応JS |
| `@babel/preset-react` | JSX→JavaScript変換 |
| `@babel/preset-typescript` | TypeScript→JavaScript変換 |

### 1.4 トランスパイルの実行

#### ソースファイルの作成

```bash
# ディレクトリ構造を作成
mkdir src dist

# ES2015+のコードを作成
cat << 'EOF' > src/app.js
// アロー関数
const greet = (name) => {
  console.log(`Hello, ${name}!`);
};

// テンプレートリテラル
const message = `Current time: ${new Date().toLocaleString()}`;

// 分割代入
const user = { name: 'Alice', age: 25 };
const { name, age } = user;

// スプレッド構文
const numbers = [1, 2, 3];
const moreNumbers = [...numbers, 4, 5];

// クラス構文
class Animal {
  constructor(name) {
    this.name = name;
  }
  
  speak() {
    console.log(`${this.name} makes a sound.`);
  }
}

// 実行
greet('World');
console.log(message);
console.log(`User: ${name}, Age: ${age}`);
console.log('Numbers:', moreNumbers);

const dog = new Animal('Dog');
dog.speak();
EOF
```

#### トランスパイル実行

```bash
# Babelでトランスパイル
npx babel src/app.js -o dist/app.js

# 結果を確認
cat dist/app.js
```

#### 期待される出力（ES5に変換済み）

```javascript
"use strict";

function _typeof(o) { /* ... */ }
function _classCallCheck(a, n) { /* ... */ }
function _defineProperties(e, r) { /* ... */ }
function _createClass(e, r, t) { /* ... */ }
function _toConsumableArray(r) { /* ... */ }

var greet = function greet(name) {
  console.log("Hello, ".concat(name, "!"));
};
var message = "Current time: ".concat(new Date().toLocaleString());
// ... 以下略
```

### 1.5 package.jsonにスクリプトを追加

```bash
# package.jsonを更新
cat << 'EOF' > package.json
{
  "name": "babel-study",
  "version": "1.0.0",
  "scripts": {
    "build": "babel src -d dist",
    "watch": "babel src -d dist --watch"
  },
  "devDependencies": {
    "@babel/cli": "^7.23.0",
    "@babel/core": "^7.23.0",
    "@babel/preset-env": "^7.23.0"
  }
}
EOF

# ビルド実行
npm run build

# 変換後のコードを実行
node dist/app.js
```

#### 期待される出力

```
Hello, World!
Current time: 11/30/2025, 10:00:00 AM
User: Alice, Age: 25
Numbers: [ 1, 2, 3, 4, 5 ]
Dog makes a sound.
```

### 1.6 コンテナ終了と確認

```bash
# コンテナを終了
exit

# ローカルでファイル確認
ls babel-study/
# 出力: dist  node_modules  package-lock.json  package.json  src
```

### ✅ このセクションで学んだこと

- Babelは最新のJavaScriptを古いブラウザ対応のコードに変換するトランスパイラ
- `@babel/preset-env`で環境に応じた変換ルールを適用
- `npx babel src -d dist`でトランスパイル、`--watch`で変更監視

---

## Section 2: Webpack（モジュールバンドラー）

### 2.1 Webpackとは？

**Webpack**は、複数のファイルを1つにまとめる**モジュールバンドラー**です。

#### Webpackの役割

```
【バンドル前】
  src/
  ├── index.js      （エントリーポイント）
  ├── utils.js      （ユーティリティ）
  ├── api.js        （API処理）
  └── style.css     （スタイル）

【バンドル後】
  dist/
  └── bundle.js     （すべてまとまった1ファイル）
```

#### なぜバンドルが必要？

| 理由 | 説明 |
|------|------|
| **HTTPリクエスト削減** | 複数ファイル→1ファイルでリクエスト数減少 |
| **依存関係解決** | モジュール間の依存を自動解決 |
| **最適化** | コード圧縮、不要コード削除 |
| **変換処理** | ローダーでCSS、画像なども処理可能 |

### 2.2 ハンズオン：Webpack環境構築

#### 学習用ディレクトリの作成

```bash
# ローカルで作業ディレクトリを作成
mkdir webpack-study && cd webpack-study

# Dockerコンテナを起動
docker run -it --rm -v $(pwd):/work -w /work node:20 bash
```

#### プロジェクト初期化とWebpackインストール

```bash
# コンテナ内で実行
npm init -y

# Webpack関連パッケージをインストール
npm install --save-dev webpack webpack-cli
```

### 2.3 ディレクトリ構造の作成

```bash
# ディレクトリとファイルを作成
mkdir -p src/modules dist

# モジュールファイルを作成
cat << 'EOF' > src/modules/math.js
// 数学関連の関数
export const add = (a, b) => a + b;
export const subtract = (a, b) => a - b;
export const multiply = (a, b) => a * b;
export const divide = (a, b) => a / b;
EOF

cat << 'EOF' > src/modules/greeting.js
// 挨拶関連の関数
export const hello = (name) => `Hello, ${name}!`;
export const goodbye = (name) => `Goodbye, ${name}!`;
EOF

# エントリーポイントを作成
cat << 'EOF' > src/index.js
// モジュールをインポート
import { add, multiply } from './modules/math.js';
import { hello, goodbye } from './modules/greeting.js';

// 使用例
console.log('=== Math Operations ===');
console.log(`5 + 3 = ${add(5, 3)}`);
console.log(`5 * 3 = ${multiply(5, 3)}`);

console.log('\n=== Greetings ===');
console.log(hello('Webpack'));
console.log(goodbye('Webpack'));
EOF

# HTMLファイルを作成
cat << 'EOF' > dist/index.html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Webpack Study</title>
</head>
<body>
    <h1>Webpack バンドルテスト</h1>
    <p>ブラウザのコンソールを確認してください</p>
    <script src="bundle.js"></script>
</body>
</html>
EOF
```

### 2.4 Webpack設定ファイルの作成

```bash
# webpack.config.jsを作成
cat << 'EOF' > webpack.config.js
const path = require('path');

module.exports = {
  // モード: development（開発）または production（本番）
  mode: 'development',
  
  // エントリーポイント: バンドルの開始地点
  entry: './src/index.js',
  
  // 出力設定
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist')
  }
};
EOF
```

#### 設定項目の解説

| 項目 | 説明 | 値 |
|------|------|-----|
| **mode** | ビルドモード | `development` / `production` |
| **entry** | エントリーポイント | `./src/index.js` |
| **output.filename** | 出力ファイル名 | `bundle.js` |
| **output.path** | 出力ディレクトリ | `dist/` |

### 2.5 バンドル実行

```bash
# package.jsonにスクリプトを追加
cat << 'EOF' > package.json
{
  "name": "webpack-study",
  "version": "1.0.0",
  "scripts": {
    "build": "webpack",
    "dev": "webpack --mode development --watch"
  },
  "devDependencies": {
    "webpack": "^5.89.0",
    "webpack-cli": "^5.1.4"
  }
}
EOF

# ビルド実行
npm run build
```

#### 期待される出力

```
asset bundle.js 4.5 KiB [emitted] (name: main)
runtime modules 670 bytes 3 modules
cacheable modules 524 bytes
  ./src/index.js 389 bytes [built] [code generated]
  ./src/modules/math.js 178 bytes [built] [code generated]
  ./src/modules/greeting.js 135 bytes [built] [code generated]
webpack 5.89.0 compiled successfully in 150 ms
```

```bash
# バンドル結果をNode.jsで実行
node dist/bundle.js
```

#### 期待される出力

```
=== Math Operations ===
5 + 3 = 8
5 * 3 = 15

=== Greetings ===
Hello, Webpack!
Goodbye, Webpack!
```

### 2.6 CSSのバンドル

#### ローダーのインストール

```bash
# CSSローダーをインストール
npm install --save-dev css-loader style-loader
```

#### CSSファイルの作成

```bash
# CSSファイルを作成
cat << 'EOF' > src/style.css
body {
  font-family: Arial, sans-serif;
  background-color: #f0f0f0;
  margin: 0;
  padding: 20px;
}

h1 {
  color: #333;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

p {
  color: #666;
}
EOF
```

#### エントリーポイントでCSSをインポート

```bash
# index.jsを更新
cat << 'EOF' > src/index.js
// CSSをインポート（Webpackが処理）
import './style.css';

// モジュールをインポート
import { add, multiply } from './modules/math.js';
import { hello, goodbye } from './modules/greeting.js';

// 使用例
console.log('=== Math Operations ===');
console.log(`5 + 3 = ${add(5, 3)}`);
console.log(`5 * 3 = ${multiply(5, 3)}`);

console.log('\n=== Greetings ===');
console.log(hello('Webpack'));
console.log(goodbye('Webpack'));

// DOM操作
document.addEventListener('DOMContentLoaded', () => {
  const result = document.createElement('div');
  result.innerHTML = `
    <h2>計算結果</h2>
    <p>5 + 3 = ${add(5, 3)}</p>
    <p>5 × 3 = ${multiply(5, 3)}</p>
  `;
  document.body.appendChild(result);
});
EOF
```

#### Webpack設定にローダーを追加

```bash
# webpack.config.jsを更新
cat << 'EOF' > webpack.config.js
const path = require('path');

module.exports = {
  mode: 'development',
  entry: './src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist')
  },
  // モジュール設定（ローダー）
  module: {
    rules: [
      {
        test: /\.css$/,           // .cssファイルを対象
        use: ['style-loader', 'css-loader']  // 右から左の順で処理
      }
    ]
  }
};
EOF

# 再ビルド
npm run build
```

#### ローダーの処理順序

```
【処理の流れ】
  style.css
      ↓
  css-loader（CSSをJSで扱える形式に変換）
      ↓
  style-loader（<style>タグとしてHTMLに挿入）
      ↓
  bundle.js に含まれる
```

**重要**：`use`配列は**右から左**の順で処理されます。

### 2.7 ブラウザで確認（オプション）

```bash
# コンテナを一度終了
exit

# ポート公開で再起動（簡易サーバー用）
docker run -it --rm -v $(pwd):/work -w /work -p 8080:8080 node:20 bash

# 簡易サーバーをインストール・起動
npm install --save-dev http-server
npx http-server dist -p 8080
```

ブラウザで `http://localhost:8080` にアクセスして確認。

### 2.8 コンテナ終了

```bash
# Ctrl + C でサーバー停止
exit
```

### ✅ このセクションで学んだこと

- Webpackは複数のファイルを1つにまとめるモジュールバンドラー
- `entry`でエントリーポイント、`output`で出力先を設定
- ローダー（css-loader、style-loaderなど）で様々なファイル形式に対応
- ローダーの処理順序は`use`配列の**右から左**

---

## Section 3: Vite（次世代ビルドツール）

### 3.1 Viteとは？

**Vite**（ヴィート：フランス語で「速い」）は、Webpackより高速なフロントエンドビルドツールです。

#### ViteとWebpackの違い

| 項目 | Webpack | Vite |
|------|---------|------|
| **起動速度** | 遅い（全体を事前バンドル） | 速い（必要な部分だけ処理） |
| **HMR** | やや遅い | 非常に高速 |
| **設定** | 複雑になりがち | シンプル |
| **本番ビルド** | 独自バンドラー | Rollup使用 |

#### Viteが高速な理由

```
【Webpack】
  起動時: 全ファイルを解析 → バンドル → サーバー起動
  
【Vite】
  起動時: サーバー起動 → リクエストに応じて必要なファイルだけ処理
```

### 3.2 ハンズオン：Viteプロジェクト作成

#### 学習用ディレクトリの作成

```bash
# ローカルで作業ディレクトリを作成
mkdir vite-study && cd vite-study

# Dockerコンテナを起動（ポート公開）
docker run -it --rm -v $(pwd):/work -w /work -p 5173:5173 node:20 bash
```

#### Viteプロジェクトの作成

```bash
# コンテナ内で実行
npm create vite@latest my-vite-app
```

#### 対話形式での選択

```
? Select a framework: › Vanilla
? Select a variant: › JavaScript
```

**フレームワーク選択肢**：
- Vanilla（素のJS）
- Vue
- React
- Svelte
- その他

### 3.3 プロジェクト構造の確認

```bash
# 作成されたディレクトリに移動
cd my-vite-app

# 構造を確認
ls -la
```

#### 生成されるファイル構造

```
my-vite-app/
├── index.html          # エントリーHTML
├── package.json        # プロジェクト設定
├── public/             # 静的ファイル
│   └── vite.svg
├── src/                # ソースコード
│   ├── counter.js
│   ├── javascript.svg
│   ├── main.js
│   └── style.css
└── vite.config.js      # Vite設定（オプション）
```

### 3.4 依存関係のインストールと起動

```bash
# 依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev -- --host
```

**`--host`オプション**：Dockerコンテナ外からアクセス可能にする

#### 期待される出力

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://172.x.x.x:5173/
```

ブラウザで `http://localhost:5173` にアクセス。

### 3.5 HMR（Hot Module Replacement）の体験

開発サーバーを起動したまま、別のターミナルでファイルを編集：

```bash
# 別のターミナルでコンテナに入る
docker exec -it $(docker ps -q) bash

# ファイルを編集
cd /work/my-vite-app
cat << 'EOF' > src/main.js
import './style.css'

document.querySelector('#app').innerHTML = `
  <div>
    <h1>Hello Vite!</h1>
    <p>ファイルを編集すると自動で反映されます</p>
    <p>現在時刻: ${new Date().toLocaleString()}</p>
  </div>
`
EOF
```

**ブラウザを確認**：ページをリロードせずに変更が反映されます。

### 3.6 本番用ビルド

```bash
# 開発サーバーを停止（Ctrl + C）後
npm run build
```

#### 期待される出力

```
vite v5.x.x building for production...
✓ 2 modules transformed.
dist/index.html                  0.xx kB │ gzip: 0.xx kB
dist/assets/index-xxxxx.css      0.xx kB │ gzip: 0.xx kB
dist/assets/index-xxxxx.js       0.xx kB │ gzip: 0.xx kB
✓ built in xxxms
```

```bash
# ビルド結果を確認
ls dist/
# 出力: assets  index.html  vite.svg
```

### 3.7 ビルド結果のプレビュー

```bash
# プレビューサーバーを起動
npm run preview -- --host
```

ブラウザで `http://localhost:4173` にアクセス。

### 3.8 package.jsonのスクリプト確認

```bash
cat package.json
```

```json
{
  "name": "my-vite-app",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",           // 開発サーバー起動
    "build": "vite build",   // 本番用ビルド
    "preview": "vite preview" // ビルド結果のプレビュー
  },
  "devDependencies": {
    "vite": "^5.0.0"
  }
}
```

### 3.9 コンテナ終了

```bash
exit
```

### ✅ このセクションで学んだこと

- ViteはWebpackより高速な次世代ビルドツール
- ESModulesを活用し、必要なファイルだけを処理するため起動が速い
- `npm run dev`で開発サーバー、`npm run build`で本番ビルド
- HMR（Hot Module Replacement）でファイル変更が即座に反映

---

## Section 4: ツール比較と使い分け

### 4.1 各ツールの役割まとめ

| ツール | カテゴリ | 主な役割 |
|--------|---------|---------|
| **Babel** | トランスパイラ | 新しいJS→古いJS変換 |
| **Webpack** | バンドラー | 複数ファイルを1つにまとめる |
| **Vite** | ビルドツール | 高速な開発環境 + ビルド |

### 4.2 組み合わせパターン

```
【パターン1: Webpack + Babel（従来型）】
  - 大規模プロジェクト
  - 細かい設定が必要な場合
  - レガシーブラウザ対応が必須

【パターン2: Vite（モダン型）】
  - 新規プロジェクト
  - 高速な開発体験を重視
  - モダンブラウザがターゲット

【パターン3: フレームワークのCLI】
  - React: Create React App / Next.js
  - Vue: Vue CLI / Nuxt.js
  - 内部でWebpackやViteを使用
```

### 4.3 学習の優先順位

1. **Vite**（推奨）：新規プロジェクトならこれから始める
2. **Webpack**：既存プロジェクトで使われていることが多い
3. **Babel**：Webpackと組み合わせて使う、または単体で学ぶ

---

## まとめ

### 🎯 学んだこと

#### Babel

| コマンド | 用途 |
|---------|------|
| `npx babel src -d dist` | srcをdistにトランスパイル |
| `npx babel src -d dist --watch` | 変更を監視して自動変換 |

#### Webpack

| コマンド | 用途 |
|---------|------|
| `npx webpack` | バンドル実行 |
| `npx webpack --mode development` | 開発モードでビルド |
| `npx webpack --mode production` | 本番モードでビルド |
| `npx webpack --watch` | 変更を監視 |

#### Vite

| コマンド | 用途 |
|---------|------|
| `npm create vite@latest` | プロジェクト作成 |
| `npm run dev` | 開発サーバー起動 |
| `npm run build` | 本番用ビルド |
| `npm run preview` | ビルド結果プレビュー |

### 📚 次のステップ

- **Part 3**: コード品質ツール編（ESLint、Prettier）
- **Part 4**: その他ツール編（yarn、Sass、nvm/nodenv）

### 🗑️ クリーンアップ

```bash
# 学習ディレクトリを削除
rm -rf babel-study webpack-study vite-study
```

---

## 参考資料

- [Babel公式ドキュメント](https://babeljs.io/docs/)
- [Webpack公式ドキュメント](https://webpack.js.org/)
- [Vite公式ドキュメント](https://vitejs.dev/)