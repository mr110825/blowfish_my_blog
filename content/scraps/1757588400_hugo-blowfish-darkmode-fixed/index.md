+++
id = "1757588400"
date = '2025-09-11T20:00:00+09:00'
draft = false
title = 'Hugo+Blowfish｜ダークモードに固定する設定方法'
tags = ["hugo", "blowfish", "darkmode"]
+++

## はじめに

Hugo静的サイトジェネレーター + Blowfishテーマを使用したサイトにおいて、表示テーマを常にダークモードに固定する方法について整理しました。

この設定により、ユーザーの環境設定に関係なく、サイトを常にダークモードで表示させることができます。

## 設定方法

### 1. params.tomlファイルの設定

`config/_default/params.toml`の以下の項目を変更します。

```toml
# テーマ設定
colorScheme = "blowfish"
defaultAppearance = "dark"          # "light" から "dark" に変更
autoSwitchAppearance = false        # true から false に変更

# フッター設定
[footer]
  showMenu = true
  showCopyright = true
  showThemeAttribution = true
  showAppearanceSwitcher = false    # true から false に変更（オプション）
  showScrollToTop = true
```

## 各設定項目の説明

| 設定項目 | 設定値 | 説明 |
| :--- | :--- | :--- |
| **defaultAppearance** | `"dark"` | サイトのデフォルト表示テーマをダークモードに設定 |
| **autoSwitchAppearance** | `false` | ユーザーの環境設定に応じた自動切り替えを無効化 |
| **showAppearanceSwitcher** | `false` | フッターのテーマ切り替えボタンを非表示（推奨） |

## 設定反映手順

| 手順 | 説明 |
| :--- | :--- |
| **1. ファイル編集** | `config/_default/params.toml`を上記のとおり変更 |
| **2. サーバー再起動** | `hugo server`コマンドでローカルサーバーを再起動 |
| **3. 確認** | サイトが常にダークモードで表示されることを確認 |

### 設定反映コマンド

```bash
# サーバー再起動
hugo server

# 下書き含む場合
hugo server -D
```

## 設定の効果

設定後の動作は以下のようになります：

- ✅ **固定表示**: サイトが常にダークモードで表示される
- ✅ **自動切り替え無効**: ユーザーの環境設定（OS設定等）の影響を受けない
- ✅ **UI整合性**: テーマ切り替えボタンを非表示にして一貫性を保つ
- ✅ **UX向上**: ユーザーが意図しないテーマ変更を防止

## トラブルシューティング

### よくある問題と解決策

| 問題 | 原因 | 解決策 |
| :--- | :--- | :--- |
| **設定が反映されない** | サーバーが再起動されていない | `hugo server`コマンドでサーバーを再起動 |
| **一部要素がライトモード** | カスタムCSSの影響 | カスタムCSSでダークモード用スタイルを確認 |
| **テーマボタンが残っている** | `showAppearanceSwitcher`が`true`のまま | `params.toml`で`false`に設定 |

## 応用設定

### ライトモードに戻したい場合

```toml
defaultAppearance = "light"
autoSwitchAppearance = false
showAppearanceSwitcher = false
```

### 自動切り替えを有効にしたい場合

```toml
defaultAppearance = "dark"          # デフォルトは維持
autoSwitchAppearance = true         # 自動切り替えを有効化
showAppearanceSwitcher = true       # 切り替えボタンも表示
```

### カスタムダークテーマの適用

カスタムCSSでさらに詳細なダークモード設定が可能です：

```css
/* custom.css */
:root[data-theme="dark"] {
  --color-primary: #your-color;
  --color-secondary: #your-color;
  /* その他のカスタム設定 */
}
```

## 参考リンク

- [Blowfishテーマ公式ドキュメント - Appearance](https://blowfish.page/docs/configuration/#appearance)
- [Hugo Configuration Documentation](https://gohugo.io/getting-started/configuration/)
- [Blowfishテーマ - GitHub](https://github.com/nunocoracao/blowfish)