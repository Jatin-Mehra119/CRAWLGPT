from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from collections import deque
import logging

class Metrics:
    def __init__(self, total_requests=0, successful_requests=0, average_response_time=0.0, uptime=0.0):
        """
        Initialize the Metrics class.
        Args:
            total_requests (int): Total number of requests.
            successful_requests (int): Number of successful requests.
            average_response_time (float): Average response time.
            uptime (float): The total uptime in seconds.
        """
        self.total_requests = total_requests
        self.successful_requests = successful_requests
        self.average_response_time = average_response_time
        self.uptime = uptime
        self.start_time = time.time()

    def to_dict(self):
        """
        Convert the metrics to a dictionary format.
        """
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "average_response_time": self.average_response_time,
            "uptime": self.uptime + (time.time() - self.start_time)
        }

    @classmethod
    def from_dict(cls, metrics_dict):
        """
        Create a Metrics instance from a dictionary.
        Args:
            metrics_dict (dict): A dictionary containing the metrics.
        """
        instance = cls(
            total_requests=metrics_dict.get("total_requests", 0),
            successful_requests=metrics_dict.get("successful_requests", 0),
            average_response_time=metrics_dict.get("average_response_time", 0.0),
            uptime=metrics_dict.get("uptime", 0.0)
        )
        return instance

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
            # Ensure 'failed_requests' attribute is present in the Metrics class
            if not hasattr(self.metrics, "failed_requests"):
                self.metrics.failed_requests = 0
            self.metrics.failed_requests += 1
        
        # Update average response time
        self.metrics.average_response_time = (
            (self.metrics.average_response_time * (self.metrics.total_requests - 1) + response_time)
            / self.metrics.total_requests
        )
        # Ensure 'total_tokens_used' attribute is present in the Metrics class
        if not hasattr(self.metrics, "total_tokens_used"):
            self.metrics.total_tokens_used = 0
        self.metrics.total_tokens_used += tokens_used