+++
id = "1757593500"
title = "Hugo・BlowfishでカスタムCSS適用"
date = '2025-09-11T21:25:00+09:00'
draft = false
tags = ["Hugo", "Blowfish", "CSS"]
+++

## はじめに

Hugo + BlowfishテーマでのカスタムCSS適用は、独自のデザインカスタマイズを可能にする重要な機能です。テーマファイルを直接編集することなく、安全にスタイルをオーバーライドできるため、テーマ更新の際も変更が維持されます。

以下に、Hugo・BlowfishでカスタムCSSを適用する手順と実践的な活用方法を説明します。

## 基本的なファイル構成

カスタムCSS適用に必要なファイル構成：

```
プロジェクトルート/
├── assets/
│   └── css/
│       └── custom.css          # カスタムCSSファイル
├── config/
│   └── _default/
│       └── params.toml         # 設定ファイル
```

**重要**: `assets/css/` ディレクトリに配置することで、Hugoのアセット処理機能が利用できます。

## インストール・セットアップ

### 1. ディレクトリとファイルの作成

```bash
# assetsディレクトリ内にcssフォルダを作成
mkdir -p assets/css

# カスタムCSSファイルを作成
touch assets/css/custom.css
```

### 2. params.tomlでの設定

`config/_default/params.toml` に以下を追加：

```toml
# カスタムスタイル設定
customCSS = ["css/custom.css"]
```

**複数ファイルの場合**:
```toml
customCSS = ["css/custom.css", "css/additional.css"]
```

## 基本的な使い方

### カスタムCSSの記述

`assets/css/custom.css` にスタイルを記述します：

| 目的 | 実装例 | 解説 |
| :--- | :--- | :--- |
| **カラーパレット設定** | `:root { --primary-color: #4f46e5; }` | CSS変数でテーマカラーを統一 |
| **既存要素の調整** | `.card { border-radius: 12px; }` | Blowfishのクラスをオーバーライド |
| **アニメーション追加** | `.card:hover { transform: translateY(-2px); }` | ホバーエフェクトの実装 |

### 実用的なカスタマイズ例

```css
/* カスタムカラーパレット */
:root {
  --primary-gradient-start: #4f46e5;
  --primary-gradient-end: #06b6d4;
  --accent-color: #10b981;
}

/* カード要素の改善 */
.min-h-full.border {
  border: none !important;
  box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.min-h-full.border:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.15);
}
```

### サイトの再生成

```bash
# 開発サーバー再起動
hugo server --port 1313

# または本番ビルド
hugo
```

## 実践的な使い方

### 1. レスポンシブデザイン対応

```css
/* モバイル対応 */
@media (max-width: 768px) {
  .grid.gap-4.sm\:grid-cols-2.md\:grid-cols-3 {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
```

### 2. アニメーション効果

```css
/* ホバーエフェクト */
.thumbnail_card {
  transition: transform 0.3s ease;
}

.min-h-full.border:hover .thumbnail_card {
  transform: scale(1.05);
}
```

### 3. ダークモード対応

```css
/* ダークモード対応 */
@media (prefers-color-scheme: dark) {
  .min-h-full.border {
    background: linear-gradient(145deg, #1f2937 0%, #111827 100%);
  }
}
```

### 問題1: CSSが適用されない

**原因と解決策**：

| 原因 | 確認方法 | 解決策 |
| :--- | :--- | :--- |
| **ファイルパス間違い** | `ls -la assets/css/custom.css` | `assets/css/` ディレクトリに正しく配置 |
| **params.toml記述ミス** | 配列形式で記述されているか | `customCSS = ["css/custom.css"]` |
| **キャッシュ問題** | ブラウザで強制リロード | `rm -rf public && hugo` |

### 問題2: 既存スタイルとの競合

```css
/* 詳細度を上げる */
body .main-content .card-element {
  color: #333 !important;
}
```

### 問題3: レスポンシブが効かない

```css
/* メディアクエリの順序を確認 */
@media (max-width: 768px) {
  /* モバイル用スタイル */
}
@media (min-width: 769px) {
  /* デスクトップ用スタイル */
}
```

## 参考リンク

- [Blowfish公式ドキュメント - カスタマイゼーション](https://blowfish.page/docs/advanced-customisation/)
- [Hugo Assets処理公式ガイド](https://gohugo.io/hugo-pipes/)
- [CSS詳細度の理解](https://developer.mozilla.org/ja/docs/Web/CSS/Specificity)