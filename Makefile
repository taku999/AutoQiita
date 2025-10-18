# Makefile for AutoQiita with uv

.PHONY: setup install dev test format lint clean server monitor help end stop

# デフォルトターゲット
help: ## このヘルプを表示
	@echo "AutoQiita - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## 初回セットアップを実行
	@echo "🚀 AutoQiita セットアップを開始..."
	./setup.sh

end: ## システムを終了・クリーンアップ
	@echo "🛑 AutoQiita システムを終了..."
	./end.sh

stop: ## 実行中のプロセスのみ停止（クリーンアップなし）
	@echo "⏹️  AutoQiitaプロセスを停止中..."
	@pkill -f "autoqiita server" 2>/dev/null || true
	@pkill -f "autoqiita monitor" 2>/dev/null || true
	@pkill -f "uvicorn.*autoqiita" 2>/dev/null || true
	@echo "✅ プロセスを停止しました"

install: ## 依存関係をインストール
	uv sync

dev: ## 開発用依存関係もインストール
	uv sync --group dev

test: ## テストを実行
	uv sync --group test
	uv run pytest

format: ## コードをフォーマット
	uv sync --group lint
	uv run black autoqiita tests
	uv run isort autoqiita tests

lint: ## 静的解析を実行
	uv sync --group lint
	uv run flake8 autoqiita
	uv run mypy autoqiita

clean: ## 一時ファイルを削除
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/

server: ## MCPサーバーを起動
	uv run autoqiita server

monitor: ## 現在のディレクトリを監視
	uv run autoqiita monitor .

status: ## システム状態を確認
	uv run autoqiita status

workspace-add: ## 現在のディレクトリをワークスペースに追加
	uv run autoqiita workspace add . --name "$(shell basename $(PWD))"

workspace-list: ## 登録済みワークスペースを一覧表示
	uv run autoqiita workspace list

build-vscode: ## VSCode拡張機能をビルド
	cd vscode_extension && npm install && npm run compile

security-scan: ## セキュリティスキャンを実行
	@echo "🔍 セキュリティスキャンを実行中..."
	find . -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.md" | head -10 | xargs -I {} uv run autoqiita security scan {}

security-check-config: ## セキュリティ設定を確認
	uv run autoqiita security check-config

extensions-list: ## 監視対象拡張子を一覧表示
	uv run autoqiita extensions list

extensions-add: ## 監視対象拡張子を追加（インタラクティブ）
	uv run autoqiita extensions add

article-save: ## 作成した記事をQiitaに保存
	uv run autoqiita save article_draft.md

article-save-simple: ## 作成した記事をQiitaに保存（重複チェック無し）
	uv run autoqiita save article_draft.md --simple

article-scan: ## 記事のセキュリティスキャンのみ実行
	uv run autoqiita security scan article_draft.md

# 開発用のクイックコマンド
quick-start: workspace-add server ## ワークスペース追加 + サーバー起動

# CI/CD用
ci: dev lint test security-check-config ## CI用：依存関係インストール + リント + テスト + セキュリティ設定確認