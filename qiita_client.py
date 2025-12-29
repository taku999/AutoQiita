"""
Qiita API client for managing drafts
"""
import requests
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class QiitaDraft:
    id: Optional[str] = None
    title: str = ""
    body: str = ""
    tags: List[Dict[str, str]] = None
    private: bool = True
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class QiitaClient:
    """Qiita API client for managing drafts"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://qiita.com/api/v2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def create_draft(self, draft: QiitaDraft) -> Dict[str, Any]:
        """Create a new draft on Qiita"""
        url = f"{self.base_url}/items"
        
        data = {
            "title": draft.title,
            "body": draft.body,
            "tags": draft.tags,
            "private": draft.private
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def update_draft(self, item_id: str, draft: QiitaDraft) -> Dict[str, Any]:
        """Update an existing draft on Qiita"""
        url = f"{self.base_url}/items/{item_id}"
        
        data = {
            "title": draft.title,
            "body": draft.body,
            "tags": draft.tags,
            "private": draft.private
        }
        
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def get_draft(self, item_id: str) -> Dict[str, Any]:
        """Get a specific draft from Qiita"""
        url = f"{self.base_url}/items/{item_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def list_user_items(self, per_page: int = 20, page: int = 1) -> List[Dict[str, Any]]:
        """List user's items (including drafts)"""
        url = f"{self.base_url}/authenticated_user/items"
        params = {"per_page": per_page, "page": page}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def find_or_create_draft(self, title: str, body: str, tags: List[Dict[str, str]] = None, 
                           security_report: Dict = None, force_upload: bool = False) -> Dict[str, Any]:
        """Create new draft with security checking"""
        if tags is None:
            tags = []
        
        # Check security report
        if security_report and not force_upload:
            if security_report.get("status") == "critical":
                raise SecurityError(
                    f"アップロードが拒否されました: {security_report.get('message', '重大なセキュリティ問題が検出されました')}"
                )
        
        # Create new draft directly (avoiding permission issues with list_user_items)
        draft = QiitaDraft(
            title=title,
            body=body,
            tags=tags,
            private=True
        )
        
        try:
            return self.create_draft(draft)
        except Exception as e:
            # If creation fails, try to find existing drafts (fallback)
            try:
                items = self.list_user_items()
                for item in items:
                    if item.get("title") == title and item.get("private", False):
                        # Update existing draft
                        draft.id = item["id"]
                        return self.update_draft(item["id"], draft)
                # If no existing draft found, re-raise original error
                raise e
            except Exception:
                # If list_user_items also fails, re-raise original creation error
                raise e
    
    def create_draft_simple(self, title: str, body: str, tags: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Simple draft creation without duplicate checking"""
        if tags is None:
            tags = []
        
        draft = QiitaDraft(
            title=title,
            body=body,
            tags=tags,
            private=True
        )
        return self.create_draft(draft)

class SecurityError(Exception):
    """Security-related error for blocking uploads"""
    pass