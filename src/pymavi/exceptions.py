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

class MaviBusySystemError(MaviError):
    """Raised when the Mavi server is busy and cannot process the request."""
    pass

class MaviDuplicateError(MaviError):
    """Raised when a duplicate request is detected, such as deleting a video that is already deleted."""
    pass

class MaviDisabledAccountError(MaviError):
    """Raised when the account is disabled. Contact support for assistance."""
    pass