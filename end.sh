#!/bin/bash
# 終了・クリーンアップスクリプト for AutoQiita

set -e

echo "🛑 AutoQiita システムを終了・クリーンアップします..."

# 実行中のプロセスを確認・終了
echo "⚠️  実行中のAutoQiitaプロセスを確認中..."

# MCPサーバーのプロセスを確認
AUTOQIITA_PIDS=$(pgrep -f "autoqiita server" 2>/dev/null || true)
if [ ! -z "$AUTOQIITA_PIDS" ]; then
    echo "🔄 AutoQiita MCPサーバーを終了中..."
    echo "$AUTOQIITA_PIDS" | xargs kill -TERM 2>/dev/null || true
    sleep 2
    # まだ残っている場合は強制終了
    REMAINING_PIDS=$(pgrep -f "autoqiita server" 2>/dev/null || true)
    if [ ! -z "$REMAINING_PIDS" ]; then
        echo "💀 強制終了中..."
        echo "$REMAINING_PIDS" | xargs kill -KILL 2>/dev/null || true
    fi
    echo "✅ MCPサーバーを終了しました"
else
    echo "✅ MCPサーバーは実行されていません"
fi

# モニタープロセスを確認
MONITOR_PIDS=$(pgrep -f "autoqiita monitor" 2>/dev/null || true)
if [ ! -z "$MONITOR_PIDS" ]; then
    echo "🔄 AutoQiitaモニターを終了中..."
    echo "$MONITOR_PIDS" | xargs kill -TERM 2>/dev/null || true
    sleep 2
    echo "✅ モニターを終了しました"
else
    echo "✅ モニターは実行されていません"
fi

# uvicornプロセスを確認（MCPサーバーのバックエンド）
UVICORN_PIDS=$(pgrep -f "uvicorn.*autoqiita" 2>/dev/null || true)
if [ ! -z "$UVICORN_PIDS" ]; then
    echo "🔄 Uvicornサーバーを終了中..."
    echo "$UVICORN_PIDS" | xargs kill -TERM 2>/dev/null || true
    sleep 2
    echo "✅ Uvicornサーバーを終了しました"
fi

# 仮想環境の無効化
if [ "$VIRTUAL_ENV" ]; then
    echo "🐍 仮想環境を無効化中..."
    deactivate 2>/dev/null || true
    echo "✅ 仮想環境を無効化しました"
else
    echo "✅ 仮想環境は有効になっていません"
fi

# 選択的クリーンアップ（ユーザー確認付き）
echo ""
echo "🧹 クリーンアップオプション:"
echo "以下の項目をクリーンアップしますか？"

# 一時ファイルのクリーンアップ
read -p "1. 一時ファイル（__pycache__、*.pyc等）を削除しますか？ [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  一時ファイルを削除中..."
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ 2>/dev/null || true
    echo "✅ 一時ファイルを削除しました"
fi

# ログファイルのクリーンアップ
read -p "2. ログファイル（*.log）を削除しますか？ [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📝 ログファイルを削除中..."
    find . -name "*.log" -delete 2>/dev/null || true
    echo "✅ ログファイルを削除しました"
fi

# 仮想環境の削除
read -p "3. 仮想環境（.venv）を削除しますか？ [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗂️  仮想環境を削除中..."
    rm -rf .venv/ 2>/dev/null || true
    echo "✅ 仮想環境を削除しました"
fi

# VSCode拡張機能のnode_modules削除
if [ -d "vscode_extension/node_modules" ]; then
    read -p "4. VSCode拡張機能のnode_modulesを削除しますか？ [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 node_modulesを削除中..."
        rm -rf vscode_extension/node_modules/ 2>/dev/null || true
        rm -rf vscode_extension/out/ 2>/dev/null || true
        echo "✅ node_modulesを削除しました"
    fi
fi

# 設定ファイルの削除確認（危険な操作）
echo ""
echo "⚠️  危険な操作:"
read -p "5. 設定ファイル（.env、workspaces.json）を削除しますか？ [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  設定ファイルを削除中..."
    rm -f .env 2>/dev/null || true
    rm -f workspaces.json 2>/dev/null || true
    echo "✅ 設定ファイルを削除しました"
    echo "⚠️  注意: 次回setup.shを実行する際は、.envファイルを再設定する必要があります"
fi

# ポート確認とプロセス終了の最終確認
echo ""
echo "🔍 ポート8000の使用状況を確認中..."
PORT_8000_PID=$(lsof -ti:8000 2>/dev/null || true)
if [ ! -z "$PORT_8000_PID" ]; then
    echo "⚠️  ポート8000がまだ使用されています (PID: $PORT_8000_PID)"
    read -p "ポート8000を使用しているプロセスを終了しますか？ [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill -TERM "$PORT_8000_PID" 2>/dev/null || true
        sleep 2
        echo "✅ ポート8000を解放しました"
    fi
else
    echo "✅ ポート8000は使用されていません"
fi

echo ""
echo "🎉 AutoQiitaシステムの終了・クリーンアップが完了しました！"
echo ""
echo "システムを再開するには:"
echo "  ./setup.sh        # 再セットアップ"
echo "  make quick-start   # クイックスタート"
echo ""