#!/usr/bin/env python3

import os
import re
import json
from datetime import datetime
from pathlib import Path

def convert_timestamp_to_yymmddhhmmss(unix_timestamp):
    """UnixタイムスタンプをYYMMDDhhmmss形式に変換"""
    try:
        dt = datetime.fromtimestamp(int(unix_timestamp))
        return dt.strftime('%y%m%d%H%M%S')
    except Exception as e:
        print(f"エラー（タイムスタンプ変換失敗）: {unix_timestamp} - {e}")
        return None

def convert_id_in_file(file_path):
    """ファイル内のIDをYYMMDDhhmmss形式に変換"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 現在のID（Unixタイムスタンプ）を検索
        id_match = re.search(r'^id = "(\d+)"', content, re.MULTILINE)
        if not id_match:
            print(f"スキップ（ID未設定）: {file_path}")
            return None, None

        old_id = id_match.group(1)

        # 新しいIDに変換
        new_id = convert_timestamp_to_yymmddhhmmss(old_id)
        if not new_id:
            return None, None

        # IDを置換
        new_content = re.sub(
            r'^id = "' + old_id + '"',
            f'id = "{new_id}"',
            content,
            flags=re.MULTILINE
        )

        # ファイルに書き込み
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"変換完了: {file_path}")
        print(f"  {old_id} → {new_id}")

        return old_id, new_id

    except Exception as e:
        print(f"エラー: {file_path} - {e}")
        return None, None

def main():
    """メイン処理"""
    target_dirs = ['content/posts', 'content/scraps']
    converted = 0
    skipped = 0
    errors = 0

    # 変換マッピングを保存（ディレクトリリネームで使用）
    mapping = {}

    for target_dir in target_dirs:
        target_path = Path(target_dir)
        if not target_path.exists():
            continue

        for file_path in sorted(target_path.rglob('index.md')):
            if file_path.name == '_index.md':
                continue

            try:
                old_id, new_id = convert_id_in_file(file_path)
                if old_id and new_id:
                    converted += 1
                    mapping[old_id] = new_id
                else:
                    skipped += 1
            except Exception as e:
                print(f"エラー: {file_path} - {e}")
                errors += 1

    # マッピングをJSONファイルに保存
    with open('id_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print("\n" + "="*50)
    print(f"変換完了: {converted}件")
    print(f"スキップ: {skipped}件")
    print(f"エラー: {errors}件")
    print(f"\nID変換マッピング: id_mapping.json に保存しました")

if __name__ == '__main__':
    main()
