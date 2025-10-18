#!/bin/bash
# セットアップスクリプト for AutoQiita with uv

set -e

echo "🚀 AutoQiita セットアップを開始します..."

# uvがインストールされているかチェック
if ! command -v uv &> /dev/null; then
    echo "❌ uvがインストールされていません。"
    echo "以下のコマンドでインストールしてください："
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uvが見つかりました"

# Python環境のセットアップ
echo "🐍 Python環境をセットアップ中..."
uv python install 3.11
uv venv

# 仮想環境の有効化
source .venv/bin/activate

# 依存関係のインストール
echo "📦 依存関係をインストール中..."
uv sync --group dev

# .envファイルの作成
if [ ! -f .env ]; then
    echo "⚙️  環境設定ファイルを作成中..."
    cp .env.example .env
    echo "📝 .envファイルを編集してQiita APIトークンを設定してください"
else
    echo "✅ .envファイルは既に存在します"
fi

# workspaces.jsonの確認
if [ ! -f workspaces.json ]; then
    echo "📁 ワークスペース設定ファイルを作成中..."
    echo '{
  "workspaces": []
}' > workspaces.json
fi

# VSCode拡張機能のセットアップ
if [ -d "vscode_extension" ]; then
    echo "🔧 VSCode拡張機能をセットアップ中..."
    cd vscode_extension
    
    if command -v npm &> /dev/null; then
        npm install
        npm run compile
        echo "✅ VSCode拡張機能のセットアップが完了しました"
    else
        echo "⚠️  npmが見つかりません。VSCode拡張機能のセットアップをスキップします"
    fi
    
    cd ..
fi

echo ""
echo "🎉 セットアップが完了しました！"
echo ""
echo "次のステップ："
echo "1. .envファイルを編集してQiita APIトークンを設定"
echo "2. MCPサーバーを起動: uv run autoqiita server"
echo "3. 別ターミナルでワークスペースを監視: uv run autoqiita monitor /path/to/your/project"
echo ""
echo "コマンド例："
echo "  uv run autoqiita status              # システム状態確認"
echo "  uv run autoqiita workspace add .     # 現在のディレクトリを監視対象に追加"
echo "  uv run autoqiita workspace list      # 登録済みワークスペース一覧"
echo ""