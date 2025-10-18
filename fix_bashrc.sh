#!/bin/bash

# AutoQiita .bashrc設定自動修正スクリプト
# .bashrcファイルのパスの問題を修正し、正しいAutoQiita設定を追加します

AUTOQIITA_DIR="/home/bell999/github/AutoQiita"
BASHRC_FILE="$HOME/.bashrc"

echo "🔧 AutoQiita .bashrc設定を修正中..."

# 現在の設定をバックアップ
if [ ! -f "${BASHRC_FILE}.autoqiita_backup" ]; then
    cp "$BASHRC_FILE" "${BASHRC_FILE}.autoqiita_backup"
    echo "📋 .bashrcをバックアップしました: ${BASHRC_FILE}.autoqiita_backup"
fi

# 古いAutoQiita設定を削除
echo "🧹 古い設定をクリーンアップ中..."
sed -i '/# AutoQiita/,/fi$/d' "$BASHRC_FILE"
sed -i '/shell_aliases\.sh/d' "$BASHRC_FILE" 
sed -i '/vscode_integration\.sh/d' "$BASHRC_FILE"

# 正しい設定を追加
echo "✅ 新しい設定を追加中..."
cat >> "$BASHRC_FILE" << EOF

# ==========================================
# AutoQiita - VSCode to Qiita Auto-Save System
# ==========================================

# AutoQiita Shell Aliases
if [ -f "$AUTOQIITA_DIR/shell_aliases.sh" ]; then
    source "$AUTOQIITA_DIR/shell_aliases.sh"
fi

# AutoQiita VSCode Integration
if [ -f "$AUTOQIITA_DIR/vscode_integration.sh" ]; then
    source "$AUTOQIITA_DIR/vscode_integration.sh"
fi

# ==========================================
EOF

echo ""
echo "🎉 設定完了！"
echo ""
echo "📋 追加された機能:"
echo "  ✅ AutoQiita Shell Aliases (aq-list, aq-add, etc.)"
echo "  ✅ AutoQiita VSCode Integration (aqs, aqa, aqc, etc.)"
echo ""
echo "💡 設定を反映するには以下を実行してください:"
echo "  source ~/.bashrc"
echo ""
echo "🔍 動作確認:"
echo "  aq-list      # ワークスペース一覧"
echo "  aqc          # システム状態確認"
echo ""

# 設定を自動で反映するか確認
read -p "今すぐ設定を反映しますか？ [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    source "$BASHRC_FILE"
    echo "✅ 設定が反映されました！"
else
    echo "⏳ 新しいターミナルまたは 'source ~/.bashrc' で設定が有効になります"
fi