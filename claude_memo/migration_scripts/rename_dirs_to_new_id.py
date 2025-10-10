#!/usr/bin/env python3

import os
import re
import subprocess
from pathlib import Path

def get_id_from_file(file_path):
    """index.mdファイルから新しいID（YYMMDDhhmmss形式）を取得"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        id_match = re.search(r'^id = "([^"]+)"', content, re.MULTILINE)
        if id_match:
            return id_match.group(1)
    except Exception as e:
        print(f"エラー: {file_path} - {e}")
    return None

def rename_directory_with_new_id(dir_path):
    """ディレクトリ名を新しいID形式でリネーム"""
    index_file = dir_path / 'index.md'

    if not index_file.exists():
        return False

    new_id = get_id_from_file(index_file)
    if not new_id:
        print(f"スキップ（ID未設定）: {dir_path}")
        return False

    current_name = dir_path.name

    # 旧ID形式（10桁数字）で始まっている場合、それを除去
    # 例: 1755557154_memo-take-notes → memo-take-notes
    base_name = re.sub(r'^\d{10}_', '', current_name)

    # 新しいID形式（12桁数字）で始まっている場合もチェック
    if re.match(r'^\d{12}_', current_name):
        print(f"スキップ（既に新ID付き）: {dir_path}")
        return False

    new_name = f"{new_id}_{base_name}"
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
                if rename_directory_with_new_id(item):
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
    print("\n注意: git mvでリネームしました。変更を確認後、次の処理に進んでください。")

if __name__ == '__main__':
    main()
