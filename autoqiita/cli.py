"""
CLI interface for AutoQiita
"""
import click
import asyncio
from pathlib import Path
from .config import Config
from .mcp_server import AutoQiitaMCPServer
from .qiita_client import QiitaClient
from .content_processor import ContentProcessor
from .multi_workspace import MultiWorkspaceConfig
from .extension_manager import FileExtensionManager

@click.group()
def cli():
    """AutoQiita - VSCode to Qiita Auto-Save System"""
    pass

@cli.command()
@click.option("--host", default="localhost", help="Host to bind MCP server")
@click.option("--port", default=8000, help="Port to bind MCP server")
def server(host, port):
    """Start the MCP server"""
    try:
        config = Config()
        server = AutoQiitaMCPServer(config)
        server.run(host=host, port=port)
    except Exception as e:
        click.echo(f"Error starting server: {e}")

@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--force", is_flag=True, help="Force upload even with security issues")
@click.option("--no-security-check", is_flag=True, help="Skip security check")
@click.option("--simple", is_flag=True, help="Simple creation without duplicate checking")
def save(file_path, force, no_security_check, simple):
    """Manually save a file to Qiita"""
    try:
        config = Config()
        qiita_client = QiitaClient(config.qiita_token)
        processor = ContentProcessor(enable_security_scan=not no_security_check)
        
        # Process file with security check
        title, body, tags, security_report = processor.process_file(file_path)
        
        # Display security report if issues found
        if security_report and security_report.get("total_issues", 0) > 0:
            from .security_scanner import SecurityScanner
            scanner = SecurityScanner()
            report_text = scanner.format_report_for_display(security_report)
            click.echo(report_text)
            
            # Check if upload should be blocked
            if processor.should_block_upload(security_report) and not force:
                click.echo("\n❌ アップロードがブロックされました。")
                click.echo("--force フラグを使用して強制アップロードできますが、推奨されません。")
                return
            
            # Ask for confirmation if not forcing
            if not force and security_report.get("total_issues", 0) > 0:
                if not click.confirm("\nセキュリティ問題が検出されましたが、続行しますか？"):
                    click.echo("アップロードをキャンセルしました。")
                    return
            
            # Add security warning to content
            body = processor.add_security_warning_to_content(body, security_report)
        
        # Save to Qiita
        if simple:
            # Simple creation without duplicate checking
            result = qiita_client.create_draft_simple(title, body, tags)
        else:
            # Standard creation with duplicate checking
            result = qiita_client.find_or_create_draft(title, body, tags, security_report, force)
        
        click.echo(f"✓ Saved to Qiita: {title}")
        click.echo(f"  ID: {result.get('id')}")
        click.echo(f"  URL: {result.get('url')}")
        
        if security_report and security_report.get("total_issues", 0) > 0:
            click.echo("  ⚠️ セキュリティ警告が記事に追加されました")
        
    except Exception as e:
        click.echo(f"Error saving file: {e}")

@cli.command()
def status():
    """Check system status"""
    try:
        config = Config()
        click.echo("AutoQiita Configuration:")
        click.echo(f"  Workspace: {config.workspace_path}")
        click.echo(f"  Watched extensions: {', '.join(config.watched_extensions)}")
        click.echo(f"  Auto-save: {'enabled' if config.auto_save_enabled else 'disabled'}")
        click.echo(f"  MCP Server: {config.mcp_host}:{config.mcp_port}")
        
        # Show registered workspaces
        multi_config = MultiWorkspaceConfig()
        workspaces = multi_config.get_enabled_workspaces()
        if workspaces:
            click.echo(f"  Registered workspaces: {len(workspaces)}")
            for ws in workspaces:
                status = "✓" if ws.get("enabled") else "✗"
                click.echo(f"    {status} {ws['name']}: {ws['path']}")
        
        # Test Qiita connection
        qiita_client = QiitaClient(config.qiita_token)
        items = qiita_client.list_user_items(per_page=1)
        click.echo(f"  Qiita: connected (found {len(items)} items)")
        
    except Exception as e:
        click.echo(f"Error checking status: {e}")

@cli.command()
@click.argument("workspace_path", type=click.Path(exists=True, file_okay=False))
def monitor(workspace_path):
    """Start monitoring a workspace (standalone mode)"""
    from .file_monitor import FileMonitor
    
    config = Config()
    config.workspace_path = workspace_path
    
    qiita_client = QiitaClient(config.qiita_token)
    processor = ContentProcessor()
    
    def on_file_changed(file_path):
        try:
            click.echo(f"Processing: {file_path}")
            title, body, tags = processor.process_file(file_path)
            result = qiita_client.find_or_create_draft(title, body, tags)
            click.echo(f"✓ Saved: {title} (ID: {result.get('id')})")
        except Exception as e:
            click.echo(f"✗ Error: {e}")
    
    click.echo(f"Starting file monitor for: {workspace_path}")
    click.echo("Press Ctrl+C to stop...")
    
    with FileMonitor(workspace_path, on_file_changed):
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo("\nStopping monitor...")

@cli.group()
def workspace():
    """Manage monitored workspaces"""
    pass

@workspace.command("add")
@click.argument("path", type=click.Path(exists=True, file_okay=False))
@click.option("--name", help="Workspace name (defaults to folder name)")
def add_workspace(path, name):
    """Add a workspace to monitor"""
    multi_config = MultiWorkspaceConfig()
    multi_config.add_workspace(path, name)
    
    workspace_name = name or Path(path).name
    click.echo(f"✓ Added workspace: {workspace_name} ({path})")

@workspace.command("remove")
@click.argument("path", type=click.Path())
def remove_workspace(path):
    """Remove a workspace from monitoring"""
    multi_config = MultiWorkspaceConfig()
    multi_config.remove_workspace(path)
    click.echo(f"✓ Removed workspace: {path}")

