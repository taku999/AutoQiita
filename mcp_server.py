"""
MCP (Model Context Protocol) Server for AutoQiita
"""
import json
import asyncio
import logging
from typing import Dict, Any, List
from pathlib import Path
import os
from datetime import datetime

# FastAPI for MCP server
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Local imports
from .qiita_client import QiitaClient
from .file_monitor import FileMonitor
from .content_processor import ContentProcessor
from .config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPRequest(BaseModel):
    method: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    result: Any = None
    error: str = None

class AutoQiitaMCPServer:
    """MCP Server for AutoQiita"""
    
    def __init__(self, config: Config):
        self.config = config
        self.qiita_client = QiitaClient(config.qiita_token)
        self.content_processor = ContentProcessor()
        self.file_monitor = None
        self.app = FastAPI(title="AutoQiita MCP Server")
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self.setup_routes()
        
    def setup_routes(self):
        """Setup FastAPI routes for MCP"""
        
        @self.app.post("/mcp/request")
        async def handle_mcp_request(request: MCPRequest) -> MCPResponse:
            """Handle MCP requests"""
            try:
                if request.method == "initialize":
                    return await self.handle_initialize(request.params)
                elif request.method == "start_monitoring":
                    return await self.handle_start_monitoring(request.params)
                elif request.method == "stop_monitoring":
                    return await self.handle_stop_monitoring(request.params)
                elif request.method == "save_to_qiita":
                    return await self.handle_save_to_qiita(request.params)
                elif request.method == "get_status":
                    return await self.handle_get_status(request.params)
                else:
                    return MCPResponse(error=f"Unknown method: {request.method}")
            except Exception as e:
                logger.error(f"Error handling MCP request: {e}")
                return MCPResponse(error=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    async def handle_initialize(self, params: Dict[str, Any]) -> MCPResponse:
        """Initialize MCP connection"""
        workspace_path = params.get("workspace_path", self.config.workspace_path)
        
        if workspace_path:
            self.config.workspace_path = workspace_path
            
        return MCPResponse(result={
            "capabilities": {
                "file_monitoring": True,
                "qiita_integration": True,
                "content_processing": True
            },
            "workspace_path": self.config.workspace_path
        })
    
    async def handle_start_monitoring(self, params: Dict[str, Any]) -> MCPResponse:
        """Start file monitoring"""
        if self.file_monitor and self.file_monitor.is_running:
            return MCPResponse(result={"status": "already_running"})
        
        try:
            self.file_monitor = FileMonitor(
                workspace_path=self.config.workspace_path,
                on_file_changed=self.on_file_changed,
                watched_extensions=set(self.config.watched_extensions),
                ignore_patterns=set(self.config.ignore_patterns)
            )
            self.file_monitor.start()
            
            logger.info(f"Started monitoring workspace: {self.config.workspace_path}")
            return MCPResponse(result={"status": "started"})
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return MCPResponse(error=f"Failed to start monitoring: {e}")
    
    async def handle_stop_monitoring(self, params: Dict[str, Any]) -> MCPResponse:
        """Stop file monitoring"""
        if self.file_monitor:
            self.file_monitor.stop()
            self.file_monitor = None
            
        return MCPResponse(result={"status": "stopped"})
    
    async def handle_save_to_qiita(self, params: Dict[str, Any]) -> MCPResponse:
        """Manually save file to Qiita"""
        file_path = params.get("file_path")
        if not file_path:
            return MCPResponse(error="file_path is required")
        
        try:
            result = await self.save_file_to_qiita(file_path)
            return MCPResponse(result=result)
        except Exception as e:
            return MCPResponse(error=str(e))
    
    async def handle_get_status(self, params: Dict[str, Any]) -> MCPResponse:
        """Get server status"""
        return MCPResponse(result={
            "monitoring": self.file_monitor.is_running if self.file_monitor else False,
            "workspace_path": self.config.workspace_path,
            "watched_extensions": self.config.watched_extensions,
            "qiita_connected": bool(self.config.qiita_token)
        })
    
    def on_file_changed(self, file_path: str):
        """Handle file change event"""
        logger.info(f"Processing file change: {file_path}")
        
        # Run async operation in background
        asyncio.create_task(self.save_file_to_qiita(file_path))
    
    async def save_file_to_qiita(self, file_path: str, force_upload: bool = False) -> Dict[str, Any]:
        """Save file content to Qiita draft with security checking"""
        try:
            # Process file content with security scan
            title, body, tags, security_report = self.content_processor.process_file(file_path)
            
            # Check if upload should be blocked
            if security_report and not force_upload:
                if self.content_processor.should_block_upload(security_report):
                    logger.warning(f"Upload blocked for {file_path} due to security issues")
                    return {
                        "success": False,
                        "file_path": file_path,
                        "title": title,
                        "blocked": True,
                        "security_report": security_report,
                        "message": "セキュリティ上の問題によりアップロードがブロックされました"
                    }
                
                # Add security warning to content if issues found
                if security_report.get("total_issues", 0) > 0:
                    body = self.content_processor.add_security_warning_to_content(body, security_report)
            
            # Save to Qiita
            result = self.qiita_client.find_or_create_draft(
                title, body, tags, security_report, force_upload
            )
            
            logger.info(f"Saved to Qiita: {title} (ID: {result.get('id')})")
            
            return {
                "success": True,
                "file_path": file_path,
                "qiita_id": result.get("id"),
                "title": title,
                "url": result.get("url"),
                "security_report": security_report
            }
            
        except Exception as e:
            logger.error(f"Failed to save to Qiita: {e}")
            raise
    
    def run(self, host: str = "localhost", port: int = 8000):
        """Run the MCP server"""
        logger.info(f"Starting AutoQiita MCP Server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

def main():
    """Main entry point for MCP server"""
    config = Config()
    server = AutoQiitaMCPServer(config)
    server.run()

if __name__ == "__main__":
    main()