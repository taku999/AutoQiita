#!/bin/bash

# AutoQiita エイリアステストスクリプト
# 各コマンドが正しく元のディレクトリに戻ることを確認

echo "🧪 AutoQiita エイリアス動作テスト"
echo "================================="

# 現在のディレクトリを保存
ORIGINAL_DIR="$(pwd)"
echo "📁 開始ディレクトリ: $ORIGINAL_DIR"

# テスト用の一時ディレクトリを作成
TEST_DIR="/tmp/autoqiita_test_$$"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo ""
echo "📂 テストディレクトリに移動: $(pwd)"
echo ""

# エイリアス設定を読み込み
echo "🔧 エイリアス設定を読み込み中..."
source "$ORIGINAL_DIR/shell_aliases.sh"

echo ""
echo "🧪 テスト1: aq-list コマンド"
echo "現在のディレクトリ（実行前）: $(pwd)"
aq-list
echo "現在のディレクトリ（実行後）: $(pwd)"

if [ "$(pwd)" = "$TEST_DIR" ]; then
    echo "✅ テスト1: 成功 - 元のディレクトリに戻りました"
else
    echo "❌ テスト1: 失敗 - ディレクトリが変更されました"
fi

echo ""
echo "🧪 テスト2: aq_workspace_list 関数"
echo "現在のディレクトリ（実行前）: $(pwd)"
aq_workspace_list
echo "現在のディレクトリ（実行後）: $(pwd)"

if [ "$(pwd)" = "$TEST_DIR" ]; then
    echo "✅ テスト2: 成功 - 元のディレクトリに戻りました"
else
    echo "❌ テスト2: 失敗 - ディレクトリが変更されました"
fi

echo ""
echo "🧪 テスト3: aq_status 関数"
echo "現在のディレクトリ（実行前）: $(pwd)"
aq_status
echo "現在のディレクトリ（実行後）: $(pwd)"

if [ "$(pwd)" = "$TEST_DIR" ]; then
    echo "✅ テスト3: 成功 - 元のディレクトリに戻りました"
else
    echo "❌ テスト3: 失敗 - ディレクトリが変更されました"
fi

# クリーンアップ
cd "$ORIGINAL_DIR"
rm -rf "$TEST_DIR"

echo ""
echo "🎉 テスト完了！"
echo "📁 最終ディレクトリ: $(pwd)"

if [ "$(pwd)" = "$ORIGINAL_DIR" ]; then
    echo "✅ 全体テスト: 成功 - 元のディレクトリに戻りました"
else
    echo "❌ 全体テスト: 失敗 - 予期しない場所にいます"
fi