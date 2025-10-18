# AutoQiita便利エイリアス設定

# ~/.bashrc または ~/.zshrc に追加してください:
# source /path/to/AutoQiita/shell_aliases.sh

# 💡 重要: このバージョンはコマンド実行後に元のディレクトリに戻ります

# AutoQiitaのベースディレクトリ
export AUTOQIITA_HOME="/home/bell999/github/AutoQiita"

# AutoQiitaコマンドの関数版（確実に元のディレクトリに戻る）
autoqiita() {
    local current_dir="$(pwd)"
    (cd "$AUTOQIITA_HOME" && uv run autoqiita "$@")
    cd "$current_dir"
}

aq() {
    local current_dir="$(pwd)"
    (cd "$AUTOQIITA_HOME" && uv run autoqiita "$@")
    cd "$current_dir"
}

# よく使うコマンドのショートカット（関数版）
aq-add() {
    local current_dir="$(pwd)"
    (cd "$AUTOQIITA_HOME" && uv run autoqiita workspace add "$@")
    cd "$current_dir"
}

aq-list() {
    local current_dir="$(pwd)"
    (cd "$AUTOQIITA_HOME" && uv run autoqiita workspace list "$@")
    cd "$current_dir"
}

aq-server() {
    local current_dir="$(pwd)"
    echo "🚀 AutoQiitaサーバーを開始中..."
    echo "📁 元のディレクトリ: $current_dir"
    (cd "$AUTOQIITA_HOME" && uv run autoqiita server "$@")
}

aq-monitor() {
    local current_dir="$(pwd)"
    (cd "$AUTOQIITA_HOME" && uv run autoqiita monitor "$@")
    cd "$current_dir"
}

aq-save() {
    local current_dir="$(pwd)"
    (cd "$AUTOQIITA_HOME" && uv run autoqiita save "$@")
    cd "$current_dir"
}

# 関数ベースのコマンド（より確実なパラメータ渡し）
aq_workspace_add() {
    local current_dir="$(pwd)"
    (cd "$AUTOQIITA_HOME" && uv run autoqiita workspace add "$@")
    cd "$current_dir"
}

aq_workspace_list() {
    local current_dir="$(pwd)"
    (cd "$AUTOQIITA_HOME" && uv run autoqiita workspace list "$@")
    cd "$current_dir"
}

aq_save_file() {
    local current_dir="$(pwd)"
    (cd "$AUTOQIITA_HOME" && uv run autoqiita save "$@")
    cd "$current_dir"
}

aq_status() {
    local current_dir="$(pwd)"
    (cd "$AUTOQIITA_HOME" && uv run autoqiita status "$@")
    cd "$current_dir"
}

aq_server_start() {
    local current_dir="$(pwd)"
    echo "🚀 AutoQiitaサーバーを開始中..."
    echo "📁 元のディレクトリ: $current_dir"
    (cd "$AUTOQIITA_HOME" && uv run autoqiita server "$@")
}

# 使用例:
# 
# どのディレクトリからでも実行可能（元のディレクトリに自動で戻ります）:
# cd /any/project/directory
# aq-list                           # ワークスペース一覧（元の場所に戻る）
# aq-add . --name "MyProject"       # 現在のディレクトリを追加（元の場所に戻る）
# aq-save README.md                 # ファイルを保存（元の場所に戻る）
# aq-server                         # サーバー起動（サーバー終了後、元の場所に戻る）
# 
# または関数版:
# aq_workspace_add /path/to/project --name "ProjectName"
# aq_workspace_list
# aq_save_file file.md
#
# ✅ 修正済み: 全てのコマンドが元のディレクトリに戻るようになりました！