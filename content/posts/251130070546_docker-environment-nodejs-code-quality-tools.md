+++
id = "251130070546"
date = '2025-11-30T07:05:46+09:00'
draft = false
title = 'Docker環境でNode.jsを学ぼう_Part3_コード品質ツール編'
tags = ["ツール", "ESLint", "Prettier", "ハンズオン・チュートリアル"]
series = ["Docker環境でNode.jsを学ぼう"]
series_order = 3
+++
## はじめに

### 🎯 このメモで理解すべき3つの要点

1. **ESLint：静的コード解析ツール**
   - コードの問題点（バグの可能性、非推奨の書き方）を検出
   - プロジェクト全体でコーディングルールを統一

2. **Prettier：コードフォーマッター**
   - コードの見た目（インデント、改行、引用符など）を自動整形
   - チーム内でコードスタイルを統一

3. **ESLintとPrettierの違いと併用**
   - ESLint = 品質・バグ検出
   - Prettier = 見た目の整形
   - 両者は競合する部分があるため、設定で調整が必要

### ⚠️ よくある初心者の間違い

- ❌ ESLintとPrettierの役割を混同している
- ❌ 両方を入れたら設定が競合してエラーになる
- ❌ ルールが厳しすぎて開発効率が落ちる

### 🔄 ESLintとPrettierの関係

```
【コード品質の2つの側面】

ESLint（静的解析）
  ├── バグの可能性を検出
  ├── 未使用変数の警告
  ├── 危険なパターンの検出
  └── コーディング規約の強制

Prettier（フォーマット）
  ├── インデントの統一
  ├── 引用符の統一（シングル/ダブル）
  ├── 改行位置の調整
  └── 行末のセミコロン
```

---

## 前提条件

- **Part 1** を完了していること（Docker基礎、Node.js/npm基礎）
- Docker Desktopがインストールされていること

---

## Section 1: ESLint（静的コード解析）

### 1.1 ESLintとは？

**ESLint**は、JavaScriptの静的コード解析ツールです。

#### ESLintができること

| 機能 | 説明 | 例 |
|------|------|-----|
| **エラー検出** | バグになりそうなコードを検出 | 未定義変数の使用 |
| **警告表示** | 非推奨の書き方を指摘 | `var`の使用 |
| **スタイル統一** | コーディングルールの強制 | セミコロンの有無 |
| **自動修正** | 一部の問題を自動で修正 | `--fix`オプション |

#### 検出できる問題の例

```javascript
// ❌ 未使用の変数
const unusedVar = 'not used';

// ❌ 未定義の変数を使用
console.log(undefinedVar);

// ❌ 比較演算子の間違い
if (value = 10) { }  // 代入になっている

// ❌ 到達不能コード
function test() {
  return;
  console.log('never executed');
}
```

### 1.2 ハンズオン：ESLint環境構築

#### 学習用ディレクトリの作成

```bash
# ローカルで作業ディレクトリを作成
mkdir eslint-study && cd eslint-study

# Dockerコンテナを起動
docker run -it --rm -v $(pwd):/work -w /work node:20 bash
```

#### プロジェクト初期化とESLintインストール

```bash
# コンテナ内で実行
npm init -y

# ESLintをインストール
npm install --save-dev eslint
```

### 1.3 ESLintの初期設定

```bash
# 対話形式で設定ファイルを作成
npm init @eslint/config
```

**注意**：ESLint v9からは「Flat Config」がデフォルトになり、設定ファイル形式が`eslint.config.mjs`に変わりました。バージョンによって対話形式の選択肢や生成される設定ファイルが異なる場合があります。以下はESLint v9での例です。

#### 対話形式での選択（推奨設定）

```
? How would you like to use ESLint?
  → To check syntax and find problems

? What type of modules does your project use?
  → JavaScript modules (import/export)

? Which framework does your project use?
  → None of these

? Does your project use TypeScript?
  → No

? Where does your code run?
  → Node（スペースキーで選択、Enterで確定）

? What format do you want your config file to be in?
  → JavaScript
```

#### 生成される設定ファイル（eslint.config.mjs）

