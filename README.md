# AutoQiita - VSCode to Qiita Auto-Save System

VSCodeで作業した内容を自動でQiitaの下書きに保存するMCPサーバーシステム

## 機能

- VSCodeでのファイル変更を監視
- Markdown形式でのコンテンツ自動変換
- Qiita APIを使った下書き自動保存
- MCPプロトコルによるVSCodeとの連携
- 複数ワークスペースの管理
- **セキュリティスキャン**: 機密情報や危険なコードパターンを自動検出
- **アップロード制御**: 重大なセキュリティ問題がある場合の自動ブロック

## セットアップ（uv使用）

### 1. 前提条件
- [uv](https://docs.astral.sh/uv/) がインストール済み
- [Qiita APIトークン](https://qiita.com/settings/applications) を取得済み

### 2. プロジェクトのセットアップ

```bash
# プロジェクトをクローン
git clone <repository-url>
cd AutoQiita

# uvでPython環境を作成・アクティベート
uv python install 3.11
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係をインストール
uv sync

# 開発用依存関係も含める場合
uv sync --group dev
```

### 3. 環境設定

```bash
# 環境変数ファイルを作成
cp .env.example .env

# .envファイルを編集してQiita APIトークンを設定
nano .env
```

### 4. システムの起動

```bash
# MCPサーバーを起動
uv run autoqiita server

# または、別ターミナルで監視モード
uv run autoqiita monitor /path/to/your/project
```

### 5. VSCode拡張機能のセットアップ

```bash
cd vscode_extension
npm install
npm run compile

# VSCodeで拡張機能をデバッグモードで起動
# F5キーを押すか、Run > Start Debugging
```

## 使用方法

### コマンドライン

```bash
# ワークスペースを追加
uv run autoqiita workspace add /path/to/project --name "MyProject"

# 登録済みワークスペース一覧
uv run autoqiita workspace list

# 単一ファイルを手動保存（セキュリティチェック付き）
uv run autoqiita save /path/to/file.py

# セキュリティチェックを無効にして保存
uv run autoqiita save /path/to/file.py --no-security-check

# セキュリティ問題があっても強制保存
uv run autoqiita save /path/to/file.py --force

# ファイルのセキュリティスキャンのみ実行
uv run autoqiita security scan /path/to/file.py

# 監視対象拡張子の管理
uv run autoqiita extensions list              # 現在の監視対象一覧
uv run autoqiita extensions add               # インタラクティブ追加
uv run autoqiita extensions add react         # キーワードで追加
uv run autoqiita extensions add .vue          # 直接拡張子追加
uv run autoqiita extensions suggest react     # 関連拡張子を提案
uv run autoqiita extensions remove .tsx       # 拡張子削除

# システム状態確認
uv run autoqiita status
```

### VSCodeコマンド

1. コマンドパレット（Ctrl+Shift+P）を開く
2. 以下のコマンドを実行：
   - `Start AutoQiita Monitoring` - 監視開始
   - `Stop AutoQiita Monitoring` - 監視停止
   - `Save Current File to Qiita` - 現在のファイルを手動保存
   - `Show AutoQiita Status` - 状態表示

## 開発

```bash
# 開発用依存関係をインストール
uv sync --group dev

# コードフォーマット
uv run black .

# 型チェック
uv run mypy autoqiita

# テスト実行
uv run pytest

# pre-commitフックをセットアップ
uv run pre-commit install

# セキュリティスキャン実行
make security-scan

# セキュリティ設定確認
make security-check-config
```

## セキュリティ機能

### 自動検出項目

- **認証情報**: パスワード、APIキー、アクセストークン、秘密鍵
- **個人情報**: メールアドレス、IPアドレス、電話番号
- **危険なコード**: eval/exec、シェルインジェクション、pickleの危険な使用
- **Webセキュリティ**: XSS、SQLインジェクション攻撃パターン
- **ファイルパス**: 個人のホームディレクトリパス

### セキュリティレベル

- **Critical**: アップロードがブロックされる重大な問題
- **High**: 警告表示、確認が必要
- **Medium**: 注意喚起
- **Low**: 情報提示

### カスタマイズ

`config/security_rules.json` でセキュリティルールをカスタマイズ可能です。

## 監視対象ファイル管理

### 拡張子の追加

```bash
# インタラクティブ追加（推奨）
uv run autoqiita extensions add

# キーワードで関連拡張子を提案・追加
uv run autoqiita extensions add react      # .jsx, .tsx を提案
uv run autoqiita extensions add vue        # .vue を提案
uv run autoqiita extensions add python     # .py を提案

# 直接拡張子を追加
uv run autoqiita extensions add .go
uv run autoqiita extensions add .rs
```

### サポートされるキーワード

- **react**: `.jsx`, `.tsx`
- **vue**: `.vue`
- **angular**: `.ts`, `.html`, `.scss`
- **node**: `.js`, `.ts`, `.json`
- **python**: `.py`
- **web**: `.html`, `.css`, `.js`
- **config**: `.json`, `.yaml`, `.yml`, `.toml`, `.ini`
- **script**: `.sh`, `.bash`, `.ps1`
- **database**: `.sql`
- **docker**: `.dockerfile`

### 設定ファイル

`config/watched_extensions.json` で監視対象拡張子をカスタマイズできます。

## システムの終了

### 完全終了・クリーンアップ

```bash
# 自動クリーンアップスクリプトを実行
./end.sh

# またはMakefileを使用
make end
```

### プロセスのみ停止

```bash
# 実行中のプロセスのみ停止（ファイルは残す）
make stop

# 手動でプロセス停止
pkill -f "autoqiita server"
pkill -f "autoqiita monitor"
```

## 設定

- `config/settings.json`: 監視対象ファイル、除外パターンなど
- `.env`: Qiita APIトークンなどの機密情報
- `workspaces.json`: 登録済みワークスペース一覧
