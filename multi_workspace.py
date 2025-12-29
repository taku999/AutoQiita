"""
Multi-workspace configuration for AutoQiita
"""
import json
import os
from typing import List, Dict
from pathlib import Path

class MultiWorkspaceConfig:
    """Configuration for monitoring multiple workspaces"""
    
    def __init__(self, config_file: str = "workspaces.json"):
        self.config_file = config_file
        self.workspaces = self.load_workspaces()
    
    def load_workspaces(self) -> List[Dict[str, any]]:
        """Load workspace configurations"""
        if not os.path.exists(self.config_file):
            return []
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("workspaces", [])
        except Exception:
            return []
    
    def save_workspaces(self):
        """Save workspace configurations"""
        data = {"workspaces": self.workspaces}
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_workspace(self, path: str, name: str = None, enabled: bool = True):
        """Add a workspace to monitor"""
        if not name:
            name = Path(path).name
        
        workspace = {
            "name": name,
            "path": str(Path(path).resolve()),
            "enabled": enabled,
            "watched_extensions": [".md", ".py", ".js", ".ts", ".txt", ".rst"],
            "ignore_patterns": [".git", "__pycache__", "node_modules", ".vscode"],
            "qiita_tags": [{"name": f"{name}-project", "versions": []}]
        }
        
        # Remove existing workspace with same path
        self.workspaces = [w for w in self.workspaces if w["path"] != workspace["path"]]
        
        self.workspaces.append(workspace)
        self.save_workspaces()
    
    def remove_workspace(self, path: str):
        """Remove a workspace from monitoring"""
        self.workspaces = [w for w in self.workspaces if w["path"] != str(Path(path).resolve())]
        self.save_workspaces()
    
    def get_enabled_workspaces(self) -> List[Dict[str, any]]:
        """Get all enabled workspaces"""
        return [w for w in self.workspaces if w.get("enabled", True)]
    
    def toggle_workspace(self, path: str, enabled: bool = None):
        """Enable or disable a workspace"""
        path = str(Path(path).resolve())
        for workspace in self.workspaces:
            if workspace["path"] == path:
                if enabled is None:
                    workspace["enabled"] = not workspace.get("enabled", True)
                else:
                    workspace["enabled"] = enabled
                break
        self.save_workspaces()