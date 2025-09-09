+++
date = '2025-08-10T20:50:45+09:00'
draft = false
title = '【Windows】Voicemeeterを使ってパソコン内音声を録音する手順'
tags = ["Windows", "Voicemeeter", "音声録音"]
+++
## はじめに

**Voicemeeter**は、Windowsでパソコン内部音声を高品質で録音するための強力なツールです。この記事では、Voicemeeterのインストールから設定、実際の録音までの手順を詳しく解説します。
### 解決する課題
- Windowsの標準機能ではPC内部音声の録音が困難
- オンラインミーティングやシステム音声をクリアに録音したい
- 複雑な音声ルーティングをシンプルに管理したい

### この記事で学べること
- Voicemeeterの基本的な設定方法
- PC内部音声の録音手順
- 仮想オーディオデバイスの活用方法

### 対象読者
- Windows環境でPC内部音声を録音したい方
- オンラインミーティングの録音を行いたい方
- Voicemeeterを初めて使用する方

{{< alert cardColor="#fbd500ff" iconColor="#1d3557" textColor="#000000ff" >}}
オンラインミーティングを録音する場合は必ず参加メンバーの許可を取ってから録音してください。
{{< /alert >}}

Voicemeeterについて公式サイトの説明：
> Voicemeeter は、任意のオーディオデバイスやアプリケーションから、またはそれらへのあらゆる音声ソースをミックス・管理するために、仮想入出力（Virtual I/O）として機能する仮想オーディオデバイスを備えたオーディオミキサーアプリケーションです。

## ハンズオン

### Step 0: 準備

Voicemeeterを使用するための環境を整備します。

**必要な条件:**
- Windows 7以降のOS
- 管理者権限でのインストール
- インストール後の再起動

### Step 1: Voicemeeterの入手とインストール

1. [VB=AUDIO software](https://vb-audio.com/Voicemeeter/)からVoicemeeterをダウンロード
2. 管理者権限でvoicemeetersetupをインストール
3. PCを再起動

### Step 2: Voicemeeterのセットアップ

**1. 出力デバイスの設定**

Windowsの「サウンド」設定で出力デバイスを設定します：

<img src="20250707153716.png">

**2. 入力デバイスの設定**

Windowsの「サウンド」設定で入力デバイスを設定します：

<img src="20250707153737.png">

#### 各設定
- Voicemeeter Out B1	仮想出力 B1（Default VAIO）
	- 一般的な仮想マイク（Google Meet等）
- Voicemeeter Out B2	仮想出力 B2（AUX VAIO）	
	- Zoomなど別ルート用に使う
- Voicemeeter Out B3	仮想出力 B3（VAIO3）
	- さらに追加の音声ルートが欲しい時
- Voicemeeter Out A1〜A5	物理的な出力（スピーカーなど）
	- 録音や再生には使わない

**3. Voicemeeterアプリケーションの設定**

1. Voicemeeterを起動
2. Voicemeeterの「Stereo Input」にて対象のマイクを設定
3. Voicemeeterの「Hardware Output」にて対象のスピーカーを設定

### Step 3: サウンドレコーダーで録音

録音を開始する前に以下を確認してください：

**準備事項:**
- Voicemeeterが起動していること
- Windows音声設定が上記の設定になっていること
- 録音対象の音声が再生されていること

**録音手順:**
1. Windowsのサウンドレコーダーを起動
2. 録音ボタンをクリックして録音開始
3. 録音終了後、ファイルを保存

<img src="20250707154452.png">

## まとめ

Voicemeeterを使用することで、Windowsで簡単にPC内部音声を録音できるようになります。

### 主要ポイント
- **仮想オーディオデバイス**: Voicemeeterが提供する仮想音声ルーティング
- **シンプルな設定**: Windows標準のサウンド設定との連携
- **高音質録音**: クリアなPC内部音声の取得

### 実践的な価値
- **会議録音**: オンラインミーティングの効率的な記録
- **音声アーカイブ**: 重要なシステム音声の保存
- **コンテンツ制作**: 音声素材の高品質な録音

## 参考リンク

- [Youtube：【Windows 11】パソコン内音声を録音する手順](https://www.youtube.com/watch?v=9jRQ6osMsUM&t=349s)
- [VB=AUDIO software](https://vb-audio.com/Voicemeeter/)