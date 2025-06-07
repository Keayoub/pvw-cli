"""
Retry handler for Purview API operations
"""

import time
import random
import logging
from typing import Callable, Any, Dict, Optional
from .exceptions import PurviewAPIError, PurviewRateLimitError

class RetryHandler:
    """Handles retry logic for API operations with exponential backoff"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize retry handler
        
        Args:
            config: Retry configuration dictionary
        """
        default_config = {
            'max_retries': 3,
            'base_delay': 1.0,
            'max_delay': 60.0,
            'exponential_base': 2,
            'jitter': True,
            'retry_on_status_codes': [429, 500, 502, 503, 504],
            'retry_on_exceptions': [ConnectionError, TimeoutError]
        }
        
        self.config = {**default_config, **(config or {})}
        self.logger = logging.getLogger(__name__)

    def execute(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute operation with retry logic
        
        Args:
            operation: Function to execute
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Result of operation
            
        Raises:
            Exception: If all retries exhausted
        """
        last_exception = None
        
        for attempt in range(self.config['max_retries'] + 1):
            try:
                return operation(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if not self._should_retry(e, attempt):
                    raise e
                
                if attempt < self.config['max_retries']:
                    delay = self._calculate_delay(attempt)
                    self.logger.warning(
                        f"Operation failed (attempt {attempt + 1}), retrying in {delay:.2f}s: {e}"
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(f"Operation failed after {attempt + 1} attempts: {e}")
                    raise e
        
        # This should never be reached, but just in case
        raise last_exception

    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if operation should be retried
        
        Args:
            exception: Exception that occurred
            attempt: Current attempt number
            
        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.config['max_retries']:
            return False
        
        # Check for specific exception types
        if type(exception) in self.config['retry_on_exceptions']:
            return True
        
        # Check for API errors with specific status codes
        if isinstance(exception, PurviewAPIError):
            if hasattr(exception, 'status_code'):
                return exception.status_code in self.config['retry_on_status_codes']
        
        # Check for rate limit errors
        if isinstance(exception, PurviewRateLimitError):
            return True
        
        return False

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for retry attempt using exponential backoff
        
        Args:
            attempt: Current attempt number
            
        Returns:
            Delay in seconds
        """
        delay = self.config['base_delay'] * (
            self.config['exponential_base'] ** attempt
        )
        
        # Apply maximum delay limit
        delay = min(delay, self.config['max_delay'])
        
        # Add jitter to prevent thundering herd
        if self.config['jitter']:
            jitter = random.uniform(0, 0.1) * delay
            delay += jitter
        
        return delay
