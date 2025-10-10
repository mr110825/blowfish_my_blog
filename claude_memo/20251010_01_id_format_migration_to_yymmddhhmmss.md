# Hugo記事ID形式移行メモ：YYMMDDhhmmss方式への統一

**作成日**: 2025-10-10
**作業目的**: 既存全記事のID形式をUnixタイムスタンプからYYMMDDhhmmss形式に移行

---

## 概要

このメモは、Hugoで構築した技術ブログの全記事（35件）について、記事IDの形式をUnixタイムスタンプ（10桁）からYYMMDDhhmmss形式（12桁）に変更した作業記録です。

### 背景・目的

**現行ID形式の課題**:
- Unixタイムスタンプ（例: `1755557154`）は機械的で可読性が低い
- ファイル名から日時を直感的に理解できない

**新形式のメリット**:
1. **可読性向上**: IDから日時が直感的にわかる（例: `250819074554` = 2025年8月19日 07:45:54）
2. **ファイルシステムレベルでの管理性向上**: ディレクトリ名だけで作成日時を把握可能
3. **時系列ソート**: 引き続き文字列ソートで時系列順に並ぶ

---

## 移行対象

### 記事数
- **Posts（記事）**: 5件
- **Scraps（スクラップ）**: 30件
- **合計**: 35件

### 変更箇所
1. フロントマター内の`id`フィールド
2. ディレクトリ名（`{ID}_ディレクトリ名`形式）
3. 内部リンク（`{{< ref "ID_ディレクトリ名" >}}`）
4. Archetypesテンプレート（新規記事用）

---

## ID形式の比較

### 変換例

| 旧ID形式 (Unix) | 日時 | 新ID形式 (YYMMDDhhmmss) |
|---|---|---|
| 1755557154 | 2025-08-19 07:45:54 | 250819074554 |
| 1759322139 | 2025-10-01 21:35:39 | 251001213539 |
| 1760054150 | 2025-10-10 08:55:50 | 251010085550 |

### ディレクトリ名の変更例

```
Before: 1755557154_memo-take-notes
After:  250819074554_memo-take-notes

Before: 1759322139_ap2025_tech_study_memo_multimedia
After:  251001213539_ap2025_tech_study_memo_multimedia

Before: 1760054150_ap2025_tech_study_memo_fundamental
After:  251010085550_ap2025_tech_study_memo_fundamental
```

---

## 移行手順

### Step 1: 既存記事ID変換スクリプトの作成・実行

#### スクリプト: `convert_ids_to_yymmddhhmmss.py`

**機能**:
- `content/posts`と`content/scraps`内の全`index.md`を検索
- フロントマター内の`id = "Unixタイムスタンプ"`を検索
- Pythonの`datetime.fromtimestamp()`でYYMMDDhhmmss形式に変換
- フロントマター内のIDを置換
- 変換マッピングを`id_mapping.json`に保存（後続処理で使用）

**主要なコード**:

```python
def convert_timestamp_to_yymmddhhmmss(unix_timestamp):
    """UnixタイムスタンプをYYMMDDhhmmss形式に変換"""
    dt = datetime.fromtimestamp(int(unix_timestamp))
    return dt.strftime('%y%m%d%H%M%S')
```

**実行結果**:
```
変換完了: 35件
スキップ: 0件
エラー: 0件
```

---

### Step 2: ディレクトリリネームスクリプトの作成・実行

#### スクリプト: `rename_dirs_to_new_id.py`

**機能**:
- 各ディレクトリの`index.md`から新しいID（YYMMDDhhmmss形式）を取得
- 旧ID形式（10桁数字）のプレフィックスを除去
- 新ID形式でディレクトリ名を再構築
- `git mv`でリネーム（Git履歴を保持）

**主要なコード**:

```python
# 旧ID形式（10桁数字）で始まっている場合、それを除去
base_name = re.sub(r'^\d{10}_', '', current_name)

# 新しいID形式でディレクトリ名を構築
new_name = f"{new_id}_{base_name}"

# git mvでリネーム（履歴を保持）
subprocess.run(['git', 'mv', str(dir_path), str(new_path)])
```

