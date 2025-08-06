+++
date = '2025-08-03T12:09:09+09:00'
draft = false
title = 'BlowfishでFaviconを設定する方法'
tags = ["Hugo", "Blowfish"]
+++
## はじめに

Blowfishではデフォルトで「フグ」のアイコンがfaviconとして設定されています。
<img src="blowfish_favicon.png" alt="Blowfishのデフォルトのfavicon" width="300"/>
デフォルトから自分好みのfaviconへ変更する手順を下記にまとめます。

---

## 設定方法

faviconの変更は、プロジェクトの `static` ディレクトリに独自の画像ファイルを配置するだけで完了します。

```
.
└── static/
    ├─ android-chrome-192x192.png
    ├─ android-chrome-512x512.png
    ├─ apple-touch-icon.png
    ├─ favicon-16x16.png
    ├─ favicon-32x32.png
    ├─ favicon.ico
    └─ site.webmanifest
```
これらのファイルと同じ名前で作成したご自身の画像を、プロジェクトのルートにある `static` フォルダに配置してください。
ファイルを配置した後、Hugoサーバーを再起動（またはビルド）すると、新しいfaviconがサイトに反d映されます。
`hugo.toml`などの設定ファイルでパスを記述する必要はありません。`static`ディレクトリに置かれたファイルが優先的に読み込まれる仕組みです。

## 各ファイルの説明

`static`ディレクトリに配置する各ファイルは、様々なデバイスや状況でサイトのアイコンを表示するために利用されます。

- **`favicon.ico`**:
  - **用途:** 最も伝統的なfavicon形式。主にPCブラウザのタブやブックマークで使われます。古いブラウザとの互換性のために重要です。

- **`favicon-16x16.png` / `favicon-32x32.png`**:
  - **用途:** 最新のPCブラウザが使用するPNG形式のfavicon。
  - **16x16px:** 標準的な解像度のディスプレイのブラウザタブに表示されます。
  - **32x32px:** Retinaディスプレイのような高解像度の画面や、タスクバーなどで使用されます。

- **`apple-touch-icon.png`**:
  - **用途:** iPhoneやiPadなど、Apple製品で「ホーム画面に追加」した際に表示されるアプリアイコンです。`180x180px`が推奨サイズです。

- **`android-chrome-192x192.png` / `android-chrome-512x512.png`**:
  - **用途:** AndroidデバイスのChromeブラウザで「ホーム画面に追加」した際に使われます。
  - **192x192px:** ホーム画面のアイコンとして表示されます。
  - **512x512px:** サイト起動時のスプラッシュスクリーンに表示されることがあります。

- **`site.webmanifest`**:
  - **用途:** ウェブアプリマニフェストと呼ばれる設定ファイルです。サイト名やテーマカラー、そして上記のような各アイコンへのパスを定義し、ブラウザにどのアイコンを使うべきかを伝えます。

これらのファイルを揃えることで、あらゆる環境でサイトのアイコンが意図通りに表示されるようになります。

## favicon作成に便利なサイト

**[favicon.io](https://favicon.io/)**<br>
1つの画像から、主要なプラットフォーム向けのfavicon一式を生成してくれます。

**[ICOON MONO](https://icooon-mono.com/)**<br>
各種アイコン素材をダウンロードできます。

---

## 参考リンク
[Blowfish_favicon](https://blowfish.page/ja/docs/partials/#%E3%83%95%E3%82%A1%E3%83%93%E3%82%B3%E3%83%B3)