+++
id = "251123221331"
date = '2025-11-23T22:13:31+09:00'
draft = false
title = 'ログ調査_more・less・grep・zgrep'
tags = ["ツール", "メモ", "実践"]
+++
## はじめに
ヘルプデスク・監視運用でTeratermを使ってログ調査を行う際のコマンドを備忘録としてまとめる。

## 前提条件
- サービスログは`.log`ファイルとして保管
- 1日経過したログは`.gz`形式で圧縮保存

## 実施したこと
特定のエラーメッセージ(ERROR)がログに含まれているか確認したい。

---

## サンプルファイルの内容

### service.log (通常のログファイル)
```log
2024-11-20 10:15:32 INFO  Application started successfully
2024-11-20 10:15:45 INFO  User login: user_id=12345
2024-11-20 10:16:03 WARN  High memory usage detected: 85%
2024-11-20 10:16:15 INFO  Processing request: /api/users
2024-11-20 10:16:28 ERROR Database connection timeout
2024-11-20 10:16:30 ERROR Failed to execute query: SELECT * FROM users
2024-11-20 10:17:12 INFO  Request completed: status=200
2024-11-20 10:18:45 WARN  Response time exceeded threshold: 3.5s
2024-11-20 10:19:03 INFO  User logout: user_id=12345
2024-11-20 10:20:15 ERROR Network unreachable: host=192.168.1.100
2024-11-20 10:21:30 INFO  Backup process started
2024-11-20 10:22:45 INFO  Backup completed successfully
```

### ファイルの一覧表示
```bash
$ ls -lh service.log*
-rw-r--r-- 1 root root 696 Nov 23 13:03 service.log
-rw-r--r-- 1 root root 375 Nov 23 13:03 service.log.gz
```

---

## 使用コマンドと実行例

### 1. 通常のログファイル(.log)からERRORを検索

**コマンド:**
```bash
grep ERROR service.log
```

**実行結果:**
```bash
2024-11-20 10:16:28 ERROR Database connection timeout
2024-11-20 10:16:30 ERROR Failed to execute query: SELECT * FROM users
2024-11-20 10:20:15 ERROR Network unreachable: host=192.168.1.100
```

### 2. 圧縮ログファイル(.gz)からERRORを検索

**コマンド:**
```bash
zgrep ERROR service.log.gz
```

**実行結果:**
```bash
2024-11-20 10:16:28 ERROR Database connection timeout
2024-11-20 10:16:30 ERROR Failed to execute query: SELECT * FROM users
2024-11-20 10:20:15 ERROR Network unreachable: host=192.168.1.100
```

💡 `.log`でも`.gz`でも同じ結果が得られる!

### 3. 行番号付きで検索

**コマンド:**
```bash
grep -n ERROR service.log
```

**実行結果:**
```bash
5:2024-11-20 10:16:28 ERROR Database connection timeout
6:2024-11-20 10:16:30 ERROR Failed to execute query: SELECT * FROM users
10:2024-11-20 10:20:15 ERROR Network unreachable: host=192.168.1.100
```

### 4. 複数パターンを同時に検索 (ERROR または WARN)

**コマンド:**
```bash
grep -E "ERROR|WARN" service.log
```

**実行結果:**
```bash
2024-11-20 10:16:03 WARN  High memory usage detected: 85%
2024-11-20 10:16:28 ERROR Database connection timeout
2024-11-20 10:16:30 ERROR Failed to execute query: SELECT * FROM users
2024-11-20 10:18:45 WARN  Response time exceeded threshold: 3.5s
2024-11-20 10:20:15 ERROR Network unreachable: host=192.168.1.100
```

### 5. 検索結果の件数をカウント

**コマンド:**
```bash
grep -c ERROR service.log
```

**実行結果:**
```bash
3
```

---

## よく使うgrepオプション