**実行結果**:
```
リネーム完了: 28件（git mv成功）
追加処理: 7件（未追跡ディレクトリを手動リネーム後git add）
合計: 35件
```

**注意点**:
- 一部のディレクトリは未追跡状態（untracked）のため、`git mv`が失敗
- 手動で`mv`コマンドでリネーム後、`git add`で追加

---

### Step 3: 内部リンク一括置換

#### スクリプト: `update_internal_links.py`

**機能**:
- `id_mapping.json`から旧ID→新ID変換マッピングを読み込み
- `content/scraps/_index.md`など、内部リンクを含むファイルを検索
- `{{< ref "旧ID_ディレクトリ名" >}}`パターンを新ID形式に置換

**主要なコード**:

```python
# {{< ref "旧ID_ディレクトリ名" >}} パターンを検索して置換
pattern = r'(\{\{<\s*ref\s+")(' + old_id + r'_[^"]+)("\s*>\}\})'

def replace_func(match):
    old_ref = match.group(2)
    new_ref = old_ref.replace(old_id, new_id, 1)
    return match.group(1) + new_ref + match.group(3)

content = re.sub(pattern, replace_func, content)
```

**実行結果**:
```
更新したファイル: 1件（content/scraps/_index.md）
更新したリンク: 30箇所
```

**更新例**:

```markdown
<!-- Before -->
- [Python概要とインストールなど]({{< ref "1756853577_styudy-python" >}})

<!-- After -->
- [Python概要とインストールなど]({{< ref "250903075257_styudy-python" >}})
```

---

### Step 4: Archetypesテンプレートの修正

新規記事作成時に自動的にYYMMDDhhmmss形式のIDを付与するため、archetypesを更新しました。

#### 修正ファイル

1. `archetypes/default.md`
2. `archetypes/posts.md`
3. `archetypes/scraps.md`

#### 変更内容

**変更前**:
```toml
+++
id = "{{ now.Unix }}"
date = '{{ .Date }}'
draft = false
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
tags = []
+++
```

**変更後**:
```toml
+++
id = "{{ now.Format "060102150405" }}"
date = '{{ .Date }}'
draft = false
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
tags = []
+++
```

#### Hugoテンプレート関数

- `{{ now.Unix }}`: Unixタイムスタンプ（秒単位の整数）
- `{{ now.Format "060102150405" }}`: YYMMDDhhmmss形式の文字列
  - `06` = YY（年の下2桁）
  - `01` = MM（月）
  - `02` = DD（日）
  - `15` = hh（時）
  - `04` = mm（分）
  - `05` = ss（秒）

**参考**: Goの時刻フォーマットは参照時刻 `Mon Jan 2 15:04:05 MST 2006` を使用

---

### Step 5: Hugoビルドテスト

```bash
hugo --quiet && echo "✅ Hugoビルド成功"
```

**結果**: ✅ ビルド成功（エラーなし）

---

### Step 6: Git コミット

```bash
git add content/ archetypes/
git add -u public/
git commit -m "記事ID形式をYYMMDDhhmmss方式に統一"
```

**コミット結果**:
- コミットID: `ef51f5d`
- 変更ファイル: 132件
- 変更内容:
  - 35記事のディレクトリリネーム（git mv）
  - 35記事のフロントマターID更新
  - Archetypes 3ファイル更新
  - 内部リンク30箇所更新
  - Public配下の生成ファイル更新

---

## 実行結果サマリー

### 処理統計

| 処理項目 | 件数 | 備考 |
|---|---|---|
| ID変換 | 35件 | 全記事のフロントマター更新 |
| ディレクトリリネーム | 35件 | git mvまたは手動mv + git add |
| 内部リンク更新 | 30箇所 | content/scraps/_index.md |
| Archetypes更新 | 3ファイル | default/posts/scraps |
| Hugoビルド | ✅ 成功 | エラーなし |
| Git コミット | 132ファイル | ef51f5d |

### 変換マッピング（一部抜粋）

