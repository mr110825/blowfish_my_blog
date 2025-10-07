# Hugo記事・スクラップID管理システム実装メモ

**作成日**: 2025-10-07
**作業目的**: Hugoブログの記事とスクラップに一意のIDを割り振る仕組みを実装

---

## 概要

このメモは、Hugoで構築した技術ブログに対して、記事とスクラップにユニークなID（Unixタイムスタンプ）を自動的に割り振るシステムを実装した手順を記録したものです。

### 実装した機能

1. **新規記事作成時の自動ID付与** - archetypesテンプレートにID設定を追加
2. **既存記事へのID追加** - 既存の全記事・スクラップにIDを自動追加
3. **ディレクトリ名へのID反映** - ファイルシステムレベルでもIDで識別可能に

### IDの形式

- **形式**: Unixタイムスタンプ（秒単位）
- **例**: `1759704789`（2025-10-06T07:53:09の場合）
- **生成方法**: 記事の`date`フィールドまたは`hugo new`実行時の現在時刻から生成

---

## 実装手順

### Step 1: Archetypes（テンプレート）の設定

新規記事作成時に自動的にIDが付与されるよう、archetypesファイルを作成・編集しました。

#### 編集・作成したファイル

**1. archetypes/default.md**（汎用テンプレート）

```toml
+++
id = "{{ now.Unix }}"
date = '{{ .Date }}'
draft = true
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
tags = []
+++
```

**2. archetypes/posts.md**（posts用テンプレート）

```toml
+++
id = "{{ now.Unix }}"
date = '{{ .Date }}'
draft = false
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
tags = []
+++
```

**3. archetypes/scraps.md**（scraps用テンプレート）

```toml
+++
id = "{{ now.Unix }}"
date = '{{ .Date }}'
draft = false
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
tags = []
+++
```

#### ポイント

- `{{ now.Unix }}`：Hugoのテンプレート関数で現在時刻のUnixタイムスタンプを取得
- `posts`と`scraps`は`draft = false`に設定（公開用）
- `default`は`draft = true`に設定（下書き用）

---

### Step 2: 既存記事へのID追加

既存の全記事・スクラップに対して、それぞれの作成日時（`date`フィールド）をベースにしたIDを追加しました。

#### 使用したスクリプト: `add_id_to_existing.py`

```python
#!/usr/bin/env python3

import os
import re
from datetime import datetime
from pathlib import Path

def parse_datetime(date_str):
    """日時文字列をUnixタイムスタンプに変換"""
    try:
        dt = datetime.fromisoformat(date_str.replace("'", ""))
        return str(int(dt.timestamp()))
    except Exception as e:
        print(f"日時パースエラー: {date_str} - {e}")
        return None

def add_id_to_file(file_path):
    """ファイルにIDを追加"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 既にIDが存在するかチェック
    if re.search(r'^id = ', content, re.MULTILINE):
        print(f"スキップ（ID既存）: {file_path}")
        return False

    # dateフィールドを検索
    date_match = re.search(r"^date = '([^']+)'", content, re.MULTILINE)
    if not date_match:
        print(f"スキップ（date未設定）: {file_path}")
        return False

    date_str = date_match.group(1)
    timestamp = parse_datetime(date_str)

    if not timestamp:
        print(f"エラー（日時変換失敗）: {file_path}")
        return False

    # フロントマターの最初の+++の後にIDを挿入
    id_line = f'id = "{timestamp}"\n'
    new_content = re.sub(
        r'^(\+\+\+)\n',
        f'\\1\n{id_line}',
        content,
        count=1,
        flags=re.MULTILINE
    )

    # ファイルに書き込み
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"追加完了: {file_path} (ID: {timestamp})")
    return True

def main():
    """メイン処理"""
    target_dirs = ['content/posts', 'content/scraps']
    processed = 0
    skipped = 0
    errors = 0

    for target_dir in target_dirs:
        for file_path in Path(target_dir).rglob('index.md'):
            if file_path.name == '_index.md':
                continue

            try:
                if add_id_to_file(file_path):
                    processed += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"エラー: {file_path} - {e}")
                errors += 1

    print("\n" + "="*50)
    print(f"処理完了: {processed}件")
    print(f"スキップ: {skipped}件")
    print(f"エラー: {errors}件")

if __name__ == '__main__':
    main()
```

#### 実行方法

```bash
# 実行権限を付与
chmod +x add_id_to_existing.py

# 実行
python3 add_id_to_existing.py
```

#### 実行結果

- 処理完了: 24件
- スキップ: 0件
- エラー: 0件

#### スクリプトの動作説明

