# セットアップガイド

## 1. 基本セットアップ

### 依存関係のインストール
```bash
pip install -e .
```

### 環境設定
```bash
# .envファイルを作成
cp .env.example .env

# .envファイルを編集してQiita APIトークンを設定
# QIITA_ACCESS_TOKEN=your_token_here
```

### Qiita APIトークンの取得
1. [Qiita設定ページ](https://qiita.com/settings/applications)にアクセス
2. 「個人用アクセストークン」を発行
3. 必要な権限：`read_qiita`, `write_qiita`

## 2. MCPサーバーの起動

```bash
# MCPサーバーを起動
autoqiita server

# または直接起動
python -m autoqiita.mcp_server
```

## 3. VSCode拡張機能のセットアップ

### 拡張機能のビルド
```bash
cd vscode_extension
npm install
npm run compile
```

### 拡張機能のインストール
1. VSCodeで `Ctrl+Shift+P` を押す
2. "Developer: Install Extension from Location" を選択
3. `vscode_extension` フォルダを選択

## 4. 使用方法

### 自動監視モード
1. VSCodeでワークスペースを開く
2. コマンドパレット（`Ctrl+Shift+P`）を開く
3. "Start AutoQiita Monitoring" を実行
4. ファイルを編集・保存すると自動でQiitaに下書き保存

### 手動保存
1. 保存したいファイルを開く
2. コマンドパレットで "Save Current File to Qiita" を実行

### ステータス確認
- ステータスバーの "AutoQiita" アイコンをクリック
- または "Show AutoQiita Status" コマンドを実行

## 5. 設定オプション

VSCodeの設定（`settings.json`）で以下を調整可能：

```json
{
  "autoqiita.mcpServerUrl": "http://localhost:8000",
  "autoqiita.autoSaveEnabled": true,
  "autoqiita.saveDelay": 5
}
```

## 6. CLIコマンド

```bash
# ステータス確認
autoqiita status

# 手動でファイル保存
autoqiita save path/to/file.md

# ワークスペース監視（スタンドアロン）
autoqiita monitor /path/to/workspace

# MCPサーバー起動
autoqiita server --host localhost --port 8000
```

## 7. トラブルシューティング

### サーバーが起動しない
- ポート8000が使用中でないか確認
- Qiita APIトークンが正しく設定されているか確認

### ファイルが保存されない
- ファイルの拡張子が監視対象に含まれているか確認
- `config/settings.json` で設定を調整

### 拡張機能が動作しない
- MCPサーバーが起動しているか確認
- VSCodeの出力パネルでエラーログを確認