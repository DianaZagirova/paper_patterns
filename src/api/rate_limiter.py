"""
Rate Limiter for API Calls

This module provides thread-safe rate limiting for API calls.
"""
import time
import threading
from typing import Callable, Any, Optional


class RateLimiter:
    """Thread-safe rate limiter for API calls."""
    
    def __init__(self, max_requests_per_sec: int):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests_per_sec: Maximum number of requests allowed per second
        """
        self.max_requests_per_sec = max_requests_per_sec
        self.semaphore = threading.BoundedSemaphore(value=max_requests_per_sec)
        self.last_request_time = [0]  # List to allow modification in nested scopes
    
    def __call__(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with rate limiting.
        
        Args:
            func: The function to call
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the function call
        """
        with self.semaphore:
            # Enforce minimum time between requests
            elapsed = time.time() - self.last_request_time[0]
            wait_time = max(0, 1.0 / self.max_requests_per_sec - elapsed)
            
            if wait_time > 0:
                time.sleep(wait_time)
            
            self.last_request_time[0] = time.time()
            return func(*args, **kwargs)
