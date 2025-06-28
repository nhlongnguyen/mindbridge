"""Job queue related exceptions."""


class JobError(Exception):
    """Base exception for job operations."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        """Initialize job error.

        Args:
            message: Error message
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.cause = cause


class BrokerConnectionError(JobError):
    """Exception raised when broker connection fails."""

    def __init__(
        self, message: str = "Broker connection error", cause: Exception | None = None
    ) -> None:
        """Initialize broker connection error.

        Args:
            message: Error message
            cause: Original exception that caused this error
        """
        super().__init__(message, cause)


class BrokerConfigurationError(JobError):
    """Exception raised when broker configuration is invalid."""

    def __init__(
        self,
        message: str = "Broker configuration error",
        cause: Exception | None = None,
    ) -> None:
        """Initialize broker configuration error.

        Args:
            message: Error message
            cause: Original exception that caused this error
        """
        super().__init__(message, cause)


class TaskExecutionError(JobError):
    """Exception raised when task execution fails."""

    def __init__(
        self, message: str = "Task execution error", cause: Exception | None = None
    ) -> None:
        """Initialize task execution error.

        Args:
            message: Error message
            cause: Original exception that caused this error
        """
        super().__init__(message, cause)


class TaskTimeoutError(JobError):
    """Exception raised when task execution times out."""

    def __init__(
        self, message: str = "Task execution timeout", cause: Exception | None = None
    ) -> None:
        """Initialize task timeout error.

        Args:
            message: Error message
            cause: Original exception that caused this error
        """
        super().__init__(message, cause)
