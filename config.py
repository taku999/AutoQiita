"""
Configuration management for AutoQiita
"""
import os
from typing import List, Set
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Configuration for AutoQiita"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Qiita settings
        self.qiita_token = os.getenv("QIITA_ACCESS_TOKEN")
        if not self.qiita_token:
            raise ValueError("QIITA_ACCESS_TOKEN environment variable is required")
        
        # Workspace settings
        self.workspace_path = os.getenv("WORKSPACE_PATH", os.getcwd())
        
        # File monitoring settings - load from extension manager
        self._load_watched_extensions()
        
        self.ignore_patterns = [
            ".git", "__pycache__", "node_modules", ".vscode", 
            ".pytest_cache", ".mypy_cache", "dist", "build",
            ".env", ".env.local", "*.log", "*.tmp"
        ]
        
        # MCP server settings
        self.mcp_host = os.getenv("MCP_HOST", "localhost")
        self.mcp_port = int(os.getenv("MCP_PORT", "8000"))
        
        # Auto-save settings
        self.auto_save_enabled = os.getenv("AUTO_SAVE_ENABLED", "true").lower() == "true"
        self.save_delay_seconds = int(os.getenv("SAVE_DELAY_SECONDS", "5"))
        
        # Security settings
        self.security_scan_enabled = os.getenv("SECURITY_SCAN_ENABLED", "true").lower() == "true"
        self.security_block_critical = os.getenv("SECURITY_BLOCK_CRITICAL", "true").lower() == "true"
        self.security_config_file = os.getenv("SECURITY_CONFIG_FILE", "config/security_rules.json")
        
        # Qiita draft settings
        self.default_tags = [
            {"name": "備忘録", "versions": []},
            {"name": "VSCode", "versions": []}
        ]
        
        self.draft_prefix = os.getenv("DRAFT_PREFIX", "[AutoSave]")
    
    def _load_watched_extensions(self):
        """Load watched extensions from extension manager"""
        try:
            from .extension_manager import FileExtensionManager
            manager = FileExtensionManager()
            self.watched_extensions = manager.list_extensions()
        except Exception:
            # Fallback to default extensions
            self.watched_extensions = [
                ".md", ".py", ".js", ".ts", ".txt", ".rst", ".json", ".yaml", ".yml"
            ]
    
    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return {
            "workspace_path": self.workspace_path,
            "watched_extensions": self.watched_extensions,
            "ignore_patterns": self.ignore_patterns,
            "mcp_host": self.mcp_host,
            "mcp_port": self.mcp_port,
            "auto_save_enabled": self.auto_save_enabled,
            "save_delay_seconds": self.save_delay_seconds,
            "default_tags": self.default_tags,
            "draft_prefix": self.draft_prefix
        }