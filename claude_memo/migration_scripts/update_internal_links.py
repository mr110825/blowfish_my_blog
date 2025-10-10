#!/usr/bin/env python3

import os
import re
import json
from pathlib import Path

def update_links_in_file(file_path, mapping):
    """ファイル内の内部リンクを新しいID形式に更新"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        updated_count = 0

        # 各旧IDを新IDに置換
        for old_id, new_id in mapping.items():
            # {{< ref "旧ID_ディレクトリ名" >}} パターンを検索して置換
            pattern = r'(\{\{<\s*ref\s+")(' + old_id + r'_[^"]+)("\s*>\}\})'

            def replace_func(match):
                nonlocal updated_count
                old_ref = match.group(2)
                new_ref = old_ref.replace(old_id, new_id, 1)
                updated_count += 1
                return match.group(1) + new_ref + match.group(3)

            content = re.sub(pattern, replace_func, content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"更新完了: {file_path} ({updated_count}箇所)")
            return updated_count
        else:
            print(f"変更なし: {file_path}")
            return 0

    except Exception as e:
        print(f"エラー: {file_path} - {e}")
        return 0

def main():
    """メイン処理"""
    # ID変換マッピングを読み込み
    with open('id_mapping.json', 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    print(f"ID変換マッピング読み込み完了: {len(mapping)}件\n")

    # 内部リンクを含む可能性のあるファイルを検索
    target_files = [
        'content/scraps/_index.md',
        'content/posts/_index.md',
    ]

    # 全ての記事内部も検索（相互参照がある可能性）
    for file_path in Path('content').rglob('index.md'):
        if file_path.name != '_index.md':
            target_files.append(str(file_path))

    total_updates = 0
    updated_files = 0

    for file_path in target_files:
        if not Path(file_path).exists():
            continue

        updates = update_links_in_file(file_path, mapping)
        if updates > 0:
            total_updates += updates
            updated_files += 1

    print("\n" + "="*50)
    print(f"更新したファイル: {updated_files}件")
    print(f"更新したリンク: {total_updates}箇所")

if __name__ == '__main__':
    main()
