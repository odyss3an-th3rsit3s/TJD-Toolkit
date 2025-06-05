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
    "PlatformError",
    "ValidationError",
    "GUIError",
    "FileOperationError",
    "JSONParsingError",
    "FontError",
    "ThemeError",
    "WindowError",
    "ViewError",
    "NavigationError",
    "HomeViewError",
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


class GUIError(TJDError):
    """Signal GUI-related operation failures.

    Base class for GUI-specific exceptions including theme configuration,
    window management, and view handling errors.

    Example:
        >>> try:
        ...     raise GUIError("Failed to update layout")
        ... except GUIError as e:
        ...     print(f"GUI error: {e}")
        GUI error: Failed to update layout
    """


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


class FontError(GUIError):
    """Signal font-related operation failures.

    Indicate failures in font operations including loading font files,
    font registration, and font configuration issues.

    Attributes:
        font_name (Optional[str]): Name of the font that caused the error.
        font_path (Optional[str]): Path to the font file that caused the error.

    Example:
        >>> try:
        ...     raise FontError("Failed to load font", font_name="NotoSans")
        ... except FontError as e:
        ...     print(f"Font error: {e}")
        Font error: Failed to load font
    """

    def __init__(
        self,
        message: str,
        font_name: Optional[str] = None,
        font_path: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize font error with context.

        Args:
            message (str): Description of the font error.
            font_name (Optional[str]): Name of the font. Defaults to None.
            font_path (Optional[str]): Path to the font file. Defaults to None.
            cause (Optional[Exception]): Original error. Defaults to None.
        """
        super().__init__(message, cause)
        self.font_name = font_name
        self.font_path = font_path


class ThemeError(GUIError):
    """Signal theme configuration and application failures.

    Indicate failures in theme-related operations including loading themes,
    applying styles, and managing font settings.

    Attributes:
        theme_name (Optional[str]): Name of the theme that caused the error.
        component (Optional[str]): UI component where the error occurred.

    Example:
        >>> try:
        ...     raise ThemeError("Invalid theme mode", theme_name="dark")
        ... except ThemeError as e:
        ...     print(f"Theme error: {e}")
        Theme error: Invalid theme mode
    """

    def __init__(
        self,
        message: str,
        theme_name: Optional[str] = None,
        component: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize theme error with context.

        Args:
            message (str): Description of the theme error.
            theme_name (Optional[str]): Name of the theme. Defaults to None.
            component (Optional[str]): Affected UI component. Defaults to None.
            cause (Optional[Exception]): Original error. Defaults to None.
        """
        super().__init__(message, cause)
        self.theme_name = theme_name
        self.component = component


class WindowError(GUIError):
    """Signal window management operation failures.

    Indicate failures in window operations including resizing,
    state changes, and configuration persistence.

    Attributes:
        window_id (Optional[str]): Identifier of the affected window.
        property_name (Optional[str]): Name of the window property.

    Example:
        >>> try:
        ...     raise WindowError("Failed to resize window", property_name="width")
        ... except WindowError as e:
        ...     print(f"Window error: {e}")
        Window error: Failed to resize window
    """

    def __init__(
        self,
        message: str,
        window_id: Optional[str] = None,
        property_name: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize window error with context.

        Args:
            message (str): Description of the window error.
            window_id (Optional[str]): Window identifier. Defaults to None.
            property_name (Optional[str]): Affected property. Defaults to None.
            cause (Optional[Exception]): Original error. Defaults to None.
        """
        super().__init__(message, cause)
        self.window_id = window_id
        self.property_name = property_name


class ViewError(GUIError):
    """Signal view handling and navigation failures.

    Indicate failures in view operations including loading views,
    route changes, and view stack management.

    Attributes:
        route (Optional[str]): Route where the error occurred.
        view_name (Optional[str]): Name of the affected view.

    Example:
        >>> try:
        ...     raise ViewError("View not found", route="/invalid")
        ... except ViewError as e:
        ...     print(f"View error: {e}")
        View error: View not found
    """

    def __init__(
        self,
        message: str,
        route: Optional[str] = None,
        view_name: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize view error with context.

        Args:
            message (str): Description of the view error.
            route (Optional[str]): Associated route. Defaults to None.
            view_name (Optional[str]): Name of the view. Defaults to None.
            cause (Optional[Exception]): Original error. Defaults to None.
        """
        super().__init__(message, cause)
        self.route = route
        self.view_name = view_name


class NavigationError(GUIError):
    """Signal navigation and routing failures.

    Indicate failures in application navigation including invalid routes,
    view loading errors, and navigation state inconsistencies.

    Attributes:
        route (Optional[str]): The route that caused the error.

    Example:
        >>> try:
        ...     raise NavigationError("Invalid route", route="/invalid/path")
        ... except NavigationError as e:
        ...     print(f"Navigation error: {e}")
        Navigation error: Invalid route
    """

    def __init__(
        self, message: str, route: Optional[str] = None, cause: Optional[Exception] = None
    ) -> None:
        """Initialize navigation error with context.

        Args:
            message (str): Description of the navigation failure.
            route (Optional[str]): The problematic route. Defaults to None.
            cause (Optional[Exception]): Original error. Defaults to None.
        """
        super().__init__(message, cause)
        self.route = route


class HomeViewError(ViewError):
    """Signal home view specific operation failures.

    Indicate failures specific to home view operations including UI setup,
    tool loading, navigation initialization, and grid creation errors.
    Inherits from ViewError to maintain the view error hierarchy.

    Attributes:
        route (Optional[str]): Route where the error occurred.
        view_name (Optional[str]): Name of the affected view.
        component (Optional[str]): Specific home view component that failed.

    Example:
        >>> try:
        ...     raise HomeViewError("Failed to create tools grid", component="tools_grid")
        ... except HomeViewError as e:
        ...     print(f"Home view error: {e}")
        Home view error: Failed to create tools grid
    """

    def __init__(
        self,
        message: str,
        route: Optional[str] = None,
        view_name: Optional[str] = None,
        component: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize home view error with context.

        Args:
            message (str): Description of the home view error.
            route (Optional[str]): Associated route. Defaults to None.
            view_name (Optional[str]): Name of the view. Defaults to None.
            component (Optional[str]): Failed component. Defaults to None.
            cause (Optional[Exception]): Original error. Defaults to None.
        """
        super().__init__(message, route, view_name, cause)
        self.component = component