| オプション | 説明 | 使用例 |
|-----------|------|--------|
| `-n` | 行番号を表示 | `grep -n ERROR service.log` |
| `-i` | 大文字小文字を区別しない | `grep -i error service.log` |
| `-c` | マッチした行数をカウント | `grep -c ERROR service.log` |
| `-v` | マッチしない行を表示 | `grep -v INFO service.log` |
| `-A 数字` | マッチ行の後ろN行も表示 | `grep -A 3 ERROR service.log` |
| `-B 数字` | マッチ行の前N行も表示 | `grep -B 2 ERROR service.log` |
| `-C 数字` | マッチ行の前後N行を表示 | `grep -C 2 ERROR service.log` |
| `-E` | 拡張正規表現を使用 | `grep -E "ERROR\|WARN" service.log` |

---

## moreとlessの違い

| 項目 | more | less |
|------|------|------|
| **スクロール方向** | 前方のみ(下方向) | 前後自由(上下両方向) |
| **検索機能** | 限定的 | 充実(前方/後方検索可能) |
| **ファイル読み込み** | 全体を読み込む | 必要な部分のみ読み込む |
| **大容量ファイル** | 遅い | 高速 |
| **操作** | シンプル | 高機能(viライク) |
| **終了時の表示** | 画面に残る | 画面から消える |

### 主な操作方法

**more:**
- `Space`: 次のページ
- `Enter`: 1行進む
- `q`: 終了

**less:**
- `Space`/`f`: 次のページ
- `b`: 前のページ
- `↑`/`↓`: 1行ずつ移動
- `/文字列`: 前方検索
- `?文字列`: 後方検索
- `n`: 次の検索結果
- `N`: 前の検索結果
- `q`: 終了

### lessでの検索実例

```bash
less service.log
```

less内で:
```
/ERROR    # 「ERROR」を前方検索
n         # 次のERRORへジャンプ
N         # 前のERRORへ戻る
```

### 使い分けのポイント
- **more**: シンプルに前から順に見たい場合
- **less**: 大きなログファイルの調査、検索が必要な場合

💡 **豆知識**: "less is more"という言葉遊びから、moreの改良版としてlessが誕生した

---

## 各コマンドの説明

| コマンド | 説明 | 対象ファイル |
|---------|------|-------------|
| `grep` | テキストファイルから文字列を検索 | `.log`など |
| `zgrep` | 圧縮ファイルを一時的に解凍して検索（解凍ファイルは作成しない） | `.gz` |
| `less` | ページ単位でファイルを表示(検索機能付き) | `.log`など |
| `zless` | 圧縮ファイルをlessで表示 | `.gz` |
| `more` | シンプルなページャー(前方スクロールのみ) | `.log`など |

---

## よくある間違い

❌ **パイプの誤用**
```bash
more service.log | zgrep ERROR
```
→ zgrepは圧縮ファイル専用。パイプで渡されたデータは圧縮されていない

⭕ **正しい使い方**
```bash
# 通常ファイル
grep ERROR service.log

# 圧縮ファイル
zgrep ERROR service.log.gz
```

---

❌ **大きなログファイルにmore**
```bash
more huge_file.log  # 読み込みが遅い
```

⭕ **lessを使う**
```bash
less huge_file.log  # 高速に起動
```

---

## 学んだこと

- 圧縮ファイルには`z系コマンド`(zgrep, zless)を直接使う方が効率的  
- `less`は`more`より高機能で検索も可能  
- ログ調査では`less`の方が実用的(前後に移動できるため)  
- `grep -n`で行番号を表示すると、lessで該当行にジャンプしやすい  
- `-A`, `-B`, `-C`オプションで前後の文脈も確認できる  

---

## 参考: よく使うログ調査パターン

```bash
# パターン1: エラーログを抽出して別ファイルに保存
grep ERROR service.log > error_only.log

# パターン2: 最新のエラーを確認
grep ERROR service.log | tail -5

# パターン3: エラーとその前後2行を表示
grep -C 2 ERROR service.log

# パターン4: 複数ファイルからエラーを検索
grep ERROR service*.log

# パターン5: 圧縮ファイルも含めて検索
zgrep ERROR service.log.gz
```