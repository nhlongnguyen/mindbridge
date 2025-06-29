"""Cache-related exceptions."""


class CacheError(Exception):
    """Base exception for cache operations."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        """Initialize cache error.

        Args:
            message: Error message
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.cause = cause


class CacheConnectionError(CacheError):
    """Exception raised when cache connection fails."""

    def __init__(
        self, message: str = "Cache connection error", cause: Exception | None = None
    ) -> None:
        """Initialize cache connection error.

        Args:
            message: Error message
            cause: Original exception that caused this error
        """
        super().__init__(message, cause)


class CacheOperationError(CacheError):
    """Exception raised when cache operation fails."""

    def __init__(
        self, message: str = "Cache operation error", cause: Exception | None = None
    ) -> None:
        """Initialize cache operation error.

        Args:
            message: Error message
            cause: Original exception that caused this error
        """
        super().__init__(message, cause)


class CacheConfigurationError(CacheError):
    """Exception raised when cache configuration is invalid."""

    def __init__(
        self, message: str = "Cache configuration error", cause: Exception | None = None
    ) -> None:
        """Initialize cache configuration error.

        Args:
            message: Error message
            cause: Original exception that caused this error
        """
        super().__init__(message, cause)