1. **対象ファイル検索**: `content/posts`と`content/scraps`から`index.md`を再帰的に検索
2. **ID存在チェック**: 既にIDが存在する場合はスキップ
3. **日時取得**: `date = '2025-10-06T07:53:09+09:00'`形式から日時を抽出
4. **Unixタイムスタンプ変換**: Pythonの`datetime.fromisoformat()`で変換
5. **ID挿入**: フロントマターの最初の`+++`直後に`id = "1759704789"`を追加

---

### Step 3: ディレクトリ名へのID反映

各記事・スクラップのディレクトリ名に`{ID}_`プレフィックスを追加し、ファイルシステムレベルでも識別しやすくしました。

#### 使用したスクリプト: `rename_dirs_with_id.py`

```python
#!/usr/bin/env python3

import os
import re
import subprocess
from pathlib import Path

def get_id_from_file(file_path):
    """index.mdファイルからIDを取得"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        id_match = re.search(r'^id = "([^"]+)"', content, re.MULTILINE)
        if id_match:
            return id_match.group(1)
    except Exception as e:
        print(f"エラー: {file_path} - {e}")
    return None

def rename_directory_with_id(dir_path):
    """ディレクトリ名にIDを追加してリネーム"""
    index_file = dir_path / 'index.md'

    if not index_file.exists():
        return False

    post_id = get_id_from_file(index_file)
    if not post_id:
        print(f"スキップ（ID未設定）: {dir_path}")
        return False

    current_name = dir_path.name

    # 既に{数字}_で始まっている場合はスキップ
    if re.match(r'^\d+_', current_name):
        print(f"スキップ（既にID付き）: {dir_path}")
        return False

    new_name = f"{post_id}_{current_name}"
    new_path = dir_path.parent / new_name

    if new_path.exists():
        print(f"スキップ（同名ディレクトリ存在）: {new_path}")
        return False

    # git mvでリネーム（履歴を保持）
    try:
        result = subprocess.run(
            ['git', 'mv', str(dir_path), str(new_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"リネーム完了: {current_name} → {new_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"エラー（git mv失敗）: {dir_path}")
        print(f"  {e.stderr}")
        return False

def main():
    """メイン処理"""
    target_dirs = ['content/posts', 'content/scraps']
    renamed = 0
    skipped = 0
    errors = 0

    for target_dir in target_dirs:
        target_path = Path(target_dir)
        if not target_path.exists():
            continue

        for item in sorted(target_path.iterdir()):
            if not item.is_dir() or item.name.startswith('_'):
                continue

            try:
                if rename_directory_with_id(item):
                    renamed += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"エラー: {item} - {e}")
                errors += 1

    print("\n" + "="*50)
    print(f"リネーム完了: {renamed}件")
    print(f"スキップ: {skipped}件")
    print(f"エラー: {errors}件")
    print("\n注意: git mvでリネームしました。変更を確認後、コミットしてください。")

if __name__ == '__main__':
    main()
```

#### 実行方法

```bash
# 実行権限を付与
chmod +x rename_dirs_with_id.py

# 実行
python3 rename_dirs_with_id.py
```

#### 実行結果

- リネーム完了: 24件
- スキップ: 0件
- エラー: 0件

#### リネーム例

```
Before: content/posts/favicon_settings/
After:  content/posts/1754190549_favicon_settings/

Before: content/scraps/ap2025_manage_study_memo/
After:  content/scraps/1759704789_ap2025_manage_study_memo/
```

#### 重要なポイント

- **git mv使用**: 通常の`mv`ではなく`git mv`を使用することで、Git履歴を保持
- **内部リンク更新**: ディレクトリ名変更後、`content/scraps/_index.md`などの内部リンクも更新が必要

---

### Step 4: 内部リンクの更新

ディレクトリ名変更に伴い、Hugoの`ref`ショートコードで参照している箇所を手動で更新しました。

#### 更新例（`content/scraps/_index.md`）

**Before:**
```markdown
- [Python概要とインストールなど]({{< ref "styudy-python" >}})
- [pyenvでPythonバージョン管理｜インストールから切り替えまで]({{< ref "study-pyenv" >}})
```

**After:**
```markdown
- [Python概要とインストールなど]({{< ref "1756853577_styudy-python" >}})
- [pyenvでPythonバージョン管理｜インストールから切り替えまで]({{< ref "1756984928_study-pyenv" >}})
```

#### 自動化の可能性

内部リンクの更新も正規表現で自動化可能ですが、今回は対象が`_index.md`1ファイルのみだったため手動で実施しました。

---

## 最終確認

### ビルドテスト

```bash
hugo --quiet && echo "✅ ビルド成功"
```

すべての変更後、ビルドが正常に完了することを確認しました。

### ディレクトリ構造の確認

```bash
ls content/posts/
```

