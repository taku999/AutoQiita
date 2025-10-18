# AutoQiita便利エイリアス設定

# ~/.bashrc または ~/.zshrc に追加してください

# AutoQiitaのベースディレクトリ
export AUTOQIITA_HOME="/home/bell999/github/AutoQiita"

# AutoQiitaコマンドのエイリアス
alias autoqiita="cd $AUTOQIITA_HOME && uv run autoqiita"
alias aq="cd $AUTOQIITA_HOME && uv run autoqiita"

# よく使うコマンドのショートカット
alias aq-add="cd $AUTOQIITA_HOME && uv run autoqiita workspace add"
alias aq-list="cd $AUTOQIITA_HOME && uv run autoqiita workspace list"
alias aq-server="cd $AUTOQIITA_HOME && uv run autoqiita server"
alias aq-monitor="cd $AUTOQIITA_HOME && uv run autoqiita monitor"
alias aq-save="cd $AUTOQIITA_HOME && uv run autoqiita save"

# 使用例:
# aq-add /path/to/project --name "ProjectName"
# aq-list
# aq-server