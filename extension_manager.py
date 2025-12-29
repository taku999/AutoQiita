"""
Interactive file extension manager for AutoQiita
"""
import json
import click
from typing import List, Set
from pathlib import Path
import os

class FileExtensionManager:
    """Manage watched file extensions"""
    
    def __init__(self, config_file: str = "config/watched_extensions.json"):
        self.config_file = config_file
        self.default_extensions = {
            '.md', '.py', '.js', '.ts', '.txt', '.rst', 
            '.json', '.yaml', '.yml', '.html', '.css', '.scss'
        }
        self.extension_descriptions = {
            '.md': 'Markdown files',
            '.py': 'Python files',
            '.js': 'JavaScript files',
            '.ts': 'TypeScript files',  
            '.tsx': 'TypeScript React files',
            '.jsx': 'JavaScript React files',
            '.txt': 'Text files',
            '.rst': 'reStructuredText files',
            '.json': 'JSON files',
            '.yaml': 'YAML files',
            '.yml': 'YAML files',
            '.html': 'HTML files',
            '.css': 'CSS files',
            '.scss': 'SCSS files',
            '.go': 'Go files',
            '.rs': 'Rust files',
            '.java': 'Java files',
            '.cpp': 'C++ files',
            '.c': 'C files',
            '.h': 'Header files',
            '.php': 'PHP files',
            '.rb': 'Ruby files',
            '.swift': 'Swift files',
            '.kt': 'Kotlin files',
            '.dart': 'Dart files',
            '.vue': 'Vue.js files',
            '.svelte': 'Svelte files',
            '.sql': 'SQL files',
            '.sh': 'Shell script files',
            '.bash': 'Bash script files',
            '.ps1': 'PowerShell files',
            '.dockerfile': 'Dockerfile',
            '.toml': 'TOML files',
            '.ini': 'INI files',
            '.xml': 'XML files',
            '.csv': 'CSV files'
        }
        self.load_extensions()
    
    def load_extensions(self) -> None:
        """Load watched extensions from config file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.watched_extensions = set(data.get("extensions", []))
                    if not self.watched_extensions:
                        self.watched_extensions = self.default_extensions.copy()
            except Exception as e:
                click.echo(f"Warning: Could not load config file: {e}")
                self.watched_extensions = self.default_extensions.copy()
        else:
            self.watched_extensions = self.default_extensions.copy()
            self.save_extensions()
    
    def save_extensions(self) -> None:
        """Save watched extensions to config file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        data = {
            "extensions": sorted(list(self.watched_extensions)),
            "descriptions": {ext: self.extension_descriptions.get(ext, f"{ext} files") 
                           for ext in self.watched_extensions}
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_extension(self, extension: str) -> bool:
        """Add a file extension to watch list"""
        # Normalize extension (ensure it starts with .)
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        if extension in self.watched_extensions:
            return False
        
        self.watched_extensions.add(extension)
        
        # Add description if not exists
        if extension not in self.extension_descriptions:
            self.extension_descriptions[extension] = f"{extension.upper()} files"
        
        self.save_extensions()
        return True
    
    def remove_extension(self, extension: str) -> bool:
        """Remove a file extension from watch list"""
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        if extension not in self.watched_extensions:
            return False
        
        self.watched_extensions.remove(extension)
        self.save_extensions()
        return True
    
    def list_extensions(self) -> List[str]:
        """Get list of watched extensions"""
        return sorted(list(self.watched_extensions))
    
    def suggest_extensions(self, keyword: str) -> List[str]:
        """Suggest extensions based on keyword"""
        keyword = keyword.lower()
        suggestions = []
        
        # Direct matches
        for ext, desc in self.extension_descriptions.items():
            if keyword in ext.lower() or keyword in desc.lower():
                suggestions.append(ext)
        
        # Special keyword mappings
        keyword_mappings = {
            'react': ['.jsx', '.tsx'],
            'vue': ['.vue'],
            'angular': ['.ts', '.html', '.scss'],
            'node': ['.js', '.ts', '.json'],
            'python': ['.py'],
            'rust': ['.rs'],
            'go': ['.go'], 
            'java': ['.java'],
            'web': ['.html', '.css', '.js'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini'],
            'script': ['.sh', '.bash', '.ps1'],
            'database': ['.sql'],
            'docker': ['.dockerfile']
        }
        
        if keyword in keyword_mappings:
            suggestions.extend(keyword_mappings[keyword])
        
        # Remove duplicates and sort
        return sorted(list(set(suggestions)))
    
    def interactive_add(self) -> None:
        """Interactive extension addition"""
        click.echo("🔍 監視対象ファイルを追加します")
        click.echo("現在の監視対象:")
        for ext in self.list_extensions():
            desc = self.extension_descriptions.get(ext, f"{ext} files")
            click.echo(f"  {ext} - {desc}")
        
        click.echo("\n💡 キーワード例: react, vue, python, web, config, etc.")
        
        while True:
            user_input = click.prompt(
                "\n追加したい拡張子またはキーワードを入力してください (終了: quit)",
                type=str
            ).strip()
            
            if user_input.lower() in ['quit', 'q', 'exit']:
                break
            
            if not user_input:
                continue
            
            # Try direct extension addition
            if user_input.startswith('.') or len(user_input.split('.')) == 2:
                if self.add_extension(user_input):
                    ext = user_input if user_input.startswith('.') else f'.{user_input}'
                    click.echo(f"✅ 追加しました: {ext}")
                else:
                    ext = user_input if user_input.startswith('.') else f'.{user_input}'
                    click.echo(f"⚠️ 既に追加済み: {ext}")
                continue
            
            # Suggest extensions
            suggestions = self.suggest_extensions(user_input)
            if not suggestions:
                # Allow custom extension
                custom_ext = f'.{user_input}'
                if click.confirm(f"カスタム拡張子 '{custom_ext}' を追加しますか？"):
                    if self.add_extension(custom_ext):
                        click.echo(f"✅ 追加しました: {custom_ext}")
                continue
            
            click.echo(f"\n'{user_input}' に関連する拡張子:")
            for i, ext in enumerate(suggestions, 1):
                desc = self.extension_descriptions.get(ext, f"{ext} files")
                status = "✓" if ext in self.watched_extensions else " "
                click.echo(f"  {i}. [{status}] {ext} - {desc}")
            
            click.echo("  a. すべて追加")
            click.echo("  s. スキップ")
            
            choice = click.prompt("選択してください", type=str).strip().lower()
            
            if choice == 'a':
                # Add all suggestions
                added = []
                for ext in suggestions:
                    if self.add_extension(ext):
                        added.append(ext)
                if added:
                    click.echo(f"✅ 追加しました: {', '.join(added)}")
                else:
                    click.echo("⚠️ すべて既に追加済みです")
            elif choice == 's':
                continue
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(suggestions):
                    ext = suggestions[idx]
                    if self.add_extension(ext):
                        click.echo(f"✅ 追加しました: {ext}")
                    else:
                        click.echo(f"⚠️ 既に追加済み: {ext}")
                else:
                    click.echo("❌ 無効な選択です")
            else:
                click.echo("❌ 無効な選択です")
        
        click.echo(f"\n🎉 現在の監視対象: {len(self.watched_extensions)}種類")
        for ext in self.list_extensions():
            desc = self.extension_descriptions.get(ext, f"{ext} files")
            click.echo(f"  {ext} - {desc}")
    
    def interactive_remove(self) -> None:
        """Interactive extension removal"""
        extensions = self.list_extensions()
        if not extensions:
            click.echo("監視対象の拡張子がありません")
            return
        
        click.echo("🗑️ 監視対象から削除する拡張子を選択してください:")
        for i, ext in enumerate(extensions, 1):
            desc = self.extension_descriptions.get(ext, f"{ext} files")
            click.echo(f"  {i}. {ext} - {desc}")
        
        click.echo("  a. すべて削除")
        click.echo("  c. キャンセル")
        
        choice = click.prompt("選択してください", type=str).strip().lower()
        
        if choice == 'c':
            click.echo("キャンセルしました")
            return
        elif choice == 'a':
            if click.confirm("すべての拡張子を削除しますか？"):
                self.watched_extensions.clear()
                self.save_extensions()
                click.echo("✅ すべての拡張子を削除しました")
            return
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(extensions):
                ext = extensions[idx]
                if self.remove_extension(ext):
                    click.echo(f"✅ 削除しました: {ext}")
                else:
                    click.echo(f"❌ 削除に失敗しました: {ext}")
            else:
                click.echo("❌ 無効な選択です")
        else:
            click.echo("❌ 無効な選択です")