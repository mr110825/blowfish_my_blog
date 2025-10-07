# Hugo記事作成時のディレクトリ名ID反映ワークフロー改善

**作成日**: 2025-10-07
**作業目的**: `hugo new`コマンドでディレクトリ名にIDが反映されない問題への対応と運用改善

---

## 背景

### 発見された問題

README.mdに記載されていた以下のコマンドでは、記事のフロントマターには`id`が自動付与されるが、**ディレクトリ名にはIDが反映されない**：

```bash
hugo new scraps/<メモのタイトル>/index.md
```

**結果:**
- ディレクトリ名: `content/scraps/<メモのタイトル>/`
- フロントマター: `id = "1759800890"` ← archetypes設定により自動付与

### なぜディレクトリ名にIDが必要か

1. **ファイルシステムレベルでの一意性**: 同名タイトルの記事を区別可能
2. **Git履歴の追跡**: IDベースで記事の変更履歴を追跡
3. **将来的な拡張性**: API開発やデータベース連携時にIDで参照

---

## 検討した解決方法

### 方法1: コマンド実行時にタイムスタンプを含める（非推奨）

```bash
hugo new scraps/$(date +%s)_<メモのタイトル>/index.md
```

**問題点:**
- `$(date +%s)`（bash実行時）と`{{ now.Unix }}`（Hugo実行時）の実行タイミングが異なる
- 1-2秒のずれが発生する可能性がある

**例:**
```bash
hugo new scraps/1759800000_test/index.md
```

結果:
- ディレクトリ名: `1759800000_test`
- ファイル内のID: `id = "1759800001"` ← **ずれる**

### 方法2: 作成後に手動リネーム（手間がかかる）

```bash
hugo new scraps/<メモのタイトル>/index.md
# 生成されたIDを確認してリネーム
git mv content/scraps/<メモのタイトル> content/scraps/$(grep '^id' content/scraps/<メモのタイトル>/index.md | cut -d'"' -f2)_<メモのタイトル>
```

**問題点:**
- 毎回手動でコマンドを実行する必要がある
- 複数記事を作成した場合、手間が増える

### 方法3: 一括リネームスクリプトによる後処理（採用）

**ワークフロー:**
1. 通常通り`hugo new`で記事を作成（ディレクトリ名にIDなし）
2. 記事を複数作成後、スクリプトで一括リネーム
3. Git履歴を保持したまま整理

**メリット:**
- 記事作成時の手間が最小限
- 複数記事をまとめて処理可能
- フロントマターのIDと確実に一致

---

## 実装内容

### 1. 一括リネームスクリプトの作成

**ファイル名:** `rename_dirs_with_id.py`

**配置場所:** プロジェクトルート（`/home/ptin110825/my_project/blowfish_my_blog/`）

**機能:**
- `content/posts`と`content/scraps`内の全ディレクトリを検索
- 各ディレクトリの`index.md`からIDを取得
- ディレクトリ名が既に`数字_`で始まっている場合はスキップ
- `git mv`でリネーム（Git履歴を保持）
- 処理結果をサマリー表示

**スクリプトの動作フロー:**

```
1. content/posts, content/scrapsを走査
   ↓
2. 各ディレクトリのindex.mdを読み込み
   ↓
3. 正規表現でid = "..."を抽出
   ↓
4. ディレクトリ名が^\d+_にマッチするかチェック
   ↓
5. マッチしない場合、{ID}_ディレクトリ名にリネーム
   ↓
6. git mvで実行（履歴保持）
```

**主要な正規表現パターン:**

```python
# フロントマターからIDを抽出
r'^id = "([^"]+)"'

# 既にID付きディレクトリ名かチェック
r'^\d+_'
```

### 2. README.mdの更新

**追加内容:**
- `hugo new`コマンドではディレクトリ名にIDが反映されないことを明記
- 一括リネームスクリプトの使い方を追加
- スクリプトの動作説明を箇条書きで記載
- 実装メモへのリンクを追加

**更新箇所:** README.md:37-54

---

## 使い方

### 新規記事作成の推奨ワークフロー

