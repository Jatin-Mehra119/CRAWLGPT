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
    """
    Implements rate limiting using a sliding window approach.
    
    Attributes:
        requests_per_minute (int): Maximum allowed requests per minute
        requests (deque): Queue storing request timestamps
        
    Example:
        >>> limiter = RateLimiter(requests_per_minute=60)
        >>> limiter.can_proceed()
        True
    """
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter with requests per minute limit.
        
        Args:
            requests_per_minute (int): Maximum allowed requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests = deque()
    
    def can_proceed(self) -> bool:
        """
        Check if a new request can proceed based on rate limits.
        
        Returns:
            bool: True if request can proceed, False otherwise
        """
        now = time.time()
        # Remove requests older than 1 minute
        while self.requests and self.requests[0] < now - 60:
            self.requests.popleft()
        
        if len(self.requests) < self.requests_per_minute:
            self.requests.append(now)
            return True
        return False

class MetricsCollector:
    """
    Collects and manages application metrics and rate limiting.
    
    Combines Metrics and RateLimiter functionality to provide
    comprehensive monitoring capabilities.
    
    Example:
        >>> collector = MetricsCollector()
        >>> collector.record_request(success=True, response_time=0.1, tokens_used=100)
    """
    def __init__(self):
        """Initialize metrics collector with default Metrics and RateLimiter."""
        self.metrics = Metrics()
        self.rate_limiter = RateLimiter()
        
    def record_request(self, success: bool, response_time: float, tokens_used: int):
        """
        Record a request and update metrics.
        
        Args:
            success (bool): Whether the request was successful
            response_time (float): Request response time in seconds
            tokens_used (int): Number of tokens used in the request
        """
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