```javascript
import globals from "globals";
import pluginJs from "@eslint/js";

export default [
  {
    languageOptions: {
      globals: globals.node
    }
  },
  pluginJs.configs.recommended,
];
```

### 1.4 ESLintを試してみる

#### 問題のあるコードを作成

```bash
# 問題のあるコードを作成
cat << 'EOF' > sample.js
// 問題のあるコード例

// 1. 未使用の変数
const unusedVariable = 'I am not used';

// 2. varの使用（letやconstが推奨）
var oldStyle = 'using var';

// 3. セミコロンなし（設定によってはエラー）
const noSemicolon = 'no semicolon'

// 4. console.logの使用（本番では非推奨の場合も）
console.log('Hello, ESLint!');

// 5. 未定義変数の使用
console.log(undefinedVar);

// 6. 関数
function greet(name) {
  return 'Hello, ' + name;
}

// 7. 関数を呼び出し
const result = greet('World');
console.log(result);
EOF
```

#### ESLintを実行

```bash
# ESLintでチェック
npx eslint sample.js
```

#### 期待される出力（エラー・警告）

```
/work/sample.js
   5:7   error  'unusedVariable' is assigned a value but never used  no-unused-vars
   8:1   error  Unexpected var, use let or const instead             no-var
  17:13  error  'undefinedVar' is not defined                        no-undef

✖ 3 problems (3 errors, 0 warnings)
  1 error and 0 warnings potentially fixable with the `--fix` option.
```

### 1.5 自動修正を試す

```bash
# 自動修正可能な問題を修正
npx eslint sample.js --fix

# 修正後のコードを確認
cat sample.js
```

**注意**：すべての問題が自動修正されるわけではありません。

### 1.6 ESLintルールのカスタマイズ

```bash
# 設定ファイルを更新
cat << 'EOF' > eslint.config.mjs
import globals from "globals";
import pluginJs from "@eslint/js";

export default [
  {
    languageOptions: {
      globals: globals.node
    }
  },
  pluginJs.configs.recommended,
  {
    rules: {
      // 未使用変数を警告に変更（エラー→警告）
      "no-unused-vars": "warn",
      
      // console.logを許可
      "no-console": "off",
      
      // varを禁止してlet/constを強制
      "no-var": "error",
      
      // セミコロンを必須に
      "semi": ["error", "always"],
      
      // シングルクォートを強制
      "quotes": ["error", "single"]
    }
  }
];
EOF

# 再度チェック
npx eslint sample.js
```

#### ルールの設定値

| 値 | 意味 |
|-----|------|
| `"off"` または `0` | ルールを無効化 |
| `"warn"` または `1` | 警告として表示 |
| `"error"` または `2` | エラーとして表示 |

### 1.7 package.jsonにスクリプトを追加

```bash
# package.jsonを更新
cat << 'EOF' > package.json
{
  "name": "eslint-study",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "lint": "eslint .",
    "lint:fix": "eslint . --fix"
  },
  "devDependencies": {
    "@eslint/js": "^9.0.0",
    "eslint": "^9.0.0",
    "globals": "^15.0.0"
  }
}
EOF

# スクリプトで実行
npm run lint
```

### 1.8 特定ファイルを除外

```bash
# .eslintignoreファイルを作成（または設定ファイルで指定）
cat << 'EOF' > .eslintignore
node_modules/
dist/
build/
*.min.js
EOF
```

### 1.9 コンテナ終了

```bash
exit
```

### ✅ このセクションで学んだこと

- ESLintはコードの問題点（バグの可能性、非推奨の書き方）を検出する静的解析ツール
- ルールは`"off"`/`"warn"`/`"error"`で制御可能
- `--fix`オプションで自動修正可能な問題を修正できる
- `.eslintignore`で除外ファイルを指定

---

## Section 2: Prettier（コードフォーマッター）

### 2.1 Prettierとは？

**Prettier**は、コードを自動整形するフォーマッターです。

#### ESLintとPrettierの違い

