"""
Security scanner for content before uploading to Qiita
"""
import re
import os
import json
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class SecurityIssue:
    """Security issue found in content"""
    level: str  # 'critical', 'high', 'medium', 'low', 'info'
    category: str  # 'credentials', 'personal_info', 'dangerous_code', etc.
    description: str
    line_number: int
    line_content: str
    suggestion: str = ""

class SecurityScanner:
    """Scan content for security issues before uploading to Qiita"""
    
    def __init__(self, config_file: str = None):
        self.patterns = self._load_security_patterns(config_file)
        self.whitelist_patterns = self._load_whitelist_patterns()
    
    def _load_security_patterns(self, config_file: str = None) -> Dict[str, List[Dict]]:
        """Load security scanning patterns"""
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Default patterns
        return {
            "credentials": [
                {
                    "pattern": r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?[a-zA-Z0-9@#$%^&*!]+['\"]?",
                    "description": "パスワードが平文で含まれている可能性があります",
                    "level": "critical",
                    "suggestion": "パスワードは環境変数や設定ファイルに移動してください"
                },
                {
                    "pattern": r"(?i)(api[_-]?key|apikey|access[_-]?token|secret[_-]?key)\s*[=:]\s*['\"]?[a-zA-Z0-9_-]{16,}['\"]?",
                    "description": "APIキーまたはアクセストークンが含まれている可能性があります",
                    "level": "critical",
                    "suggestion": "APIキーは環境変数に移動し、ダミー値に置き換えてください"
                },
                {
                    "pattern": r"(?i)(database[_-]?url|db[_-]?url|connection[_-]?string)\s*[=:]\s*['\"]?[^'\"\\s]+['\"]?",
                    "description": "データベース接続文字列が含まれている可能性があります",
                    "level": "high",
                    "suggestion": "接続文字列は環境変数に移動してください"
                },
                {
                    "pattern": r"(?i)-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
                    "description": "秘密鍵が含まれています",
                    "level": "critical",
                    "suggestion": "秘密鍵は絶対に公開しないでください"
                }
            ],
            "personal_info": [
                {
                    "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                    "description": "メールアドレスが含まれています",
                    "level": "medium",
                    "suggestion": "個人のメールアドレスは example@example.com に置き換えることをお勧めします"
                },
                {
                    "pattern": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
                    "description": "IPアドレスが含まれています",
                    "level": "medium",
                    "suggestion": "実際のIPアドレスはダミー値（例：192.168.1.1）に置き換えることをお勧めします"
                },
                {
                    "pattern": r"\b(?:\+81|0)\d{1,4}-?\d{1,4}-?\d{4}\b",
                    "description": "電話番号が含まれている可能性があります",
                    "level": "medium",
                    "suggestion": "実際の電話番号はダミー値に置き換えてください"
                }
            ],
            "dangerous_code": [
                {
                    "pattern": r"(?i)(eval|exec)\s*\(",
                    "description": "動的コード実行（eval/exec）が使用されています",
                    "level": "high",
                    "suggestion": "eval/execの使用は危険です。より安全な代替手段を検討してください"
                },
                {
                    "pattern": r"(?i)(os\.system|subprocess\.call|subprocess\.run)\s*\([^)]*shell\s*=\s*True",
                    "description": "シェルインジェクションの脆弱性の可能性があります",
                    "level": "high",
                    "suggestion": "shell=Trueの使用を避け、引数をリストで渡してください"
                },
                {
                    "pattern": r"(?i)pickle\.loads?\s*\(",
                    "description": "pickle.loadsは信頼できないデータに対して危険です",
                    "level": "medium",
                    "suggestion": "信頼できないデータにはjsonやその他の安全な形式を使用してください"
                },
                {
                    "pattern": r"(?i)(rm\s+-rf|del\s+/s|format\s+c:)",
                    "description": "危険なシステムコマンドが含まれています",
                    "level": "high",
                    "suggestion": "破壊的なコマンドは削除するか、コメントアウトしてください"
                }
            ],
            "web_security": [
                {
                    "pattern": r"(?i)(<script[^>]*>|javascript:)",
                    "description": "XSS攻撃の可能性があるJavaScriptコードが含まれています",
                    "level": "medium",
                    "suggestion": "サンプルコードの場合は安全な例に置き換えてください"
                },
                {
                    "pattern": r"(?i)(union\s+select|drop\s+table|delete\s+from.*where)",
                    "description": "SQLインジェクション攻撃のパターンが含まれています",
                    "level": "medium",
                    "suggestion": "SQLインジェクションの例の場合は、安全なコメント付きで説明してください"
                }
            ],
            "file_paths": [
                {
                    "pattern": r"(?i)[c-z]:\\(?:users|documents|desktop)\\[^\\s\"']+",
                    "description": "個人のファイルパスが含まれています",
                    "level": "low",
                    "suggestion": "個人のパスは汎用的なパス例に置き換えてください"
                },
                {
                    "pattern": r"/home/[^/\\s\"']+",
                    "description": "個人のホームディレクトリパスが含まれています",
                    "level": "low",
                    "suggestion": "個人のパスは /home/user や /path/to などに置き換えてください"
                }
            ]
        }
    
    def _load_whitelist_patterns(self) -> List[str]:
        """Load patterns that should be ignored (whitelisted)"""
        return [
            r"example\.com",
            r"test@example\.com",
            r"your_api_key_here",
            r"your_password_here",
            r"192\.168\.1\.1",
            r"127\.0\.0\.1",
            r"localhost",
            r"dummy_token",
            r"sample_password"
        ]
    
    def scan_content(self, content: str, file_path: str = "") -> List[SecurityIssue]:
        """Scan content for security issues"""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip if line matches whitelist patterns
            if self._is_whitelisted(line):
                continue
            
            # Check all security patterns
            for category, patterns in self.patterns.items():
                for pattern_config in patterns:
                    pattern = pattern_config["pattern"]
                    matches = re.finditer(pattern, line)
                    
                    for match in matches:
                        issue = SecurityIssue(
                            level=pattern_config["level"],
                            category=category,
                            description=pattern_config["description"],
                            line_number=line_num,
                            line_content=line.strip(),
                            suggestion=pattern_config.get("suggestion", "")
                        )
                        issues.append(issue)
        
        return issues
    
    def _is_whitelisted(self, line: str) -> bool:
        """Check if line matches whitelist patterns"""
        for pattern in self.whitelist_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False
    
    def scan_file(self, file_path: str) -> List[SecurityIssue]:
        """Scan a file for security issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.scan_content(content, file_path)
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
            return []
    
    def get_security_report(self, issues: List[SecurityIssue]) -> Dict[str, Any]:
        """Generate a security report"""
        if not issues:
            return {
                "status": "passed",
                "total_issues": 0,
                "by_level": {},
                "by_category": {},
                "message": "セキュリティチェックに問題はありませんでした"
            }
        
        # Count by level
        by_level = {}
        for issue in issues:
            by_level[issue.level] = by_level.get(issue.level, 0) + 1
        
        # Count by category
        by_category = {}
        for issue in issues:
            by_category[issue.category] = by_category.get(issue.category, 0) + 1
        
        # Determine overall status
        has_critical = any(issue.level == "critical" for issue in issues)
        has_high = any(issue.level == "high" for issue in issues)
        
        if has_critical:
            status = "critical"
            message = "❌ 重大なセキュリティ問題が見つかりました。修正が必要です。"
        elif has_high:
            status = "high"
            message = "⚠️ 高レベルのセキュリティ問題が見つかりました。確認が必要です。"
        else:
            status = "warning"
            message = "⚠️ セキュリティに関する注意事項があります。確認をお勧めします。"
        
        return {
            "status": status,
            "total_issues": len(issues),
            "by_level": by_level,
            "by_category": by_category,
            "message": message,
            "issues": issues
        }
    
    def should_block_upload(self, issues: List[SecurityIssue]) -> bool:
        """Determine if upload should be blocked based on security issues"""
        return any(issue.level in ["critical"] for issue in issues)
    
    def format_report_for_display(self, report: Dict[str, Any]) -> str:
        """Format security report for console display"""
        if report["status"] == "passed":
            return "✅ セキュリティチェック: 問題なし"
        
        output = [f"\n{report['message']}"]
        output.append(f"検出された問題: {report['total_issues']}件")
        
        if report["by_level"]:
            output.append("\n問題レベル別:")
            for level, count in sorted(report["by_level"].items()):
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(level, "⚪")
                output.append(f"  {emoji} {level}: {count}件")
        
        if "issues" in report:
            output.append("\n詳細:")
            for i, issue in enumerate(report["issues"][:10], 1):  # Show first 10 issues
                output.append(f"\n{i}. [{issue.level.upper()}] {issue.description}")
                output.append(f"   行 {issue.line_number}: {issue.line_content[:80]}...")
                if issue.suggestion:
                    output.append(f"   💡 提案: {issue.suggestion}")
            
            if len(report["issues"]) > 10:
                output.append(f"\n... および他 {len(report['issues']) - 10} 件")
        
        return "\n".join(output)