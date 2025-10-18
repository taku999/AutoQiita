#!/bin/bash
# グローバルインストールスクリプト

echo "🚀 AutoQiitaをグローバルにインストールします..."

# 現在のディレクトリを保存
CURRENT_DIR=$(pwd)
AUTOQIITA_DIR="/home/bell999/github/AutoQiita"

# AutoQiitaディレクトリに移動
cd "$AUTOQIITA_DIR"

# pipxでグローバルインストール（推奨）
if command -v pipx &> /dev/null; then
    echo "📦 pipxでインストール中..."
    pipx install -e .
    echo "✅ pipxインストール完了"
elif command -v uv &> /dev/null; then
    echo "📦 uvでグローバルインストール中..."
    uv tool install -e .
    echo "✅ uvツールインストール完了"
else
    echo "📦 pipでグローバルインストール中..."
    pip install -e .
    echo "✅ pipインストール完了"
fi

# 元のディレクトリに戻る
cd "$CURRENT_DIR"

echo ""
echo "🎉 グローバルインストール完了！"
echo ""
echo "使用方法:"
echo "  autoqiita monitor .                    # 現在のディレクトリを監視"
echo "  autoqiita workspace add . --name 'MyProject'  # ワークスペース追加"
echo "  autoqiita server                       # MCPサーバー起動"
echo ""