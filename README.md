# 技術的デジャブ回避メモ帳

技術的デジャブを回避するためにメモや備忘録

## よく利用するコマンド

```bash
# Hugoの開発サーバー起動
hugo server
```

```bash
# Hugoで新規の記事を作成
hugo new posts/<記事のタイトル>/index.md
```

```
# geminiで記事を評価する
gemini --prompt "@content/posts/<記事のタイトル> を @blog_evaluation_prompt_5criteria.md を参考にして評価してほしい"
```
