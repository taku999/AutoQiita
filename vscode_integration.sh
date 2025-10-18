#!/bin/bash

# AutoQiita VSCode統合スクリプト
# VSCodeの統合ターミナルでどのプロジェクトからでも簡単にAutoQiitaを使えるようにします

# 現在のファイルをQiitaに保存
autoqiita_save_current() {
    if [ $# -eq 0 ]; then
        echo "❌ ファイルパスを指定してください"
        echo "使用例: autoqiita_save_current file.md"
        return 1
    fi
    
    local current_dir="$(pwd)"
    local file_path="$1"
    
    # 相対パスを絶対パスに変換
    if [[ ! "$file_path" = /* ]]; then
        file_path="$current_dir/$file_path"
    fi
    
    echo "📝 ファイルをQiitaに保存中: $file_path"
    (cd "/home/bell999/github/AutoQiita" && uv run autoqiita save "$file_path")
    cd "$current_dir"
}

# 現在のディレクトリをワークスペースに追加
autoqiita_add_here() {
    local workspace_name="${1:-$(basename $(pwd))}"
    local current_dir="$(pwd)"
    
    echo "📁 現在のディレクトリをワークスペースに追加: $workspace_name"
    (cd "/home/bell999/github/AutoQiita" && uv run autoqiita workspace add "$current_dir" --name "$workspace_name")
    cd "$current_dir"
}

# AutoQiitaサーバーのステータス確認
autoqiita_check() {
    local current_dir="$(pwd)"
    echo "🔍 AutoQiitaシステム状態:"
    (cd "/home/bell999/github/AutoQiita" && uv run autoqiita status)
    echo ""
    echo "📋 登録済みワークスペース:"
    (cd "/home/bell999/github/AutoQiita" && uv run autoqiita workspace list)
    cd "$current_dir"
}

# エイリアスを設定
alias aqs='autoqiita_save_current'      # クイック保存
alias aqa='autoqiita_add_here'          # ワークスペース追加
alias aqc='autoqiita_check'             # 状態確認
alias aqh='autoqiita --help'            # ヘルプ

echo "🎉 AutoQiita VSCode統合機能を有効化しました！"
echo ""
echo "📋 使用可能なコマンド:"
echo "  aqs file.md        - ファイルをQiitaに保存"
echo "  aqa [名前]         - 現在のディレクトリをワークスペースに追加"
echo "  aqc                - システム状態確認"
echo "  aqh                - ヘルプ表示"
echo "  autoqiita          - フルコマンド"