| 観点 | ESLint | Prettier |
|------|--------|----------|
| **主な目的** | コード品質・バグ検出 | コードスタイル統一 |
| **対象** | 主にJavaScript/TypeScript | JS, CSS, HTML, JSON, Markdownなど |
| **設定** | 細かいルール設定が可能 | 設定項目は少ない（意見付きツール） |
| **哲学** | 柔軟性重視 | 議論を減らす（opinionated） |

#### Prettierが整形する内容

```javascript
// 整形前（バラバラなスタイル）
const foo={a:1,b:2,c:3};
function bar( x,y ){return x+y}
const arr = [1,2,3,4,5]

// 整形後（統一されたスタイル）
const foo = { a: 1, b: 2, c: 3 };
function bar(x, y) {
  return x + y;
}
const arr = [1, 2, 3, 4, 5];
```

### 2.2 ハンズオン：Prettier環境構築

#### 学習用ディレクトリの作成

```bash
# ローカルで作業ディレクトリを作成
mkdir prettier-study && cd prettier-study

# Dockerコンテナを起動
docker run -it --rm -v $(pwd):/work -w /work node:20 bash
```

#### プロジェクト初期化とPrettierインストール

```bash
# コンテナ内で実行
npm init -y

# Prettierをインストール（バージョン固定推奨）
npm install --save-dev --save-exact prettier
```

**`--save-exact`の理由**：Prettierのバージョンが変わると整形結果が変わる可能性があるため、チーム内でバージョンを固定します。

### 2.3 Prettierを試してみる

#### 整形前のコードを作成

```bash
# 整形前のコードを作成
cat << 'EOF' > sample.js
// 整形前のコード（わざと汚く書く）
const user={name:"Alice",age:25,email:"alice@example.com"};
function greet(name){console.log("Hello, "+name+"!");}
const numbers=[1,2,3,4,5];
const doubled=numbers.map(n=>n*2);
if(user.age>=18){console.log("Adult")}else{console.log("Minor")}
EOF

# 内容確認
cat sample.js
```

#### Prettierでチェック（整形せずに確認）

```bash
# 整形が必要かチェック
npx prettier --check sample.js
```

#### 期待される出力

```
Checking formatting...
[warn] sample.js
[warn] Code style issues found in the above file. Run Prettier with --write to fix.
```

#### Prettierで整形

```bash
# 整形を実行
npx prettier --write sample.js

# 整形後のコードを確認
cat sample.js
```

#### 期待される出力（整形後）

```javascript
// 整形前のコード（わざと汚く書く）
const user = { name: "Alice", age: 25, email: "alice@example.com" };
function greet(name) {
  console.log("Hello, " + name + "!");
}
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map((n) => n * 2);
if (user.age >= 18) {
  console.log("Adult");
} else {
  console.log("Minor");
}
```

### 2.4 Prettier設定ファイルの作成

```bash
# .prettierrcファイルを作成
cat << 'EOF' > .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 80,
  "bracketSpacing": true,
  "arrowParens": "always"
}
EOF
```

#### 設定項目の説明

| 項目 | 説明 | デフォルト | 設定例 |
|------|------|-----------|--------|
| **semi** | セミコロンを付けるか | `true` | `true` |
| **singleQuote** | シングルクォートを使うか | `false` | `true` |
| **tabWidth** | タブの幅 | `2` | `2` |
| **trailingComma** | 末尾カンマ | `"all"` | `"es5"` |
| **printWidth** | 1行の最大文字数 | `80` | `80` |
| **bracketSpacing** | オブジェクトの括弧内スペース | `true` | `true` |
| **arrowParens** | アロー関数の括弧 | `"always"` | `"always"` |

### 2.5 設定を反映して再整形

```bash
# 設定を反映して再整形
npx prettier --write sample.js

# 結果を確認（シングルクォートに変わる）
cat sample.js
```

#### 期待される出力

```javascript
// 整形前のコード（わざと汚く書く）
const user = { name: 'Alice', age: 25, email: 'alice@example.com' };
function greet(name) {
  console.log('Hello, ' + name + '!');
}
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map((n) => n * 2);
if (user.age >= 18) {
  console.log('Adult');
} else {
  console.log('Minor');
}
```

