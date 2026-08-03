"""
Compass SDK Exceptions
"""


class CompassAPIError(Exception):
    """Base exception for Compass API errors"""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class CompassAuthenticationError(CompassAPIError):
    """Authentication failed (401)"""
    pass


class CompassNotFoundError(CompassAPIError):
    """Resource not found (404)"""
    pass


class CompassRateLimitError(CompassAPIError):
    """Rate limit exceeded (429)"""
    pass


class CompassValidationError(CompassAPIError):
    """Validation error (422)"""
    pass
