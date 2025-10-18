"""
File monitoring service using watchdog
"""
import os
import time
from pathlib import Path
from typing import Set, Callable, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VSCodeFileHandler(FileSystemEventHandler):
    """Handle file system events for VSCode workspace"""
    
    def __init__(self, 
                 on_file_changed: Callable[[str], None],
                 watched_extensions: Set[str] = None,
                 ignore_patterns: Set[str] = None):
        self.on_file_changed = on_file_changed
        self.watched_extensions = watched_extensions or {'.md', '.py', '.js', '.ts', '.txt', '.rst'}
        self.ignore_patterns = ignore_patterns or {
            '.git', '__pycache__', 'node_modules', '.vscode', 
            '.pytest_cache', '.mypy_cache', 'dist', 'build'
        }
        self.last_modified = {}
        self.debounce_time = 2.0  # 2秒のデバウンス
        
    def should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed"""
        path = Path(file_path)
        
        # Check extension
        if path.suffix not in self.watched_extensions:
            return False
            
        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if pattern in path.parts:
                return False
                
        # Check if it's a regular file
        if not path.is_file():
            return False
            
        return True
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        
        if not self.should_process_file(file_path):
            return
            
        # Debounce rapid file changes
        current_time = time.time()
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < self.debounce_time:
                return
                
        self.last_modified[file_path] = current_time
        
        logger.info(f"File modified: {file_path}")
        
        # Schedule the callback
        try:
            self.on_file_changed(file_path)
        except Exception as e:
            logger.error(f"Error processing file change: {e}")

class FileMonitor:
    """Monitor VSCode workspace for file changes"""
    
    def __init__(self, 
                 workspace_path: str,
                 on_file_changed: Callable[[str], None],
                 watched_extensions: Set[str] = None,
                 ignore_patterns: Set[str] = None):
        self.workspace_path = Path(workspace_path)
        self.observer = Observer()
        self.handler = VSCodeFileHandler(
            on_file_changed=on_file_changed,
            watched_extensions=watched_extensions,
            ignore_patterns=ignore_patterns
        )
        self.is_running = False
        
    def start(self):
        """Start monitoring the workspace"""
        if self.is_running:
            return
            
        logger.info(f"Starting file monitor for: {self.workspace_path}")
        
        self.observer.schedule(
            self.handler, 
            str(self.workspace_path), 
            recursive=True
        )
        self.observer.start()
        self.is_running = True
        
    def stop(self):
        """Stop monitoring"""
        if not self.is_running:
            return
            
        logger.info("Stopping file monitor")
        self.observer.stop()
        self.observer.join()
        self.is_running = False
        
    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()