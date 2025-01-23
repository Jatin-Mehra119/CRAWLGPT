from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from collections import deque
import logging

@dataclass
class Metrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0
    total_tokens_used: int = 0
    start_time: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "average_response_time": round(self.average_response_time, 2),
            "total_tokens_used": self.total_tokens_used,
            "uptime": str(datetime.utcnow() - self.start_time)
        }

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = deque()
    
    def can_proceed(self) -> bool:
        now = time.time()
        # Remove requests older than 1 minute
        while self.requests and self.requests[0] < now - 60:
            self.requests.popleft()
        
        if len(self.requests) < self.requests_per_minute:
            self.requests.append(now)
            return True
        return False

class MetricsCollector:
    def __init__(self):
        self.metrics = Metrics()
        self.rate_limiter = RateLimiter()
        
    def record_request(self, success: bool, response_time: float, tokens_used: int):
        self.metrics.total_requests += 1
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        # Update average response time
        self.metrics.average_response_time = (
            (self.metrics.average_response_time * (self.metrics.total_requests - 1) + response_time)
            / self.metrics.total_requests
        )
        self.metrics.total_tokens_used += tokens_used