```bash
# 1. 通常通り記事を作成（複数作成可能）
hugo new scraps/JIS_Q_21500_2018/index.md
hugo new scraps/earned_value_management/index.md
hugo new posts/new-feature-guide/index.md

# 2. 記事の内容を編集

# 3. 一括リネームスクリプトを実行
python3 rename_dirs_with_id.py

# 4. 結果確認
# リネーム完了: JIS_Q_21500_2018 → 1759799499_JIS_Q_21500_2018
# リネーム完了: earned_value_management → 1759800890_earned_value_management
# リネーム完了: new-feature-guide → 1759801234_new-feature-guide
# ==================================================
# リネーム完了: 3件
# スキップ: 21件
# エラー: 0件

# 5. 変更をコミット
git add .
git commit -m "新規記事追加とディレクトリ名へのID反映"
```

### スクリプト実行結果の例

```
リネーム完了: JIS_Q_21500_2018 → 1759799499_JIS_Q_21500_2018
リネーム完了: earned_value_management → 1759800890_earned_value_management
スキップ（既にID付き）: content/scraps/1759704789_ap2025_manage_study_memo
スキップ（既にID付き）: content/posts/1754190549_favicon_settings
...

==================================================
リネーム完了: 2件
スキップ: 22件
エラー: 0件

注意: git mvでリネームしました。変更を確認後、コミットしてください。
```

---

## 技術的詳細

### archetypesの設定（参考）

**ファイル:** `archetypes/scraps.md`

```toml
+++
id = "{{ now.Unix }}"
date = '{{ .Date }}'
draft = false
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
tags = []
+++
```

- `{{ now.Unix }}`: Hugo実行時の現在時刻をUnixタイムスタンプで取得
- これにより、フロントマターには確実にIDが記録される

### Git履歴を保持するリネーム

通常の`mv`コマンドではなく`git mv`を使用する理由：

```python
subprocess.run(
    ['git', 'mv', str(dir_path), str(new_path)],
    capture_output=True,
    text=True,
    check=True
)
```

**メリット:**
- ディレクトリのリネーム履歴がGitに記録される
- ファイル変更履歴が途切れない
- `git log --follow`で追跡可能

---

## トラブルシューティング

### エラー: permission denied

**原因:** スクリプトに実行権限がない

**解決方法:**
```bash
chmod +x rename_dirs_with_id.py
```

### エラー: git mv failed

**原因:** 同名のディレクトリが既に存在する

**解決方法:**
手動で既存ディレクトリ名を確認し、重複を解消してから再実行

### ディレクトリ名がリネームされない

**原因1:** `index.md`にIDが設定されていない

**確認方法:**
```bash
grep "^id" content/scraps/<ディレクトリ名>/index.md
```

**解決方法:**
フロントマターに手動でIDを追加（`id = "1759800000"`）

**原因2:** 既に`数字_`で始まっている

**確認方法:**
```bash
ls content/scraps/ | grep "^\d"
```

スクリプトは既にID付きのディレクトリをスキップします。

---

## 今後の改善案

### オプション1: Hugoプラグイン化

Hugoのフック機能を使って、`hugo new`実行時に自動的にディレクトリをリネームする仕組みを検討

### オプション2: Git Hooksの活用

`.git/hooks/post-commit`にスクリプトを組み込み、コミット時に自動実行

### オプション3: VSCode拡張機能

記事作成時にワンクリックでリネームできる拡張機能の作成

---

## まとめ

### 実現したこと

1. ✅ `hugo new`コマンドではディレクトリ名にIDが反映されない問題を明確化
2. ✅ 一括リネームスクリプト`rename_dirs_with_id.py`の作成
3. ✅ README.mdへの運用方法の追記
4. ✅ Git履歴を保持したリネーム処理の実装

### 運用ワークフロー

```
記事作成 → 内容編集 → python3 rename_dirs_with_id.py → コミット
```

このワークフローにより、記事作成時の手間を最小限にしつつ、ディレクトリ名とフロントマターのIDを確実に一致させることができます。

---

## 関連ファイル

- **スクリプト:** `/home/ptin110825/my_project/blowfish_my_blog/rename_dirs_with_id.py`
- **README:** `/home/ptin110825/my_project/blowfish_my_blog/README.md`
- **Archetypes:** `/home/ptin110825/my_project/blowfish_my_blog/archetypes/scraps.md`
- **実装メモ:** `/home/ptin110825/my_project/blowfish_my_blog/claude_memo/20251007_hugo_id_system_implementation.md`

---

**最終更新**: 2025-10-07
**作業者**: Claude Code
