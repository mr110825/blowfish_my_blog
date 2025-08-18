# 技術的デジャブ回避メモ帳

技術的デジャブを回避するためにメモや備忘録

## コマンドリファレンス

```bash
# Hugoの開発サーバー起動
hugo server
```

```bash
# Hugoの開発サーバー起動（下書き含む）
hugo server -D
```

```bash
# Hugoで新規の記事を作成
hugo new posts/<記事のタイトル>/index.md

# Hugoで新規のスクラップメモを作成
hugo new scraps/<メモのタイトル>/index.md
```

```
# geminiで記事を評価する
gemini --prompt "@content/posts/<記事のタイトル> を @blog_evaluation_prompt_5criteria.md を参考にして評価してほしい"
```

### スクラップメモ用のチートシート

```html
{{< timeline >}}

{{< timelineItem header="メモのヘッダー" badge="2025/XX/XX">}}

{{< /timelineItem >}}

{{< /timeline >}}
```