"""
Custom exceptions for Purview CLI
"""

class PurviewClientError(Exception):
    """Base exception class for Purview client errors"""
    pass

class PurviewAuthenticationError(PurviewClientError):
    """Exception raised for authentication errors"""
    pass

class PurviewAPIError(PurviewClientError):
    """Exception raised for API errors"""
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class PurviewConfigurationError(PurviewClientError):
    """Exception raised for configuration errors"""
    pass

class PurviewValidationError(PurviewClientError):
    """Exception raised for validation errors"""
    pass

class PurviewBulkOperationError(PurviewClientError):
    """Exception raised for bulk operation errors"""
    def __init__(self, message, failed_operations=None):
        super().__init__(message)
        self.failed_operations = failed_operations or []

class PurviewRateLimitError(PurviewClientError):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after
