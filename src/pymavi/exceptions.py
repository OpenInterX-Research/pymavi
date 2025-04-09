"""Custom exceptions for the Pymavi SDK."""

class MaviError(Exception):
    """Base exception for all Pymavi-related errors."""
    pass

class MaviAuthenticationError(MaviError):
    """Raised when there are authentication-related errors."""
    pass

class MaviAPIError(MaviError):
    """Raised when the API returns an error response."""
    pass

class MaviValidationError(MaviError):
    """Raised when there are validation errors in the input parameters."""
    pass 