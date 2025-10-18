# AutoQiita記事の手動投稿手順

## 現在の状況
- 記事ファイル `article_draft.md` を作成しました
- Qiita APIトークンで403エラーが発生中
- セキュリティチェックは正常に動作（info レベルの問題1件検出）

## 手動投稿手順

### 1. Qiita APIトークンの確認
現在のトークンに問題がある可能性があります。

1. [Qiita設定ページ](https://qiita.com/settings/applications)にアクセス
2. 新しいアクセストークンを生成
3. 必要な権限を確認：
   - `read_qiita`: 自分の記事の読み取り
   - `write_qiita`: 記事の作成・更新

### 2. .envファイルの更新
```bash
# 新しいトークンに更新
QIITA_ACCESS_TOKEN=新しいトークン
```

### 3. 再試行
```bash
uv run autoqiita save article_draft.md
```

### 4. 手動コピー（代替案）
APIが使用できない場合：

1. `article_draft.md` の内容をコピー
2. [Qiita記事作成ページ](https://qiita.com/drafts/new)で新規記事作成
3. Markdown内容を貼り付け
4. タグを追加：`Python`, `VSCode`, `Qiita`, `自動化`, `セキュリティ`

## セキュリティチェック結果
✅ 自動スキャン完了
- 検出問題: 1件（info レベル）
- GitHubURLが含まれていますが、実際のサービスURLなので問題なし

## 記事の特徴
- **総文字数**: 約8,000文字
- **技術内容**: Python, FastAPI, セキュリティ, 自動化
- **対象読者**: VSCode使用者、Qiita投稿者
- **実装済み機能**: 完全動作するシステム

この記事により、AutoQiitaシステムの全容と技術的な工夫を共有できます。