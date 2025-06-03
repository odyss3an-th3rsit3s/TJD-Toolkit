"""Define exception hierarchy for TJD-Toolkit operations.

This module implements the base exception types and error handling patterns
for the TJD-Toolkit application. All custom exceptions inherit from TJDError to ensure
consistent error handling and logging throughout the codebase.

Example:
    >>> try:
    ...     raise TJDError("Failed to process request")
    ... except TJDError as e:
    ...     print(f"Error occurred: {e}")
    Error occurred: Failed to process request

Attributes:
    __all__ (List[str]): Public interface exports.
    logger (logging.Logger): Module-level logger instance.
"""

from __future__ import annotations

import logging
from typing import Optional

__all__ = [
    "TJDError",
    "ConfigurationError",
    "OperationError",
    "FileOperationError",
    "ValidationError",
    "JSONParsingError",
    "PlatformError",
]

logger = logging.getLogger(__name__)


class TJDError(Exception):
    """Define base exception type for all toolkit errors.

    Serve as the foundation for the project's exception hierarchy and
    provide consistent error handling patterns across the application.

    Attributes:
        message (str): Human-readable error description.
        cause (Optional[Exception]): Original exception that caused this error.

    Args:
        message (str): Clear description of the error.
        cause (Optional[Exception], optional): Original exception. Defaults to None.

    Example:
        >>> error = TJDError("Database connection failed", cause=db_error)
        >>> assert error.message == "Database connection failed"
        >>> assert error.cause == db_error
    """

    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        """Initialize error with message and optional cause.

        Args:
            message (str): Clear description of the error.
            cause (Optional[Exception]): Original exception. Defaults to None.

        Note:
            Use descriptive messages that guide users toward resolution.
        """
        super().__init__(message)
        self.message = message
        self.cause = cause

        # Log error creation at debug level for troubleshooting
        logger.debug(f"TJDError created: {message}", exc_info=cause if cause else False)


class ConfigurationError(TJDError):
    """Signal configuration-related failures.

    Indicates issues with configuration handling including missing files,
    invalid formats, incorrect values, and structural problems.

    Example:
        >>> try:
        ...     raise ConfigurationError("Missing required setting 'port'")
        ... except ConfigurationError as e:
        ...     print(f"Config error: {e}")
        Config error: Missing required setting 'port'
    """


class OperationError(TJDError):
    """Signal failure of specific operations.

    Indicate failures in system operations like file I/O, network
    requests, or external process interactions.

    Attributes:
        operation (str): Name or identifier of the failed operation.

    Example:
        >>> try:
        ...     raise OperationError("save_file", "Permission denied")
        ... except OperationError as e:
        ...     print(f"Operation failed: {e}")
        Operation failed: save_file failed: Permission denied
    """

    def __init__(self, operation: str, message: str, cause: Optional[Exception] = None) -> None:
        """Initialize operation error with context.

        Args:
            operation (str): Name of the operation that failed.
            message (str): Description of the failure.
            cause (Optional[Exception]): Original error. Defaults to None.
        """
        super().__init__(f"{operation} failed: {message}", cause)
        self.operation = operation


class FileOperationError(OperationError):
    """Signal file system operation failures.

    Indicate failures in file operations including reading, writing,
    creating directories, and file access permissions.

    Attributes:
        file_path (Optional[str]): Path to the file that caused the error.

    Example:
        >>> try:
        ...     raise FileOperationError("read", "Permission denied", "/etc/config")
        ... except FileOperationError as e:
        ...     print(f"File error: {e}")
        File error: read failed: Permission denied
    """

    def __init__(
        self,
        operation: str,
        message: str,
        file_path: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize file operation error with context.

        Args:
            operation (str): Type of file operation that failed.
            message (str): Description of the failure.
            file_path (Optional[str]): Path to the file. Defaults to None.
            cause (Optional[Exception]): Original error. Defaults to None.
        """
        super().__init__(operation, message, cause)
        self.file_path = file_path


class ValidationError(TJDError):
    """Signal data validation failures.

    Indicate failures in data validation including type checking,
    format validation, and constraint violations.

    Attributes:
        field (Optional[str]): Name of the field that failed validation.
        value (Optional[str]): String representation of the invalid value.

    Example:
        >>> try:
        ...     raise ValidationError("Invalid email format", "email", "invalid-email")
        ... except ValidationError as e:
        ...     print(f"Validation error: {e}")
        Validation error: Invalid email format
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize validation error with context.

        Args:
            message (str): Description of the validation failure.
            field (Optional[str]): Name of the field. Defaults to None.
            value (Optional[str]): Invalid value representation. Defaults to None.
            cause (Optional[Exception]): Original error. Defaults to None.
        """
        super().__init__(message, cause)
        self.field = field
        self.value = value


class JSONParsingError(ConfigurationError):
    """Signal JSON parsing and serialization failures.

    Indicate failures in JSON operations including parsing invalid JSON,
    encoding errors, and structure validation issues.

    Example:
        >>> try:
        ...     raise JSONParsingError("Invalid JSON syntax in config file")
        ... except JSONParsingError as e:
        ...     print(f"JSON error: {e}")
        JSON error: Invalid JSON syntax in config file
    """


class PlatformError(TJDError):
    """Signal platform-specific operation failures.

    Indicate failures in platform-dependent operations including privilege
    elevation, system path access, and OS-specific functionality.

    Attributes:
        platform (Optional[str]): The platform where the error occurred.
        operation (Optional[str]): The platform-specific operation that failed.

    Example:
        >>> try:
        ...     raise PlatformError("Failed to elevate privileges", platform="windows")
        ... except PlatformError as e:
        ...     print(f"Platform error: {e}")
        Platform error: Failed to elevate privileges
    """

    def __init__(
        self,
        message: str,
        platform: Optional[str] = None,
        operation: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize platform error with context.

        Args:
            message (str): Description of the platform error.
            platform (Optional[str]): Affected platform. Defaults to None.
            operation (Optional[str]): Failed operation. Defaults to None.
            cause (Optional[Exception]): Original error. Defaults to None.
        """
        super().__init__(message, cause)
        self.platform = platform
        self.operation = operation