```json
{
  "1754153716": "250803015516",
  "1754190549": "250803120909",
  "1755557154": "250819074554",
  "1756683405": "250901083645",
  "1759322139": "251001213539",
  "1760054150": "251010085550"
}
```

完全なマッピングは `claude_memo/migration_scripts/id_mapping.json` に保存されています。

---

## 技術的詳細

### 1. Pythonでのタイムスタンプ変換

```python
from datetime import datetime

# Unixタイムスタンプ → datetime
dt = datetime.fromtimestamp(1755557154)
# datetime(2025, 8, 19, 7, 45, 54)

# datetime → YYMMDDhhmmss形式
new_id = dt.strftime('%y%m%d%H%M%S')
# '250819074554'
```

### 2. 正規表現パターン

#### フロントマター内ID検索
```python
r'^id = "(\d+)"'
# 行頭の id = "数字列" にマッチ
```

#### 旧ID形式のディレクトリ名検出
```python
r'^\d{10}_'
# 10桁の数字で始まる（旧ID形式）
```

#### 新ID形式のディレクトリ名検出
```python
r'^\d{12}_'
# 12桁の数字で始まる（新ID形式）
```

#### 内部リンクのref検索
```python
r'(\{\{<\s*ref\s+")(' + old_id + r'_[^"]+)("\s*>\}\})'
# {{< ref "ID_ディレクトリ名" >}} パターンにマッチ
```

### 3. Git履歴保持のためのリネーム

通常の`mv`ではなく`git mv`を使用する理由:

```python
subprocess.run(['git', 'mv', str(dir_path), str(new_path)])
```

**メリット**:
- ディレクトリのリネーム履歴がGitに記録される
- ファイル変更履歴が途切れない
- `git log --follow`で追跡可能

---

## トラブルシューティング

### 問題1: git mvが失敗（未追跡ディレクトリ）

**エラー例**:
```
fatal: source directory is empty, source=content/scraps/1760054150_...
```

**原因**:
- ディレクトリがGitの追跡対象外（untracked）
- git statusで削除済みと認識されているが、実際にはファイルが存在

**解決方法**:
```bash
# 手動でmvコマンドでリネーム
mv content/scraps/旧ディレクトリ名 content/scraps/新ディレクトリ名

# git addで追加
git add content/scraps/新ディレクトリ名
```

### 問題2: Pythonスクリプトの構文エラー

**エラー例**:
```python
SyntaxError: f-string: single '}' is not allowed
```

**原因**:
f-stringで`{`や`}`を使う場合、エスケープが必要

**解決方法**:
```python
# NG
pattern = rf'(\{{{{<\s*ref\s+")({old_id}_[^"]+)("\s*>}}})'

# OK
pattern = r'(\{\{<\s*ref\s+")(' + old_id + r'_[^"]+)("\s*>\}\})'
```

---

## 新しいID形式での運用

### 新規記事作成

archetypesの更新により、`hugo new`コマンドで自動的にYYMMDDhhmmss形式のIDが付与されます。

```bash
# 記事作成
hugo new posts/new-article/index.md

# 生成されるフロントマター
+++
id = "251010092500"  # 実行時刻に基づく
date = '2025-10-10T09:25:00+09:00'
draft = false
title = 'New Article'
tags = []
+++
```

### ディレクトリ名の命名規則

**推奨方法1**: archetypesで生成されたIDを確認してから手動リネーム

```bash
# 1. 仮のディレクトリ名で作成
hugo new posts/temporary-name/index.md

# 2. 生成されたIDを確認
cat content/posts/temporary-name/index.md | grep "^id"
# id = "251010092500"

# 3. ディレクトリをリネーム
git mv content/posts/temporary-name content/posts/251010092500_actual-article-name
```

**推奨方法2**: 既存のリネームスクリプトを使用

```bash
# 1. 通常通り記事を複数作成
hugo new scraps/article1/index.md
hugo new scraps/article2/index.md

# 2. スクリプトで一括リネーム
python3 claude_memo/migration_scripts/rename_dirs_to_new_id.py

# 3. 変更をコミット
git add .
git commit -m "新規記事追加"
```

