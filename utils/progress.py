from typing import Optional
from datetime import datetime
import json

class ProgressTracker:
    """
    Tracks progress of operations with step counting and status updates.
    
    Attributes:
        total_steps (int): Total number of steps in the operation
        current_step (int): Current step number
        operation_name (str): Name of the operation being tracked
        start_time (datetime): When the operation started
        status (str): Current status ('in_progress', 'completed', or 'failed')
        message (str): Current status message
    
    Example:
        >>> tracker = ProgressTracker(total_steps=3, operation_name="data_import")
        >>> tracker.update(1, "Reading file...")
        >>> tracker.complete("Import finished successfully")
    """
    def __init__(self, total_steps: int, operation_name: str):
        """
        Initialize progress tracker.
        
        Args:
            total_steps (int): Total number of steps in operation
            operation_name (str): Name of the operation
            
        Example:
            >>> tracker = ProgressTracker(3, "data_import")
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.operation_name = operation_name
        self.start_time = datetime.utcnow()
        self.status = "in_progress"
        self.message = ""
        
    def update(self, step: int, message: str = ""):
        """
        Update current step and status message.
        
        Args:
            step (int): Current step number
            message (str): Status message
            
        Example:
            >>> tracker.update(1, "Processing...")
        """
        self.current_step = step
        self.message = message
        
    def complete(self, message: str = "Operation completed successfully"):
        """
        Mark operation as completed.
        
        Args:
            message (str): Completion message
            
        Example:
            >>> tracker.complete("All data processed")
        """
        self.current_step = self.total_steps
        self.status = "completed"
        self.message = message
        
    def fail(self, error_message: str):
        """
        Mark operation as failed.
        
        Args:
            error_message (str): Error description
            
        Example:
            >>> tracker.fail("Network connection lost")
        """
        self.status = "failed"
        self.message = error_message
        
    @property
    def progress(self) -> float:
        """
        Calculate progress percentage.
        
        Returns:
            float: Progress as percentage between 0-100
            
        Example:
            >>> tracker.progress
            66.66  # When 2 of 3 steps completed
        """
        return (self.current_step / self.total_steps) * 100 if self.total_steps > 0 else 0
    
    def to_dict(self) -> dict:
        """
        Convert tracker state to dictionary.
        
        Returns:
            dict: Current state as dictionary
            
        Example:
            >>> tracker.to_dict()
            {
                'operation': 'data_import',
                'progress': 66.66,
                'status': 'in_progress',
                'message': 'Processing...',
                'started_at': '2024-01-23T10:30:00',
                'current_step': 2,
                'total_steps': 3
            }
        """
        return {
            "operation": self.operation_name,
            "progress": round(self.progress, 2),
            "status": self.status,
            "message": self.message,
            "started_at": self.start_time.isoformat(),
            "current_step": self.current_step,
            "total_steps": self.total_steps
        }