+++
id = "251214215249"
date = '2025-12-14T21:52:49+09:00'
draft = false
title = 'Dockerで勉強用の使い捨て環境を構築する'
tags = ["ツール", "Docker", "ハンズオン・チュートリアル", "入門"]
+++

## 今日学んだこと

Dockerを使って学習用の使い捨て環境を構築する方法を学びました。`docker run -it --rm`の基本パターンを押さえておけば、Node.js、Python、MySQL、Linux基礎など様々な学習環境をローカルPCを汚さずに構築できます。

## 学習内容

### 基本パターン

```bash
# 使い捨てコンテナの基本形
docker run -it --rm <イメージ名> bash

# ローカルファイルをマウントする場合
docker run -it --rm -v $(pwd):/work -w /work <イメージ名> bash
```

| オプション | 意味 |
|-----------|------|
| `-it` | 対話モード（ターミナルで操作可能） |
| `--rm` | 終了時にコンテナ自動削除 |
| `-v $(pwd):/work` | カレントディレクトリをコンテナ内の/workにマウント |
| `-w /work` | 作業ディレクトリを/workに設定 |

### 学習内容別イメージ一覧

| 学習内容 | イメージ | 用途 |
|---------|---------|------|
| Node.js/フロントエンド | `node:20` | npm、Babel、Webpack、React等 |
| Python/データ分析 | `python:3.12` | pip、Pandas、Scikit-learn等 |
| MySQL | `mysql:8.0` | SQL学習 |
| Linux基礎 | `ubuntu:24.04` | コマンド操作練習 |

### Node.js環境

```bash
docker run -it --rm -v $(pwd):/work -w /work node:20 bash

# コンテナ内
npm init -y
npm install --save-dev @babel/cli @babel/core @babel/preset-env
```

### Python環境

```bash
docker run -it --rm -v $(pwd):/work -w /work python:3.12 bash

# コンテナ内
pip install pandas matplotlib scikit-learn
python script.py
```

### MySQL環境

```bash
# 単体でSQL練習（データは消える）
docker run -it --rm -e MYSQL_ROOT_PASSWORD=root mysql:8.0 mysql -uroot -proot

# バックグラウンドで起動してクライアントから接続
docker run -d --rm --name mysql-study -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 mysql:8.0

# 接続
docker exec -it mysql-study mysql -uroot -proot

# 終了時
docker stop mysql-study
```

### Docker Compose（複数コンテナ連携）

アプリとDBなど複数コンテナを扱う場合に便利です。

```yaml
# docker-compose.yml
services:
  app:
    image: node:20
    volumes:
      - .:/work
    working_dir: /work
    command: bash
    tty: true
    stdin_open: true

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: study
```

```bash
# 起動
docker compose up -d

# アプリコンテナに入る
docker compose exec app bash

# 終了・削除
docker compose down
```

### Dockerfileで環境を固定

毎回同じ環境を再現したい場合に使用します。

```dockerfile
# Dockerfile
FROM node:20
WORKDIR /workspace
RUN npm install -g npm@latest
CMD ["bash"]
```

```bash
docker build -t study-env .
docker run -it --rm -v $(pwd):/workspace study-env
```

### 学習例：Babelのトランスパイル

実際にBabelの学習環境を構築してみます。

```bash
mkdir babel-study && cd babel-study
docker run -it --rm -v $(pwd):/work -w /work node:20 bash

# コンテナ内
npm init -y
npm install --save-dev @babel/cli @babel/core @babel/preset-env
echo '{ "presets": ["@babel/preset-env"] }' > .babelrc
mkdir src dist
echo 'const greet = () => console.log("Hello");' > src/app.js
npx babel src/app.js -o dist/app.js
cat dist/app.js
exit
```

マウントしたファイルは手元に残ります。不要になったら`babel-study`ディレクトリごと削除すればクリーンアップ完了です。

## まとめ

| パターン | コマンド | 用途 |
|---------|---------|------|
| 基本形 | `docker run -it --rm <イメージ> bash` | 簡単な動作確認 |
| ファイル永続化 | `docker run -it --rm -v $(pwd):/work -w /work <イメージ> bash` | 学習成果を残したい場合 |
| 複数コンテナ | `docker compose up -d` | アプリ+DB連携 |
| 環境固定 | `Dockerfile` + `docker build` | チームで同一環境を共有 |

- `--rm`オプションでコンテナ終了時に自動削除されるため、ローカル環境を汚さない
- `-v`でマウントしたディレクトリ内のファイルはコンテナ終了後も残る
- 学習終了後はディレクトリごと削除すれば完全にクリーンアップできる

## 参考

- [Docker公式ドキュメント](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