### 2.6 複数ファイルの整形

```bash
# 複数のファイルを作成
mkdir src

cat << 'EOF' > src/utils.js
const add=(a,b)=>a+b;
const subtract=(a,b)=>a-b;
module.exports={add,subtract};
EOF

cat << 'EOF' > src/index.js
const {add,subtract}=require('./utils');
console.log(add(5,3));
console.log(subtract(10,4));
EOF

# srcディレクトリ内のすべてのJSファイルを整形
npx prettier --write "src/**/*.js"
```

### 2.7 除外ファイルの設定

```bash
# .prettierignoreファイルを作成
cat << 'EOF' > .prettierignore
node_modules/
dist/
build/
*.min.js
package-lock.json
EOF
```

### 2.8 package.jsonにスクリプトを追加

```bash
# package.jsonを更新
cat << 'EOF' > package.json
{
  "name": "prettier-study",
  "version": "1.0.0",
  "scripts": {
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  },
  "devDependencies": {
    "prettier": "3.3.0"
  }
}
EOF

# スクリプトで実行
npm run format:check
npm run format
```

### 2.9 コンテナ終了

```bash
exit
```

### ✅ このセクションで学んだこと

- Prettierはコードの見た目（インデント、引用符、改行など）を自動整形するフォーマッター
- `.prettierrc`で整形ルールを設定（`singleQuote`、`semi`など）
- `--check`でチェックのみ、`--write`で整形を実行
- `--save-exact`でバージョンを固定してチーム内で整形結果を統一

---

## Section 3: ESLintとPrettierの併用

### 3.1 なぜ併用するのか？

| ツール | 役割 |
|--------|------|
| **ESLint** | コードの品質チェック（バグ検出） |
| **Prettier** | コードの見た目を整形 |

**両方使うことで**：品質の高い、見た目も統一されたコードになります。

### 3.2 競合の問題

ESLintとPrettierには**スタイルに関するルールが重複**しています。

```
【競合の例】
ESLint: "セミコロンは必須！"
Prettier: "セミコロンなしで整形しました"
→ 矛盾が発生
```

### 3.3 ハンズオン：ESLint + Prettier

#### 学習用ディレクトリの作成

```bash
# ローカルで作業ディレクトリを作成
mkdir eslint-prettier-study && cd eslint-prettier-study

# Dockerコンテナを起動
docker run -it --rm -v $(pwd):/work -w /work node:20 bash
```

#### 必要なパッケージをインストール

```bash
# コンテナ内で実行
npm init -y

# ESLintとPrettierをインストール
npm install --save-dev eslint prettier

# 競合を解決するパッケージ
npm install --save-dev eslint-config-prettier
```

#### パッケージの説明

| パッケージ | 役割 |
|-----------|------|
| `eslint` | 静的コード解析 |
| `prettier` | コードフォーマッター |
| `eslint-config-prettier` | ESLintのスタイルルールを無効化（Prettierと競合しないように） |

### 3.4 設定ファイルの作成

#### ESLint設定

```bash
# eslint.config.mjsを作成
cat << 'EOF' > eslint.config.mjs
import globals from "globals";
import pluginJs from "@eslint/js";
import eslintConfigPrettier from "eslint-config-prettier";

export default [
  {
    languageOptions: {
      globals: globals.node
    }
  },
  pluginJs.configs.recommended,
  // Prettierと競合するルールを無効化（最後に配置）
  eslintConfigPrettier,
  {
    rules: {
      "no-unused-vars": "warn",
      "no-console": "off"
    }
  }
];
EOF
```

**重要**：`eslintConfigPrettier`は**最後**に配置して、競合するルールを上書きします。

#### Prettier設定

```bash
# .prettierrcを作成
cat << 'EOF' > .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
EOF
```

### 3.5 テストコードの作成と実行

```bash
# 問題のあるコードを作成
cat << 'EOF' > sample.js
// 問題のあるコード
const unusedVar="not used";
const user={name:"Alice",age:25};
function greet(name){console.log("Hello, "+name)}
console.log(undefinedVar);
EOF

# ESLintでチェック（品質の問題を検出）
npx eslint sample.js
```