---

## メリット・デメリット

### メリット

1. **視認性**: IDから日時が一目でわかる
   ```
   251010085550 → 2025年10月10日 08:55:50
   ```

2. **ファイルシステムでの管理性**: エクスプローラーやlsコマンドでもソート順が直感的

3. **時系列ソート**: 文字列ソートで自動的に時系列順

4. **デバッグ効率化**: ログやエラーメッセージにIDが含まれる場合、いつの記事か即座に判断可能

### デメリット・制約事項

1. **2100年問題**: YY形式（2桁年号）では2000年代と2100年代の区別が困難
   - `250101` → 2025年または2125年？
   - ただし、2100年まで75年の猶予

2. **タイムゾーン情報の欠如**: どのタイムゾーンの時刻か不明
   - 現状はJST（日本標準時）前提

3. **ID長の増加**: 10桁 → 12桁に増加
   - ファイル名が若干長くなる

4. **既存システムとの非互換性**:
   - 今回の移行により、旧ID形式を前提としたツールがある場合は修正が必要
   - ただし、本プロジェクトでは該当なし

---

## 代替案として検討した形式

### YYYYMMDD-hhmmss 形式

```
例: 20251010-085550
```

**メリット**:
- 2100年問題の解消（4桁年号）
- より明確な日時表現

**デメリット**:
- ID長が14桁（+ハイフン）に増加
- 今回は採用見送り

---

## 学習ポイント

### 1. Hugoテンプレート関数

```go
{{ now.Unix }}           // Unixタイムスタンプ（整数）
{{ now.Format "..." }}   // カスタムフォーマット（文字列）
{{ .Date }}              // 記事の作成日時
```

### 2. Goの時刻フォーマット

Goでは参照時刻 `Mon Jan 2 15:04:05 MST 2006` を使用:
- `06` → YY（年の下2桁）
- `2006` → YYYY（4桁年号）
- `01` → MM（月）
- `02` → DD（日）
- `15` → hh（24時間表記の時）
- `04` → mm（分）
- `05` → ss（秒）

### 3. Python datetime

```python
# タイムスタンプ → datetime
dt = datetime.fromtimestamp(1760054150)

# datetime → フォーマット済み文字列
formatted = dt.strftime('%y%m%d%H%M%S')
```

### 4. Gitでのリネーム履歴保持

```bash
# 履歴保持
git mv old_name new_name

# 履歴が途切れる
mv old_name new_name
git add new_name
```

---

## 関連ファイル

### 移行スクリプト

- `claude_memo/migration_scripts/convert_ids_to_yymmddhhmmss.py` - ID変換スクリプト
- `claude_memo/migration_scripts/rename_dirs_to_new_id.py` - ディレクトリリネームスクリプト
- `claude_memo/migration_scripts/update_internal_links.py` - 内部リンク更新スクリプト
- `claude_memo/migration_scripts/id_mapping.json` - 変換マッピングデータ

### Archetypes

- `archetypes/default.md`
- `archetypes/posts.md`
- `archetypes/scraps.md`

### 参考メモ

- `claude_memo/20251007_01_hugo_id_system_implementation.md` - 初期ID実装メモ
- `claude_memo/20251007_02_hugo_directory_id_rename_workflow.md` - ディレクトリID反映ワークフロー

---

## まとめ

今回の移行作業により、以下が実現しました：

1. ✅ 全35記事のID形式をYYMMDDhhmmssに統一
2. ✅ ディレクトリ名へのID反映完了
3. ✅ 内部リンクの整合性確保
4. ✅ 新規記事作成時の自動ID付与（新形式）
5. ✅ Git履歴の保持
6. ✅ Hugoビルドの正常動作確認

この変更により、記事管理の可読性と効率性が大幅に向上しました。今後作成する記事も自動的に新しいID形式が適用されます。

---

**最終更新**: 2025-10-10
**作業者**: Claude Code
**コミットID**: ef51f5d