@workspace.command("list")
def list_workspaces():
    """List all registered workspaces"""
    multi_config = MultiWorkspaceConfig()
    workspaces = multi_config.workspaces
    
    if not workspaces:
        click.echo("No workspaces registered")
        return
    
    click.echo("Registered workspaces:")
    for ws in workspaces:
        status = "✓ enabled" if ws.get("enabled") else "✗ disabled"
        click.echo(f"  {ws['name']}: {ws['path']} ({status})")

@workspace.command("toggle")
@click.argument("path", type=click.Path())
def toggle_workspace(path):
    """Enable/disable a workspace"""
    multi_config = MultiWorkspaceConfig()
    multi_config.toggle_workspace(path)
    click.echo(f"✓ Toggled workspace: {path}")

@cli.group()
def security():
    """Security-related commands"""
    pass

@security.command("scan")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--config", help="Security config file path")
def scan_file(file_path, config):
    """Scan a file for security issues"""
    try:
        from .security_scanner import SecurityScanner
        
        scanner = SecurityScanner(config)
        issues = scanner.scan_file(file_path)
        report = scanner.get_security_report(issues)
        
        report_text = scanner.format_report_for_display(report)
        click.echo(report_text)
        
        # Set exit code based on severity
        if report["status"] == "critical":
            exit(2)
        elif report["status"] in ["high", "warning"]:
            exit(1)
        else:
            exit(0)
            
    except Exception as e:
        click.echo(f"Error scanning file: {e}")
        exit(1)

@security.command("check-config")
def check_security_config():
    """Check security configuration"""
    try:
        from .security_scanner import SecurityScanner
        
        config_file = "config/security_rules.json"
        if os.path.exists(config_file):
            scanner = SecurityScanner(config_file)
            click.echo(f"✅ Security config loaded: {config_file}")
            
            total_patterns = sum(len(patterns) for patterns in scanner.patterns.values())
            click.echo(f"  Total security patterns: {total_patterns}")
            
            for category, patterns in scanner.patterns.items():
                click.echo(f"  {category}: {len(patterns)} patterns")
        else:
            click.echo(f"⚠️ Security config not found: {config_file}")
            click.echo("Using default patterns")
            
    except Exception as e:
        click.echo(f"Error checking security config: {e}")

@cli.group()
def extensions():
    """Manage watched file extensions"""
    pass

@extensions.command("list")
def list_extensions():
    """List all watched file extensions"""
    try:
        manager = FileExtensionManager()
        extensions = manager.list_extensions()
        
        if not extensions:
            click.echo("監視対象の拡張子がありません")
            return
        
        click.echo(f"監視対象の拡張子: {len(extensions)}種類")
        for ext in extensions:
            desc = manager.extension_descriptions.get(ext, f"{ext} files")
            click.echo(f"  {ext} - {desc}")
            
    except Exception as e:
        click.echo(f"Error listing extensions: {e}")

@extensions.command("add")
@click.argument("extension", required=False)
def add_extension(extension):
    """Add file extension to watch list"""
    try:
        manager = FileExtensionManager()
        
        if extension:
            # Direct addition
            if manager.add_extension(extension):
                ext = extension if extension.startswith('.') else f'.{extension}'
                click.echo(f"✅ 追加しました: {ext}")
            else:
                ext = extension if extension.startswith('.') else f'.{extension}'
                click.echo(f"⚠️ 既に追加済み: {ext}")
        else:
            # Interactive mode
            manager.interactive_add()
            
    except Exception as e:
        click.echo(f"Error adding extension: {e}")

@extensions.command("remove")
@click.argument("extension", required=False)
def remove_extension(extension):
    """Remove file extension from watch list"""
    try:
        manager = FileExtensionManager()
        
        if extension:
            # Direct removal
            if manager.remove_extension(extension):
                ext = extension if extension.startswith('.') else f'.{extension}'
                click.echo(f"✅ 削除しました: {ext}")
            else:
                ext = extension if extension.startswith('.') else f'.{extension}'
                click.echo(f"❌ 見つかりません: {ext}")
        else:
            # Interactive mode
            manager.interactive_remove()
            
    except Exception as e:
        click.echo(f"Error removing extension: {e}")

@extensions.command("suggest")
@click.argument("keyword")
def suggest_extensions(keyword):
    """Suggest extensions based on keyword"""
    try:
        manager = FileExtensionManager()
        suggestions = manager.suggest_extensions(keyword)
        
        if not suggestions:
            click.echo(f"'{keyword}' に関連する拡張子が見つかりませんでした")
            return
        
        click.echo(f"'{keyword}' に関連する拡張子:")
        for ext in suggestions:
            desc = manager.extension_descriptions.get(ext, f"{ext} files")
            status = "✓" if ext in manager.watched_extensions else " "
            click.echo(f"  [{status}] {ext} - {desc}")
            
    except Exception as e:
        click.echo(f"Error suggesting extensions: {e}")

@extensions.command("reset")
def reset_extensions():
    """Reset to default extensions"""
    try:
        manager = FileExtensionManager()
        
        if click.confirm("デフォルトの拡張子にリセットしますか？"):
            manager.watched_extensions = manager.default_extensions.copy()
            manager.save_extensions()
            click.echo("✅ デフォルトの拡張子にリセットしました")
            
            click.echo("現在の監視対象:")
            for ext in manager.list_extensions():
                desc = manager.extension_descriptions.get(ext, f"{ext} files")
                click.echo(f"  {ext} - {desc}")
        else:
            click.echo("キャンセルしました")
            
    except Exception as e:
        click.echo(f"Error resetting extensions: {e}")

if __name__ == "__main__":
    cli()