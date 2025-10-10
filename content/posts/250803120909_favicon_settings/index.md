+++
id = "250803120909"
date = '2025-08-03T12:09:09+09:00'
draft = false
title = 'BlowfishでFaviconを設定する方法'
tags = ["Hugo", "Blowfish"]
+++

## はじめに

**Blowfish**テーマを使用したHugoサイトでは、デフォルトで「フグ」のアイコンがfaviconとして設定されています。この記事では、デフォルトのfaviconから独自のfaviconに変更する手順を詳しく解説します。

<img src="blowfish_favicon.png" alt="Blowfishのデフォルトのfavicon" width="300"/>

### 解決する課題
- デフォルトfaviconからオリジナルアイコンへの変更
- 複数デバイス・プラットフォームでの適切なアイコン表示
- ブランディング一貫性の確保

### この記事で学べること
- Hugoサイトでのfavicon設定の仕組み
- 複数プラットフォーム対応のfavicon一式の作成方法
- 各faviconファイルの用途と必要性

### 対象読者
- Hugo + Blowfishテーマを使用している方
- Webサイトのfavicon設定を行いたい方
- マルチプラットフォーム対応のアイコン設定を学びたい方

## 対象システム

- **Hugo**: v0.80以降
- **テーマ**: Blowfish
- **対応OS**: Windows, macOS, Linux
- **対応ブラウザ**: Chrome, Firefox, Safari, Edge

## favicon設定

### Step 0: 準備

favicon変更に必要なファイルを事前に準備します。以下の形式とサイズのファイルが必要です：

- `favicon.ico` - 従来のブラウザ対応用
- `favicon-16x16.png` - 標準解像度用（16×16px）
- `favicon-32x32.png` - 高解像度用（32×32px）
- `apple-touch-icon.png` - iOS用（180×180px）
- `android-chrome-192x192.png` - Android用（192×192px）
- `android-chrome-512x512.png` - Android用（512×512px）
- `site.webmanifest` - Webマニフェストファイル

### Step 1: ファビコンファイルの配置

準備したfaviconファイルをプロジェクトの `static` ディレクトリに配置します：

```bash
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

{{< alert icon="lightbulb" cardColor="#d9ff00be" iconColor="#1d3557" textColor="#000000ff" >}}
`static`ディレクトリに置かれたファイルは、Hugoビルド時に自動的にサイトルートにコピーされます。設定ファイルでのパス指定は不要です。
{{< /alert >}}

### Step 2: 設定の確認

ファイル配置後、サイトでfaviconが正しく反映されているかを確認します：

```bash
hugo server -D
```

ブラウザで `http://localhost:1313` にアクセスし、以下を確認：
- ブラウザタブにfaviconが表示されている
- ブックマーク時に正しいアイコンが使用される
- モバイルデバイスでのホーム画面追加時の表示

本番環境への反映：

```bash
hugo
```

## 各ファイルの詳細説明

### ブラウザ用favicon

- **`favicon.ico`**
  - 最も伝統的なfavicon形式
  - PCブラウザのタブやブックマークで使用
  - 古いブラウザとの互換性確保のため必須

- **`favicon-16x16.png`**
  - 標準解像度ディスプレイのブラウザタブ用
  - PNG形式で軽量

- **`favicon-32x32.png`**
  - 高解像度ディスプレイ（Retina等）用
  - タスクバーやブックマークでも使用

### モバイル用アイコン

- **`apple-touch-icon.png`**
  - iOSデバイスの「ホーム画面に追加」時に使用
  - 推奨サイズ：180×180px

- **`android-chrome-192x192.png`**
  - Androidのホーム画面アイコン用
  - サイズ：192×192px

- **`android-chrome-512x512.png`**
  - Android用大サイズアイコン
  - スプラッシュスクリーンで使用される場合がある
  - サイズ：512×512px

### Webマニフェスト

- **`site.webmanifest`**
  - PWA（Progressive Web App）用設定ファイル
  - サイト名、テーマカラー、アイコンパスを定義
  - ブラウザが適切なアイコンを選択するための情報を提供

## favicon作成に便利なツール

### オンラインツール

- **[favicon.io](https://favicon.io/)**
  - 1つの画像から主要プラットフォーム向けfavicon一式を自動生成
  - 多様な入力形式に対応（画像、テキスト、絵文字）

- **[ICOON MONO](https://icooon-mono.com/)**
  - 豊富なアイコン素材を無料でダウンロード可能
  - SVGおよびPNG形式で提供

### 推奨ワークフロー

1. 元となる高解像度画像（512×512px以上）を用意
2. favicon.ioで各サイズのファイルを一括生成
3. 生成されたファイルを `static` ディレクトリに配置
4. サイトを再起動して動作確認

## トラブルシューティング

### よくある問題と解決法

**問題1: ブラウザでfaviconが更新されない**
- **原因**: ブラウザキャッシュが残っている
- **解決法**: ハードリロード（Ctrl+Shift+R または Cmd+Shift+R）を実行

**問題2: 一部のサイズのfaviconが表示されない**
- **原因**: ファイル名が正しくない、またはサイズが仕様と異なる
- **解決法**: ファイル名とサイズを再確認し、必要に応じて再生成

**問題3: モバイルでアイコンが正しく表示されない**
- **原因**: `site.webmanifest` の設定が不適切
- **解決法**: マニフェストファイルのパスとサイズ指定を確認

{{< alert icon="lightbulb" cardColor="#d9ff00be" iconColor="#1d3557" textColor="#000000ff" >}}
favicon変更後は必ずシークレットモード（プライベートブラウジング）でも確認することをお勧めします。キャッシュの影響を受けずに正確な表示を確認できます。
{{< /alert >}}

## コマンドリファレンス

```bash
# Hugo開発サーバーの起動
hugo server -D

# 本番ビルド
hugo

# ビルド成果物のクリーンアップ
hugo --cleanDestinationDir

# 特定ポートでの起動
hugo server -D -p 8080

# ブラウザキャッシュクリア（開発者ツールで実行）
# Chrome/Firefox: Ctrl+Shift+R (Windows/Linux) または Cmd+Shift+R (macOS)
# Safari: Cmd+Option+R
```

## まとめ

Blowfishテーマでのfavicon設定は、`static` ディレクトリへのファイル配置だけで簡単に実現できます。複数のプラットフォームに対応するため、適切なサイズとフォーマットのファイルを用意することが重要です。

### 主要ポイント
- 7種類のfaviconファイルで全プラットフォームをカバー
- `static` ディレクトリへの配置で自動的に適用
- ブラウザキャッシュに注意した確認作業

## 参考リンク

- [Blowfish公式ドキュメント - ファビコン](https://blowfish.page/ja/docs/partials/#%E3%83%95%E3%82%A1%E3%83%93%E3%82%B3%E3%83%B3)
- [favicon.io](https://favicon.io/)
- [ICOON MONO](https://icooon-mono.com/)