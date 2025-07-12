"""
Progress tracking utilities for all methodologies
"""

import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ProgressTracker:
    """Track and report progress for analysis tasks"""
    
    def __init__(self, task_name: str, total_items: int):
        self.task_name = task_name
        self.total_items = total_items
        self.completed_items = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.update_interval = 5.0  # Seconds between updates
        
    def update(self, items_completed: int = 1, force: bool = False) -> None:
        """Update progress and log if interval has passed"""
        self.completed_items += items_completed
        current_time = time.time()
        
        # Log progress if interval passed or forced
        if force or (current_time - self.last_update_time) >= self.update_interval:
            self._log_progress()
            self.last_update_time = current_time
    
    def _log_progress(self) -> None:
        """Log current progress"""
        elapsed = time.time() - self.start_time
        percent = (self.completed_items / self.total_items * 100) if self.total_items > 0 else 0
        
        if self.completed_items > 0:
            avg_time_per_item = elapsed / self.completed_items
            remaining_items = self.total_items - self.completed_items
            eta_seconds = avg_time_per_item * remaining_items
            eta_str = self._format_time(eta_seconds)
        else:
            eta_str = "calculating..."
        
        logger.info(
            f"{self.task_name}: {self.completed_items}/{self.total_items} "
            f"({percent:.1f}%) - ETA: {eta_str}"
        )
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds into human-readable time"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def finish(self) -> Dict[str, Any]:
        """Mark task as finished and return summary"""
        elapsed = time.time() - self.start_time
        
        summary = {
            "task_name": self.task_name,
            "total_items": self.total_items,
            "completed_items": self.completed_items,
            "elapsed_seconds": elapsed,
            "elapsed_formatted": self._format_time(elapsed),
            "success_rate": (self.completed_items / self.total_items * 100) if self.total_items > 0 else 0
        }
        
        logger.info(
            f"{self.task_name} completed: {self.completed_items}/{self.total_items} "
            f"in {summary['elapsed_formatted']} ({summary['success_rate']:.1f}% success)"
        )
        
        return summary


class BatchProgressTracker(ProgressTracker):
    """Extended progress tracker for batch processing"""
    
    def __init__(self, task_name: str, total_batches: int, items_per_batch: int):
        super().__init__(task_name, total_batches)
        self.items_per_batch = items_per_batch
        self.total_items_processed = 0
        
    def update_batch(self, batch_num: int, items_in_batch: int, success: bool = True) -> None:
        """Update progress for a completed batch"""
        self.total_items_processed += items_in_batch
        
        status = "completed" if success else "failed"
        logger.info(
            f"{self.task_name} - Batch {batch_num}/{self.total_items}: {status} "
            f"({items_in_batch} items, {self.total_items_processed} total)"
        )
        
        self.update(1)