**出力例:**
```
1754153716_how_to_download_github_issues
1754190549_favicon_settings
1754519137_git-worktree-hands-on
1754826645_how-to-Record-PC-internal-audio
1757130872_How-to-Get-Your-Hugo+Blowfish-Website-Indexed-by-Google
_index.md
```

### フロントマターの確認

```toml
+++
id = "1754190549"
date = '2025-08-03T12:09:09+09:00'
draft = false
title = 'BlowfishでFaviconを設定する方法'
tags = ["Hugo", "Blowfish"]
+++
```

---

## 今後の使い方

### 新規記事の作成

archetypesの設定により、`hugo new`コマンドで自動的にIDが付与されます。

#### Posts（記事）を作成

```bash
hugo new posts/new-article-name/index.md
```

自動生成されるフロントマター:
```toml
+++
id = "1759798470"  # 実行時のUnixタイムスタンプ
date = '2025-10-07T09:54:30+09:00'
draft = false
title = 'New Article Name'
tags = []
+++
```

#### Scraps（スクラップ）を作成

```bash
hugo new scraps/new-scrap-name/index.md
```

自動生成されるフロントマター:
```toml
+++
id = "1759798470"  # 実行時のUnixタイムスタンプ
date = '2025-10-07T09:54:30+09:00'
draft = false
title = 'New Scrap Name'
tags = []
+++
```

### ディレクトリ名の命名規則

今後、新規作成する記事のディレクトリ名は手動で`{ID}_`プレフィックスを付けることを推奨します。

**推奨命名例:**
```bash
# IDを先に確認してからディレクトリ名を決める
hugo new posts/temporary-name/index.md

# 生成されたIDを確認（例: 1759800000）
cat content/posts/temporary-name/index.md | grep "^id"

# ディレクトリをリネーム
git mv content/posts/temporary-name content/posts/1759800000_actual-article-name
```

または、最初から計画的に：
```bash
# 現在のUnixタイムスタンプを取得
current_timestamp=$(date +%s)

# IDを含めたディレクトリ名で作成
hugo new posts/${current_timestamp}_new-article/index.md
```

---

## 学習ポイント

### 1. Hugoのテンプレート変数

- `{{ now.Unix }}`: 現在のUnixタイムスタンプ
- `{{ .Date }}`: 記事の作成日時
- `{{ .File.ContentBaseName }}`: ファイル名（拡張子なし）

### 2. Pythonでのファイル操作

- `Path.rglob()`: 再帰的なファイル検索
- `re.search()`: 正規表現による文字列検索
- `re.sub()`: 正規表現による文字列置換
- `datetime.fromisoformat()`: ISO形式の日時文字列をパース

### 3. Git操作のベストプラクティス

- `git mv`: ファイル/ディレクトリのリネーム時は履歴を保持
- `subprocess.run()`: Pythonスクリプトから外部コマンドを実行

### 4. 正規表現パターン

```python
# フロントマターのIDフィールドを検索
r'^id = "([^"]+)"'

# フロントマターのdateフィールドを検索
r"^date = '([^']+)'"

# 数字で始まる文字列（ID付きディレクトリ名）
r'^\d+_'
```

---

## トラブルシューティング

### ビルドエラー: REF_NOT_FOUND

**原因**: ディレクトリ名変更後、内部リンクが古い名前を参照している

**解決方法**: `ref`ショートコード内のパスを新しいディレクトリ名に更新

```markdown
<!-- Before -->
{{< ref "old-directory-name" >}}

<!-- After -->
{{< ref "1759800000_old-directory-name" >}}
```

### スクリプト実行時のエラー: permission denied

**原因**: 実行権限が付与されていない

**解決方法**:
```bash
chmod +x script_name.py
```

### 日時変換エラー: datetime parse failed

**原因**: `date`フィールドが標準的なISO 8601形式でない

**解決方法**: 手動でフロントマターの`date`フィールドを修正

---

## 参考リンク

- [Hugo Archetypes | Hugo Documentation](https://gohugo.io/content-management/archetypes/)
- [Hugo Template Variables | Hugo Documentation](https://gohugo.io/variables/)
- [Python datetime documentation](https://docs.python.org/3/library/datetime.html)
- [Python pathlib documentation](https://docs.python.org/3/library/pathlib.html)

---

## まとめ

今回の実装により、以下が実現しました：

1. ✅ 新規記事作成時の自動ID付与
2. ✅ 既存全24件の記事・スクラップへのID追加
3. ✅ ディレクトリ名へのID反映
4. ✅ ビルドの正常動作確認

この仕組みにより、記事やスクラップを一意に識別でき、将来的なデータベース連携やAPI開発時にも活用できます。