#### 期待される出力

```
/work/sample.js
  2:7   warning  'unusedVar' is assigned a value but never used  no-unused-vars
  5:13  error    'undefinedVar' is not defined                   no-undef

✖ 2 problems (1 error, 1 warning)
```

```bash
# Prettierで整形（見た目を統一）
npx prettier --write sample.js

# 整形後のコードを確認
cat sample.js
```

#### 整形後のコード

```javascript
// 問題のあるコード
const unusedVar = 'not used';
const user = { name: 'Alice', age: 25 };
function greet(name) {
  console.log('Hello, ' + name);
}
console.log(undefinedVar);
```

### 3.6 package.jsonにスクリプトを追加

```bash
# package.jsonを更新
cat << 'EOF' > package.json
{
  "name": "eslint-prettier-study",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "check": "npm run lint && npm run format:check",
    "fix": "npm run lint:fix && npm run format"
  },
  "devDependencies": {
    "@eslint/js": "^9.0.0",
    "eslint": "^9.0.0",
    "eslint-config-prettier": "^9.0.0",
    "globals": "^15.0.0",
    "prettier": "^3.0.0"
  }
}
EOF
```

#### スクリプトの使い分け

| スクリプト | 用途 |
|-----------|------|
| `npm run lint` | ESLintでチェック |
| `npm run format:check` | Prettierでチェック |
| `npm run check` | 両方でチェック |
| `npm run fix` | 両方で自動修正 |

### 3.7 推奨ワークフロー

```bash
# 1. コードを書く

# 2. 保存時に自動整形（エディタ設定推奨）

# 3. コミット前にチェック
npm run check

# 4. 問題があれば修正
npm run fix
```

### 3.8 コンテナ終了

```bash
exit
```

### ✅ このセクションで学んだこと

- ESLint（品質チェック）とPrettier（整形）は役割が異なるため併用が効果的
- `eslint-config-prettier`でESLintのスタイルルールを無効化し競合を防止
- 設定ファイルで`eslintConfigPrettier`は**最後に配置**する
- `npm run check`でチェック、`npm run fix`で自動修正のワークフローを構築

---

## Section 4: VSCode連携（補足）

### 4.1 推奨拡張機能

| 拡張機能 | 機能 |
|---------|------|
| **ESLint** | ESLintの結果をエディタに表示 |
| **Prettier** | 保存時に自動整形 |

### 4.2 settings.jsonの設定例

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### 4.3 Dev Containers（VSCode + Docker）

VSCodeのDev Containers拡張機能を使えば、Docker環境でもVSCodeの機能をフル活用できます。

---

## まとめ

### 🎯 学んだこと

#### ESLint

| コマンド | 用途 |
|---------|------|
| `npx eslint <file>` | ファイルをチェック |
| `npx eslint . ` | 全ファイルをチェック |
| `npx eslint . --fix` | 自動修正 |

#### Prettier

| コマンド | 用途 |
|---------|------|
| `npx prettier --check <file>` | 整形が必要かチェック |
| `npx prettier --write <file>` | 整形を実行 |
| `npx prettier --write .` | 全ファイルを整形 |

#### 併用時の設定

| ファイル | 役割 |
|---------|------|
| `eslint.config.mjs` | ESLint設定 + `eslint-config-prettier` |
| `.prettierrc` | Prettier設定 |
| `.eslintignore` | ESLint除外ファイル |
| `.prettierignore` | Prettier除外ファイル |

### 📚 次のステップ

- **Part 4**: その他ツール編（yarn、Sass、nvm/nodenv）

### 🗑️ クリーンアップ

```bash
# 学習ディレクトリを削除
rm -rf eslint-study prettier-study eslint-prettier-study
```

---

## 参考資料

- [ESLint公式ドキュメント](https://eslint.org/docs/latest/)
- [Prettier公式ドキュメント](https://prettier.io/docs/en/)
- [eslint-config-prettier](https://github.com/prettier/eslint-config-prettier)