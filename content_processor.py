"""
Content processor for converting various file types to Qiita-compatible markdown
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import markdown
import logging

from .security_scanner import SecurityScanner, SecurityIssue

logger = logging.getLogger(__name__)

class ContentProcessor:
    """Process file content for Qiita upload with security scanning"""
    
    def __init__(self, enable_security_scan: bool = True, security_config_file: str = None):
        self.processors = {
            '.md': self._process_markdown,
            '.py': self._process_python,
            '.js': self._process_javascript,
            '.ts': self._process_typescript,
            '.txt': self._process_text,
            '.rst': self._process_rst
        }
        self.enable_security_scan = enable_security_scan
        
        if enable_security_scan:
            config_path = security_config_file or "config/security_rules.json"
            self.security_scanner = SecurityScanner(config_path)
        else:
            self.security_scanner = None
    
    def process_file(self, file_path: str) -> Tuple[str, str, List[Dict[str, str]], Optional[Dict]]:
        """
        Process a file and return (title, body, tags, security_report)
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension not in self.processors:
            title, body, tags = self._process_generic(file_path)
        else:
            title, body, tags = self.processors[extension](file_path)
        
        # Perform security scan
        security_report = None
        if self.enable_security_scan and self.security_scanner:
            security_report = self._perform_security_scan(body, file_path)
        
        return title, body, tags, security_report
    
    def _perform_security_scan(self, content: str, file_path: str) -> Dict:
        """Perform security scan on content"""
        try:
            issues = self.security_scanner.scan_content(content, file_path)
            report = self.security_scanner.get_security_report(issues)
            
            logger.info(f"Security scan completed for {file_path}: {report['total_issues']} issues found")
            
            return report
        except Exception as e:
            logger.error(f"Security scan failed for {file_path}: {e}")
            return {
                "status": "error",
                "message": f"セキュリティスキャンでエラーが発生しました: {e}",
                "total_issues": 0
            }
    
    def should_block_upload(self, security_report: Optional[Dict]) -> bool:
        """Check if upload should be blocked based on security report"""
        if not security_report or not self.security_scanner:
            return False
        
        return security_report.get("status") == "critical"
    
    def add_security_warning_to_content(self, body: str, security_report: Dict) -> str:
        """Add security warning to content if issues found"""
        if not security_report or security_report.get("total_issues", 0) == 0:
            return body
        
        warning_section = self._generate_security_warning_section(security_report)
        
        # Add warning at the beginning of the content
        return f"{warning_section}\n\n{body}"
    
    def _generate_security_warning_section(self, security_report: Dict) -> str:
        """Generate security warning section for content"""
        if security_report.get("status") == "critical":
            warning_icon = "🚨"
            warning_level = "重要"
        elif security_report.get("status") == "high":
            warning_icon = "⚠️"
            warning_level = "注意"
        else:
            warning_icon = "💡"
            warning_level = "情報"
        
        warning = f"""
{warning_icon} **セキュリティ{warning_level}**

この記事には以下のセキュリティに関する項目が含まれています：

"""
        
        # Add issue summary
        if "by_category" in security_report:
            for category, count in security_report["by_category"].items():
                category_name = self._get_category_japanese_name(category)
                warning += f"- {category_name}: {count}件\n"
        
        warning += """
記事の内容を確認し、必要に応じて以下の対応を行ってください：
- 実際の認証情報やAPIキーが含まれていないか確認
- 個人情報（メールアドレス、電話番号等）の匿名化
- 危険なコード例には適切な警告を追加

---
"""
        
        return warning
    
    def _get_category_japanese_name(self, category: str) -> str:
        """Get Japanese name for security category"""
        category_names = {
            "credentials": "認証情報",
            "personal_info": "個人情報",
            "dangerous_code": "危険なコード",
            "web_security": "Webセキュリティ",
            "file_paths": "ファイルパス",
            "network_info": "ネットワーク情報"
        }
        return category_names.get(category, category)
    
    def _read_file_content(self, file_path: str) -> str:
        """Read file content with encoding detection"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='shift_jis') as f:
                return f.read()
    
    def _extract_title_from_content(self, content: str, filename: str) -> str:
        """Extract title from content or use filename"""
        lines = content.strip().split('\n')
        
        # Look for markdown title
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        
        # Look for docstring or comment title
        title_patterns = [
            r'^"""([^"]+)"""',  # Python docstring
            r'^/\*\*\s*([^*]+)\s*\*/',  # JS/TS comment
            r'^#\s*(.+)$',  # Comment line
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        # Use filename as fallback
        return Path(filename).stem.replace('_', ' ').replace('-', ' ').title()
    
    def _process_markdown(self, file_path: str) -> Tuple[str, str, List[Dict[str, str]]]:
        """Process markdown file"""
        content = self._read_file_content(file_path)
        title = self._extract_title_from_content(content, file_path)
        
        # Extract tags from front matter or content
        tags = self._extract_tags_from_content(content)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = f"{content}\n\n---\n*Last updated: {timestamp}*\n*Source: {Path(file_path).name}*"
        
        return title, body, tags
    
    def _process_python(self, file_path: str) -> Tuple[str, str, List[Dict[str, str]]]:
        """Process Python file"""
        content = self._read_file_content(file_path)
        title = self._extract_title_from_content(content, file_path)
        
        # Create markdown with code block
        body = f"""# {title}

Pythonコードファイル: `{Path(file_path).name}`

```python
{content}
```

---
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Source: {Path(file_path).name}*
"""
        
        tags = [{"name": "Python", "versions": []}]
        return title, body, tags
    
    def _process_javascript(self, file_path: str) -> Tuple[str, str, List[Dict[str, str]]]:
        """Process JavaScript file"""
        content = self._read_file_content(file_path)
        title = self._extract_title_from_content(content, file_path)
        
        body = f"""# {title}

JavaScriptコードファイル: `{Path(file_path).name}`

```javascript
{content}
```

---
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Source: {Path(file_path).name}*
"""
        
        tags = [{"name": "JavaScript", "versions": []}]
        return title, body, tags
    
    def _process_typescript(self, file_path: str) -> Tuple[str, str, List[Dict[str, str]]]:
        """Process TypeScript file"""
        content = self._read_file_content(file_path)
        title = self._extract_title_from_content(content, file_path)
        
        body = f"""# {title}

TypeScriptコードファイル: `{Path(file_path).name}`

```typescript
{content}
```

---
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Source: {Path(file_path).name}*
"""
        
        tags = [{"name": "TypeScript", "versions": []}]
        return title, body, tags
    
    def _process_text(self, file_path: str) -> Tuple[str, str, List[Dict[str, str]]]:
        """Process plain text file"""
        content = self._read_file_content(file_path)
        title = self._extract_title_from_content(content, file_path)
        
        body = f"""# {title}

テキストファイル: `{Path(file_path).name}`

```
{content}
```

---
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Source: {Path(file_path).name}*
"""
        
        tags = [{"name": "備忘録", "versions": []}]
        return title, body, tags
    
    def _process_rst(self, file_path: str) -> Tuple[str, str, List[Dict[str, str]]]:
        """Process reStructuredText file"""
        content = self._read_file_content(file_path)
        title = self._extract_title_from_content(content, file_path)
        
        # Convert to markdown-style
        body = f"""# {title}

reStructuredTextファイル: `{Path(file_path).name}`

```rst
{content}
```

---
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Source: {Path(file_path).name}*
"""
        
        tags = [{"name": "ドキュメント", "versions": []}]
        return title, body, tags
    
    def _process_generic(self, file_path: str) -> Tuple[str, str, List[Dict[str, str]]]:
        """Process generic file"""
        content = self._read_file_content(file_path)
        title = self._extract_title_from_content(content, file_path)
        extension = Path(file_path).suffix
        
        body = f"""# {title}

ファイル: `{Path(file_path).name}` ({extension})

```
{content}
```

---
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Source: {Path(file_path).name}*
"""
        
        tags = [{"name": "その他", "versions": []}]
        return title, body, tags
    
    def _extract_tags_from_content(self, content: str) -> List[Dict[str, str]]:
        """Extract tags from content"""
        tags = []
        
        # Look for YAML front matter
        if content.startswith('---'):
            end_marker = content.find('---', 3)
            if end_marker != -1:
                front_matter = content[3:end_marker]
                tag_match = re.search(r'tags:\s*\[(.*?)\]', front_matter)
                if tag_match:
                    tag_names = [tag.strip().strip('"\'') for tag in tag_match.group(1).split(',')]
                    tags = [{"name": name, "versions": []} for name in tag_names if name]
        
        # Default tags if none found
        if not tags:
            tags = [{"name": "備忘録", "versions": []}]
            
        return tags