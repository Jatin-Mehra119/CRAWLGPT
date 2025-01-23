from typing import Optional
from datetime import datetime
import json

class ProgressTracker:
    def __init__(self, total_steps: int, operation_name: str):
        self.total_steps = total_steps
        self.current_step = 0
        self.operation_name = operation_name
        self.start_time = datetime.utcnow()
        self.status = "in_progress"
        self.message = ""
        
    def update(self, step: int, message: str = ""):
        self.current_step = step
        self.message = message
        
    def complete(self, message: str = "Operation completed successfully"):
        self.current_step = self.total_steps
        self.status = "completed"
        self.message = message
        
    def fail(self, error_message: str):
        self.status = "failed"
        self.message = error_message
        
    @property
    def progress(self) -> float:
        return (self.current_step / self.total_steps) * 100 if self.total_steps > 0 else 0
    
    def to_dict(self) -> dict:
        return {
            "operation": self.operation_name,
            "progress": round(self.progress, 2),
            "status": self.status,
            "message": self.message,
            "started_at": self.start_time.isoformat(),
            "current_step": self.current_step,
            "total_steps": self.total_steps
        }