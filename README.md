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

## 他のプロジェクトでの使用方法

### 📁 **新しいプロジェクトを監視対象に追加**

#### **方法1: ワークスペース追加（推奨）**
```bash
# AutoQiitaディレクトリで実行
cd /path/to/AutoQiita

# 他のプロジェクトを追加
uv run autoqiita workspace add /path/to/your/project --name "ProjectName"

# 全ワークスペースを監視するサーバーを起動
uv run autoqiita server
```

#### **方法2: 直接監視**
```bash
# AutoQiitaディレクトリで実行
cd /path/to/AutoQiita

# 特定のプロジェクトのみ監視
uv run autoqiita monitor /path/to/your/project
```

#### **方法3: Makefileコマンド**
```bash
# AutoQiitaディレクトリで実行
cd /path/to/AutoQiita

# 他のプロジェクトを追加
make workspace-add-other PATH=/path/to/project NAME=ProjectName

# 全ワークスペース監視
make monitor-all

# 特定プロジェクト監視
make monitor-project PATH=/path/to/project
```

### 🔧 **便利なエイリアス設定**
```bash
# エイリアスを読み込み
source /path/to/AutoQiita/shell_aliases.sh

# または ~/.bashrc に追加
echo 'source /path/to/AutoQiita/shell_aliases.sh' >> ~/.bashrc
source ~/.bashrc

# 使用例
aq-add /path/to/project --name ProjectName
aq-list
aq-server
```

## 🚀 VSCodeでの他フォルダからの使用方法

AutoQiitaをグローバルにインストールすることで、**どのプロジェクトフォルダからでも**AutoQiitaコマンドを実行できます。

### **グローバルインストール**

```bash
# AutoQiitaディレクトリで実行
cd /path/to/AutoQiita
./install_global.sh
```

これにより、システム全体で`autoqiita`コマンドが使用可能になります。

### **どこからでも使えるコマンド**

```bash
# 任意のプロジェクトディレクトリで
cd /path/to/any/project

# ファイルをQiitaに保存
autoqiita save README.md

# 現在のディレクトリをワークスペースに追加
autoqiita workspace add . --name "MyProject"

# システム状態確認
autoqiita status

# ワークスペース一覧
autoqiita workspace list
```

### **📱 便利な短縮コマンド**

VSCode統合機能を使用すると、さらに短いコマンドが利用できます：

```bash
# VSCode統合機能を有効化
source /path/to/AutoQiita/vscode_integration.sh

# 短縮コマンド例
aqs file.md        # ファイルをQiitaに保存
aqa project-name   # 現在のディレクトリをワークスペースに追加
aqc                # システム状態確認
aqh                # ヘルプ表示
```

### **🔄 自動ロード設定**

新しいターミナルでも自動的に短縮コマンドを使えるようにするには：

```bash
# bashrcに自動ロード設定を追加
echo "
# AutoQiita VSCode Integration
if [ -f /path/to/AutoQiita/vscode_integration.sh ]; then
    source /path/to/AutoQiita/vscode_integration.sh
fi" >> ~/.bashrc

# 設定を即座に反映
source ~/.bashrc
```

### **💡 VSCodeでの実際の使用例**

1. **新しいプロジェクトで作業開始**：
   ```bash
   cd /path/to/new/project
   aqa my-new-project    # ワークスペースに追加
   ```

2. **ファイル編集後に即座に保存**：
   ```bash
   aqs README.md         # Qiitaに保存
   ```

3. **システム状態確認**：
   ```bash
   aqc                   # 全体状況をチェック
   ```

4. **自動監視の開始**：
   ```bash
   # 任意のディレクトリから
   autoqiita server      # 全ワークスペースを監視
   ```

### **✨ 主な利点**

- ✅ **プロジェクト間の移動不要**: AutoQiitaディレクトリに戻る必要なし
- ✅ **短縮コマンド**: `aqs`, `aqa`, `aqc`などで高速操作
- ✅ **VSCode統合**: 統合ターミナルでシームレスに使用
- ✅ **自動パス解決**: 相対パスも絶対パスも自動対応
- ✅ **永続設定**: 一度設定すれば全プロジェクトで使用可能

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

#### **コマンドパレット使用**
1. コマンドパレット（Ctrl+Shift+P）を開く
2. 以下のコマンドを実行：
   - `Start AutoQiita Monitoring` - 監視開始
   - `Stop AutoQiita Monitoring` - 監視停止
   - `Save Current File to Qiita` - 現在のファイルを手動保存
   - `Show AutoQiita Status` - 状態表示

#### **統合ターミナル使用（推奨）**
VSCodeの統合ターミナル（Ctrl+`）で以下のコマンドが使用可能：

```bash
# 基本コマンド（グローバルインストール後）
autoqiita save current-file.md    # 現在のファイルを保存
autoqiita workspace add .         # 現在のフォルダを追加
autoqiita status                  # 状態確認

# 短縮コマンド（vscode_integration.sh読み込み後）
aqs file.md                       # クイック保存
aqa project-name                  # ワークスペース追加
aqc                               # 状態確認
```

#### **ワークフロー例**
```bash
# 1. 新しいプロジェクトを開く
# File > Open Folder で任意のプロジェクトを開く

# 2. 統合ターミナルを開く（Ctrl+`）

# 3. AutoQiitaに追加
aqa my-project

# 4. ファイル編集後に保存
aqs README.md

# 5. 自動監視を開始（オプション）
autoqiita server &   # バックグラウンドで実行
```

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
