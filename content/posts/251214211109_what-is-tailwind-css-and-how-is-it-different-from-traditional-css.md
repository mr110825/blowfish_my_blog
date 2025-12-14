+++
id = "251214211109"
date = '2025-12-14T21:11:09+09:00'
draft = false
title = 'Tailwind CSS とは何か？従来のCSSと何が違うのか？'
tags = ["ツール", "Tailwind CSS", "CSS", "入門"]
+++

## 今日学んだこと

Tailwind CSSはユーティリティファーストのCSSフレームワークです。従来のCSSとは異なり、小さなユーティリティクラスをHTMLに直接記述することで、スタイルの定義と適用箇所を同じ場所に置く（コロケーション）アプローチを取ります。

## 学習内容

### Tailwind CSSとは

Tailwind CSSは、`bg-blue-500` や `text-white` などの小さなユーティリティクラスを組み合わせてスタイリングを行うCSSフレームワークです。

### 従来のCSSとの違い

従来のCSSでは、HTMLとCSSを別ファイルに分離して管理していました。

```css
/* 従来のCSS */
.primary-button {
  background-color: blue;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
}
```

```html
<button class="primary-button">ボタン</button>
```

しかし、実際の開発ではHTMLとCSSを常にセットで変更することが多く、ファイル間の追跡が困難という課題がありました。

Tailwind CSSでは、ユーティリティクラスをHTMLに直接記述します。

```html
<!-- Tailwind CSS -->
<button class="bg-blue-500 text-white px-4 py-2 rounded">ボタン</button>
```

スタイルの定義と適用箇所が同じ場所にあるため、直感的に理解しやすくなります。

### ユーティリティファーストとは

Tailwind CSSの根底にある考え方が「ユーティリティファースト」です。

ユーティリティクラスとは「1つのCSSプロパティだけを持つ小さなクラス」のことです。このユーティリティクラスを最優先に使用することで、CSSの肥大化を防ぐことができます。

共通スタイルの一括管理が必要な場合は、コンポーネント化や`@apply`ディレクティブで対応可能です。

## まとめ

- Tailwind CSSはユーティリティファーストのCSSフレームワーク
- 小さなユーティリティクラスをHTMLに直接記述する
- スタイルの定義と適用箇所が同じ場所にある（コロケーション）ため、直感的に理解しやすい
- 共通スタイルはコンポーネント化や`@apply`で管理可能

## 参考

- [Tailwind CSS公式ドキュメント](https://tailwindcss.com/docs)
