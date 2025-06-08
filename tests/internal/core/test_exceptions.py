"""Test suite for custom exception classes in the TJD-Toolkit.

This module contains comprehensive test coverage for all exception classes
defined in internal.core.exceptions, including inheritance hierarchies,
initialization behavior, and integration scenarios.

The test suite validates:
    - Proper exception instantiation and attribute assignment
    - Inheritance relationships and exception catching behavior
    - Logging integration and debug output
    - Edge cases and parameter validation
    - Module exports and public interface compliance

Example:
    Run the test suite with pytest:
        $ pytest test_exceptions.py -v
"""

import logging
from unittest.mock import patch

import pytest

from internal.core.exceptions import (
    TJDError,
    ConfigurationError,
    OperationError,
    PlatformError,
    ValidationError,
    GUIError,
    FileOperationError,
    JSONParsingError,
    FontError,
    ThemeError,
    WindowError,
    ViewError,
    NavigationError,
    HomeViewError,
    ToolViewError,
)


class TestTJDError:
    """Test suite for the base TJDError exception class.

    This class tests the foundational TJDError exception, which serves
    as the base class for all custom exceptions in the TJD-Toolkit.
    Tests cover basic instantiation, cause handling, inheritance,
    and logging behavior.
    """

    def test_basic_instantiation(self):
        """Test basic creation with just message parameter."""
        error = TJDError("Test error message")
        assert error.message == "Test error message"
        assert error.cause is None
        assert str(error) == "Test error message"

    def test_instantiation_with_cause(self):
        """Test creation with cause parameter for exception chaining."""
        original_error = ValueError("Original error")
        error = TJDError("Test error message", cause=original_error)
        assert error.message == "Test error message"
        assert error.cause == original_error
        assert str(error) == "Test error message"

    def test_inheritance(self):
        """Test that TJDError properly inherits from Exception."""
        error = TJDError("Test")
        assert isinstance(error, Exception)

    @patch("internal.core.exceptions.logger")
    def test_logging_without_cause(self, mock_logger):
        """Test debug logging occurs on creation without cause.

        Args:
            mock_logger: Mocked logger instance for testing logging calls.
        """
        TJDError("Test message")
        mock_logger.debug.assert_called_once_with("TJDError created: Test message", exc_info=False)

    @patch("internal.core.exceptions.logger")
    def test_logging_with_cause(self, mock_logger):
        """Test debug logging occurs with cause parameter.

        Args:
            mock_logger: Mocked logger instance for testing logging calls.
        """
        cause = ValueError("Original cause")
        TJDError("Test message", cause=cause)
        mock_logger.debug.assert_called_once_with("TJDError created: Test message", exc_info=cause)

    def test_none_cause_handling(self):
        """Test that None cause is handled properly."""
        error = TJDError("Test message", cause=None)
        assert error.cause is None


class TestConfigurationError:
    """Test suite for ConfigurationError exception class.

    This class tests the ConfigurationError exception, which is used
    for configuration-related errors in the TJD-Toolkit. Tests cover
    inheritance from TJDError and basic functionality.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy from TJDError and Exception."""
        error = ConfigurationError("Config error")
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic ConfigurationError instantiation and attributes."""
        error = ConfigurationError("Missing config file")
        assert error.message == "Missing config file"
        assert str(error) == "Missing config file"

    def test_with_cause(self):
        """Test ConfigurationError creation with exception chaining."""
        cause = FileNotFoundError("File not found")
        error = ConfigurationError("Config missing", cause=cause)
        assert error.cause == cause


class TestOperationError:
    """Test suite for OperationError exception class.

    This class tests the OperationError exception, which provides
    context about failed operations. Tests cover operation naming,
    message formatting, and inheritance behavior.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy from TJDError and Exception."""
        error = OperationError("test_op", "Test error")
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_operation_context(self):
        """Test operation context inclusion in error message."""
        error = OperationError("save_file", "Permission denied")
        assert error.operation == "save_file"
        assert error.message == "save_file failed: Permission denied"
        assert str(error) == "save_file failed: Permission denied"

    def test_with_cause(self):
        """Test OperationError creation with exception chaining."""
        cause = IOError("IO error")
        error = OperationError("read_file", "Cannot read", cause=cause)
        assert error.operation == "read_file"
        assert error.cause == cause
        assert "read_file failed: Cannot read" in str(error)

    def test_empty_operation_name(self):
        """Test behavior with empty operation name."""
        error = OperationError("", "Failed")
        assert error.operation == ""
        assert error.message == " failed: Failed"


class TestPlatformError:
    """Test suite for PlatformError exception class.

    This class tests the PlatformError exception, which provides
    context about platform-specific operations and failures.
    Tests cover platform and operation context handling.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy from TJDError and Exception."""
        error = PlatformError("Platform specific error")
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic PlatformError instantiation and attributes."""
        error = PlatformError("Privilege escalation failed")
        assert error.message == "Privilege escalation failed"
        assert error.platform is None
        assert error.operation is None

    def test_with_platform_and_operation(self):
        """Test PlatformError creation with platform and operation context."""
        error = PlatformError("Failed to elevate", platform="windows", operation="runas")
        assert error.message == "Failed to elevate"
        assert error.platform == "windows"
        assert error.operation == "runas"

    def test_with_cause(self):
        """Test PlatformError creation with exception chaining."""
        cause = PermissionError("Access denied")
        error = PlatformError("Elevation failed", platform="linux", operation="sudo", cause=cause)
        assert error.platform == "linux"
        assert error.operation == "sudo"
        assert error.cause == cause

    def test_none_platform_and_operation(self):
        """Test explicit None platform and operation handling."""
        error = PlatformError("Error", platform=None, operation=None)
        assert error.platform is None
        assert error.operation is None


class TestValidationError:
    """Test suite for ValidationError exception class.

    This class tests the ValidationError exception, which provides
    context about validation failures including field and value
    information. Tests cover field/value handling and inheritance.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy from TJDError and Exception."""
        error = ValidationError("Invalid data")
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic ValidationError instantiation and attributes."""
        error = ValidationError("Invalid email format")
        assert error.message == "Invalid email format"
        assert error.field is None
        assert error.value is None

    def test_with_field_and_value(self):
        """Test ValidationError creation with field and value context."""
        error = ValidationError("Invalid email", field="email", value="invalid-email")
        assert error.message == "Invalid email"
        assert error.field == "email"
        assert error.value == "invalid-email"

    def test_with_cause(self):
        """Test ValidationError creation with exception chaining."""
        cause = TypeError("Type error")
        error = ValidationError("Type mismatch", field="age", value="not_a_number", cause=cause)
        assert error.field == "age"
        assert error.value == "not_a_number"
        assert error.cause == cause

    def test_none_field_and_value(self):
        """Test explicit None field and value handling."""
        error = ValidationError("Error", field=None, value=None)
        assert error.field is None
        assert error.value is None


class TestGUIError:
    """Test suite for GUIError exception class.

    This class tests the GUIError exception, which serves as the base
    class for all GUI-related errors in the TJD-Toolkit. Tests cover
    inheritance from TJDError and basic functionality.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy from TJDError and Exception."""
        error = GUIError("GUI operation failed")
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic GUIError instantiation and attributes."""
        error = GUIError("Failed to update layout")
        assert error.message == "Failed to update layout"
        assert str(error) == "Failed to update layout"

    def test_with_cause(self):
        """Test GUIError creation with exception chaining."""
        cause = RuntimeError("Runtime error")
        error = GUIError("GUI error", cause=cause)
        assert error.cause == cause


class TestFileOperationError:
    """Test suite for FileOperationError exception class.

    This class tests the FileOperationError exception, which extends
    OperationError to provide file-specific context. Tests cover
    file path handling and inheritance from OperationError.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy through OperationError to TJDError."""
        error = FileOperationError("read", "Permission denied")
        assert isinstance(error, OperationError)
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic FileOperationError instantiation and attributes."""
        error = FileOperationError("write", "Disk full")
        assert error.operation == "write"
        assert error.message == "write failed: Disk full"
        assert error.file_path is None

    def test_with_file_path(self):
        """Test FileOperationError creation with file path context."""
        error = FileOperationError("delete", "Not found", file_path="/tmp/test.txt")
        assert error.operation == "delete"
        assert error.file_path == "/tmp/test.txt"
        assert "delete failed: Not found" in str(error)

    def test_with_all_parameters(self):
        """Test FileOperationError with all available parameters."""
        cause = OSError("OS error")
        error = FileOperationError(
            "create", "Permission denied", file_path="/etc/config", cause=cause
        )
        assert error.operation == "create"
        assert error.file_path == "/etc/config"
        assert error.cause == cause

    def test_none_file_path(self):
        """Test explicit None file path handling."""
        error = FileOperationError("read", "Error", file_path=None)
        assert error.file_path is None


class TestJSONParsingError:
    """Test suite for JSONParsingError exception class.

    This class tests the JSONParsingError exception, which extends
    ConfigurationError for JSON-specific parsing failures. Tests
    cover inheritance and integration with standard JSON exceptions.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy through ConfigurationError to TJDError."""
        error = JSONParsingError("Invalid JSON")
        assert isinstance(error, ConfigurationError)
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic JSONParsingError instantiation and attributes."""
        error = JSONParsingError("Malformed JSON syntax")
        assert error.message == "Malformed JSON syntax"
        assert str(error) == "Malformed JSON syntax"

    def test_with_cause(self):
        """Test JSONParsingError creation with JSON decode exception chaining."""
        import json

        cause = json.JSONDecodeError("Invalid", "doc", 0)
        error = JSONParsingError("JSON parse failed", cause=cause)
        assert error.cause == cause


class TestFontError:
    """Test suite for FontError exception class.

    This class tests the FontError exception, which extends GUIError
    for font-specific operations. Tests cover font name and path
    handling along with inheritance behavior.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy through GUIError to TJDError."""
        error = FontError("Font loading failed")
        assert isinstance(error, GUIError)
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic FontError instantiation and attributes."""
        error = FontError("Failed to load font")
        assert error.message == "Failed to load font"
        assert error.font_name is None
        assert error.font_path is None

    def test_with_font_name(self):
        """Test FontError creation with font name context."""
        error = FontError("Font not found", font_name="NotoSans")
        assert error.message == "Font not found"
        assert error.font_name == "NotoSans"
        assert error.font_path is None

    def test_with_font_path(self):
        """Test FontError creation with font path context."""
        error = FontError("Cannot read font file", font_path="/fonts/custom.ttf")
        assert error.message == "Cannot read font file"
        assert error.font_name is None
        assert error.font_path == "/fonts/custom.ttf"

    def test_with_all_parameters(self):
        """Test FontError with all available parameters."""
        cause = FileNotFoundError("File not found")
        error = FontError(
            "Font loading failed", font_name="Arial", font_path="/fonts/arial.ttf", cause=cause
        )
        assert error.font_name == "Arial"
        assert error.font_path == "/fonts/arial.ttf"
        assert error.cause == cause

    def test_none_font_attributes(self):
        """Test explicit None font attributes handling."""
        error = FontError("Error", font_name=None, font_path=None)
        assert error.font_name is None
        assert error.font_path is None


class TestThemeError:
    """Test suite for ThemeError exception class.

    This class tests the ThemeError exception, which extends GUIError
    for theme-specific operations. Tests cover theme name and component
    handling along with inheritance behavior.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy through GUIError to TJDError."""
        error = ThemeError("Theme loading failed")
        assert isinstance(error, GUIError)
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic ThemeError instantiation and attributes."""
        error = ThemeError("Invalid theme mode")
        assert error.message == "Invalid theme mode"
        assert error.theme_name is None
        assert error.component is None

    def test_with_theme_name(self):
        """Test ThemeError creation with theme name context."""
        error = ThemeError("Theme not found", theme_name="dark")
        assert error.message == "Theme not found"
        assert error.theme_name == "dark"
        assert error.component is None

    def test_with_component(self):
        """Test ThemeError creation with component context."""
        error = ThemeError("Component styling failed", component="button")
        assert error.message == "Component styling failed"
        assert error.theme_name is None
        assert error.component == "button"

    def test_with_all_parameters(self):
        """Test ThemeError with all available parameters."""
        cause = ValueError("Invalid value")
        error = ThemeError(
            "Theme application failed", theme_name="custom", component="navbar", cause=cause
        )
        assert error.theme_name == "custom"
        assert error.component == "navbar"
        assert error.cause == cause

    def test_none_theme_attributes(self):
        """Test explicit None theme attributes handling."""
        error = ThemeError("Error", theme_name=None, component=None)
        assert error.theme_name is None
        assert error.component is None


class TestWindowError:
    """Test suite for WindowError exception class.

    This class tests the WindowError exception, which extends GUIError
    for window management operations. Tests cover window ID and property
    handling along with inheritance behavior.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy through GUIError to TJDError."""
        error = WindowError("Window operation failed")
        assert isinstance(error, GUIError)
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic WindowError instantiation and attributes."""
        error = WindowError("Failed to resize window")
        assert error.message == "Failed to resize window"
        assert error.window_id is None
        assert error.property_name is None

    def test_with_window_id(self):
        """Test WindowError creation with window ID context."""
        error = WindowError("Window not found", window_id="main_window")
        assert error.message == "Window not found"
        assert error.window_id == "main_window"
        assert error.property_name is None

    def test_with_property_name(self):
        """Test WindowError creation with property name context."""
        error = WindowError("Invalid property", property_name="width")
        assert error.message == "Invalid property"
        assert error.window_id is None
        assert error.property_name == "width"

    def test_with_all_parameters(self):
        """Test WindowError with all available parameters."""
        cause = AttributeError("Attribute error")
        error = WindowError(
            "Property update failed", window_id="dialog", property_name="height", cause=cause
        )
        assert error.window_id == "dialog"
        assert error.property_name == "height"
        assert error.cause == cause

    def test_none_window_attributes(self):
        """Test explicit None window attributes handling."""
        error = WindowError("Error", window_id=None, property_name=None)
        assert error.window_id is None
        assert error.property_name is None


class TestViewError:
    """Test suite for ViewError exception class.

    This class tests the ViewError exception, which extends GUIError
    for view handling operations. Tests cover route and view name
    handling along with inheritance behavior.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy through GUIError to TJDError."""
        error = ViewError("View loading failed")
        assert isinstance(error, GUIError)
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic ViewError instantiation and attributes."""
        error = ViewError("View not found")
        assert error.message == "View not found"
        assert error.route is None
        assert error.view_name is None

    def test_with_route(self):
        """Test ViewError creation with route context."""
        error = ViewError("Invalid route", route="/invalid")
        assert error.message == "Invalid route"
        assert error.route == "/invalid"
        assert error.view_name is None

    def test_with_view_name(self):
        """Test ViewError creation with view name context."""
        error = ViewError("View loading failed", view_name="settings")
        assert error.message == "View loading failed"
        assert error.route is None
        assert error.view_name == "settings"

    def test_with_all_parameters(self):
        """Test ViewError with all available parameters."""
        cause = ImportError("Import error")
        error = ViewError(
            "View initialization failed", route="/settings", view_name="SettingsView", cause=cause
        )
        assert error.route == "/settings"
        assert error.view_name == "SettingsView"
        assert error.cause == cause

    def test_none_view_attributes(self):
        """Test explicit None view attributes handling."""
        error = ViewError("Error", route=None, view_name=None)
        assert error.route is None
        assert error.view_name is None


class TestNavigationError:
    """Test suite for NavigationError exception class.

    This class tests the NavigationError exception, which extends GUIError
    for navigation operations. Tests cover route handling along with
    inheritance behavior.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy through GUIError to TJDError."""
        error = NavigationError("Navigation failed")
        assert isinstance(error, GUIError)
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic NavigationError instantiation and attributes."""
        error = NavigationError("Invalid route")
        assert error.message == "Invalid route"
        assert error.route is None

    def test_with_route(self):
        """Test NavigationError creation with route context."""
        error = NavigationError("Route not found", route="/invalid/path")
        assert error.message == "Route not found"
        assert error.route == "/invalid/path"

    def test_with_cause(self):
        """Test NavigationError creation with exception chaining."""
        cause = KeyError("Key error")
        error = NavigationError("Navigation failed", route="/error", cause=cause)
        assert error.route == "/error"
        assert error.cause == cause

    def test_none_route(self):
        """Test explicit None route handling."""
        error = NavigationError("Error", route=None)
        assert error.route is None


class TestHomeViewError:
    """Test suite for HomeViewError exception class.

    This class tests the HomeViewError exception, which extends ViewError
    for home view specific operations. Tests cover component handling along
    with inherited route and view name attributes from ViewError.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy through ViewError to GUIError to TJDError."""
        error = HomeViewError("Home view operation failed")
        assert isinstance(error, ViewError)
        assert isinstance(error, GUIError)
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic HomeViewError instantiation and attributes."""
        error = HomeViewError("Failed to initialize home view")
        assert error.message == "Failed to initialize home view"
        assert error.route is None
        assert error.view_name is None
        assert error.component is None

    def test_with_component(self):
        """Test HomeViewError creation with component context."""
        error = HomeViewError("Component loading failed", component="tools_grid")
        assert error.message == "Component loading failed"
        assert error.route is None
        assert error.view_name is None
        assert error.component == "tools_grid"

    def test_with_route(self):
        """Test HomeViewError creation with route context."""
        error = HomeViewError("Route handling failed", route="/home")
        assert error.message == "Route handling failed"
        assert error.route == "/home"
        assert error.view_name is None
        assert error.component is None

    def test_with_view_name(self):
        """Test HomeViewError creation with view name context."""
        error = HomeViewError("View loading failed", view_name="HomeView")
        assert error.message == "View loading failed"
        assert error.route is None
        assert error.view_name == "HomeView"
        assert error.component is None

    def test_with_route_and_component(self):
        """Test HomeViewError creation with route and component context."""
        error = HomeViewError("Navigation failed", route="/home", component="nav_bar")
        assert error.message == "Navigation failed"
        assert error.route == "/home"
        assert error.view_name is None
        assert error.component == "nav_bar"

    def test_with_all_parameters(self):
        """Test HomeViewError with all available parameters."""
        cause = RuntimeError("Runtime error")
        error = HomeViewError(
            "Home view initialization failed",
            route="/home",
            view_name="HomeView",
            component="tools_grid",
            cause=cause,
        )
        assert error.message == "Home view initialization failed"
        assert error.route == "/home"
        assert error.view_name == "HomeView"
        assert error.component == "tools_grid"
        assert error.cause == cause

    def test_with_cause(self):
        """Test HomeViewError creation with exception chaining."""
        cause = ValueError("Invalid component configuration")
        error = HomeViewError("Component setup failed", component="tools_grid", cause=cause)
        assert error.message == "Component setup failed"
        assert error.component == "tools_grid"
        assert error.cause == cause

    def test_none_home_view_attributes(self):
        """Test explicit None home view attributes handling."""
        error = HomeViewError("Error", route=None, view_name=None, component=None)
        assert error.route is None
        assert error.view_name is None
        assert error.component is None


class TestToolViewError:
    """Test suite for ToolViewError exception class.

    This class tests the ToolViewError exception, which extends ViewError
    for tool view specific operations. Tests cover component handling along
    with inherited route and view name attributes from ViewError.
    """

    def test_inheritance(self):
        """Test inheritance hierarchy through ViewError to GUIError to TJDError."""
        error = ToolViewError("Tool view operation failed")
        assert isinstance(error, ViewError)
        assert isinstance(error, GUIError)
        assert isinstance(error, TJDError)
        assert isinstance(error, Exception)

    def test_basic_functionality(self):
        """Test basic ToolViewError instantiation and attributes."""
        error = ToolViewError("Failed to initialize tool view")
        assert error.message == "Failed to initialize tool view"
        assert error.route is None
        assert error.view_name is None
        assert error.component is None

    def test_with_component(self):
        """Test ToolViewError creation with component context."""
        error = ToolViewError("Component loading failed", component="header")
        assert error.message == "Component loading failed"
        assert error.route is None
        assert error.view_name is None
        assert error.component == "header"

    def test_with_route(self):
        """Test ToolViewError creation with route context."""
        error = ToolViewError("Route handling failed", route="/tool")
        assert error.message == "Route handling failed"
        assert error.route == "/tool"
        assert error.view_name is None
        assert error.component is None

    def test_with_view_name(self):
        """Test ToolViewError creation with view name context."""
        error = ToolViewError("View loading failed", view_name="ToolView")
        assert error.message == "View loading failed"
        assert error.route is None
        assert error.view_name == "ToolView"
        assert error.component is None

    def test_with_route_and_component(self):
        """Test ToolViewError creation with route and component context."""
        error = ToolViewError("Navigation failed", route="/tool", component="nav_bar")
        assert error.message == "Navigation failed"
        assert error.route == "/tool"
        assert error.view_name is None
        assert error.component == "nav_bar"

    def test_with_all_parameters(self):
        """Test ToolViewError with all available parameters."""
        cause = RuntimeError("Runtime error")
        error = ToolViewError(
            "Tool view initialization failed",
            route="/tool",
            view_name="ToolView",
            component="header",
            cause=cause,
        )
        assert error.message == "Tool view initialization failed"
        assert error.route == "/tool"
        assert error.view_name == "ToolView"
        assert error.component == "header"
        assert error.cause == cause

    def test_with_cause(self):
        """Test ToolViewError creation with exception chaining."""
        cause = ValueError("Invalid component configuration")
        error = ToolViewError("Component setup failed", component="header", cause=cause)
        assert error.message == "Component setup failed"
        assert error.component == "header"
        assert error.cause == cause

    def test_none_tool_view_attributes(self):
        """Test explicit None tool view attributes handling."""
        error = ToolViewError("Error", route=None, view_name=None, component=None)
        assert error.route is None
        assert error.view_name is None
        assert error.component is None


class TestExceptionHierarchy:
    """Test suite for exception hierarchy and catching behavior.

    This class validates that the exception inheritance hierarchy
    works correctly and that exceptions can be caught by their
    base classes as expected. Critical for proper exception handling.
    """

    def test_exception_catching_hierarchy(self):
        """Test that derived exceptions can be caught by base classes."""
        # FileOperationError should be catchable as OperationError
        with pytest.raises(OperationError):
            raise FileOperationError("read", "test error")

        # JSONParsingError should be catchable as ConfigurationError
        with pytest.raises(ConfigurationError):
            raise JSONParsingError("test error")

        # HomeViewError should be catchable as ViewError
        with pytest.raises(ViewError):
            raise HomeViewError("test error")

        # ToolViewError should be catchable as ViewError
        with pytest.raises(ViewError):
            raise ToolViewError("test error")

        # All GUI exceptions should be catchable as GUIError
        gui_exceptions = [
            FontError("test"),
            ThemeError("test"),
            WindowError("test"),
            ViewError("test"),
            NavigationError("test"),
            HomeViewError("test"),
            ToolViewError("test"),
        ]

        for exc in gui_exceptions:
            with pytest.raises(GUIError):
                raise exc

        # All exceptions should be catchable as TJDError
        exceptions_to_test = [
            ConfigurationError("test"),
            OperationError("op", "test"),
            PlatformError("test"),
            ValidationError("test"),
            GUIError("test"),
            FileOperationError("read", "test"),
            JSONParsingError("test"),
            FontError("test"),
            ThemeError("test"),
            WindowError("test"),
            ViewError("test"),
            NavigationError("test"),
            HomeViewError("test"),
            ToolViewError("test"),
        ]

        for exc in exceptions_to_test:
            with pytest.raises(TJDError):
                raise exc

    def test_specific_exception_catching(self):
        """Test catching specific exception types and accessing attributes."""
        with pytest.raises(FileOperationError) as exc_info:
            raise FileOperationError("write", "disk full", "/tmp/file")
        assert exc_info.value.operation == "write"
        assert exc_info.value.file_path == "/tmp/file"

        with pytest.raises(FontError) as exc_info:
            raise FontError("font error", font_name="Arial", font_path="/fonts/arial.ttf")
        assert exc_info.value.font_name == "Arial"
        assert exc_info.value.font_path == "/fonts/arial.ttf"

        with pytest.raises(ThemeError) as exc_info:
            raise ThemeError("theme error", theme_name="dark", component="button")
        assert exc_info.value.theme_name == "dark"
        assert exc_info.value.component == "button"

        with pytest.raises(HomeViewError) as exc_info:
            raise HomeViewError(
                "home view error", route="/home", view_name="HomeView", component="tools_grid"
            )
        assert exc_info.value.route == "/home"
        assert exc_info.value.view_name == "HomeView"
        assert exc_info.value.component == "tools_grid"

        with pytest.raises(ToolViewError) as exc_info:
            raise ToolViewError(
                "tool view error", route="/tool", view_name="ToolView", component="header"
            )
        assert exc_info.value.route == "/tool"
        assert exc_info.value.view_name == "ToolView"
        assert exc_info.value.component == "header"


class TestModuleExports:
    """Test suite for module exports and public interface.

    This class validates that the exceptions module properly exports
    all expected exception classes and maintains a correct public
    interface through __all__ declaration.
    """

    def test_all_exports(self):
        """Test that __all__ contains all expected exception classes."""
        from internal.core.exceptions import __all__

        expected_exports = [
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
            "ToolViewError",
        ]

        assert set(__all__) == set(expected_exports)

    def test_logger_exists(self):
        """Test that module logger is properly configured."""
        import internal.core.exceptions

        assert hasattr(internal.core.exceptions, "logger")
        assert isinstance(internal.core.exceptions.logger, logging.Logger)


class TestExceptionIntegration:
    """Integration tests for exception usage scenarios.

    This class tests realistic exception usage patterns including
    exception chaining, logging integration, and complex error
    handling scenarios that might occur in production code.
    """

    def test_exception_chaining(self):
        """Test exception chaining in realistic error handling scenarios."""
        with pytest.raises(OperationError) as exc_info:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise OperationError("process_data", "Processing failed", cause=e)

        op_error = exc_info.value
        assert op_error.operation == "process_data"
        assert isinstance(op_error.cause, ValueError)
        assert str(op_error.cause) == "Original error"

    @patch("internal.core.exceptions.logger")
    def test_logging_integration(self, mock_logger):
        """Test that logging works throughout the exception hierarchy.

        Args:
            mock_logger: Mocked logger instance for testing logging calls.
        """
        ConfigurationError("Config error")
        ValidationError("Validation error")
        GUIError("GUI error")
        FontError("Font error")

        # All should trigger logging since they inherit from TJDError
        assert mock_logger.debug.call_count == 4

    def test_gui_error_scenario(self):
        """Test a realistic GUI error handling scenario."""
        # Simulate a theme loading error that cascades through components
        with pytest.raises(ThemeError) as exc_info:
            try:
                # Simulate font loading failure
                raise FileNotFoundError("Font file not found")
            except FileNotFoundError as e:
                raise ThemeError(
                    "Failed to apply theme",
                    theme_name="dark",
                    component="main_window",
                    cause=e,
                )

        error = exc_info.value
        assert error.theme_name == "dark"
        assert error.component == "main_window"
        assert isinstance(error.cause, FileNotFoundError)
        assert "Failed to apply theme" in str(error)

    def test_real_world_scenario(self):
        """Test a realistic error handling scenario with file operations."""
        # Simulate a file operation that fails
        with pytest.raises(FileOperationError) as exc_info:
            try:
                # Simulate file not found
                raise FileNotFoundError("No such file")
            except FileNotFoundError as e:
                raise FileOperationError(
                    "backup",
                    "Cannot backup missing file",
                    file_path="/config/app.json",
                    cause=e,
                )

        error = exc_info.value
        assert error.operation == "backup"
        assert error.file_path == "/config/app.json"
        assert isinstance(error.cause, FileNotFoundError)
        assert "backup failed" in str(error)


class TestParametrizedExceptions:
    """Parametrized tests for comprehensive exception testing.

    This class uses pytest's parametrization feature to efficiently
    test multiple exception types with various parameter combinations,
    ensuring consistent behavior across all exception classes.
    """

    @pytest.mark.parametrize(
        "exception_class,args,expected_attrs",
        [
            (TJDError, ("message",), {"message": "message", "cause": None}),
            (ConfigurationError, ("config error",), {"message": "config error"}),
            (
                OperationError,
                ("op", "msg"),
                {"operation": "op", "message": "op failed: msg"},
            ),
            (
                PlatformError,
                ("platform error",),
                {"message": "platform error", "platform": None},
            ),
            (
                ValidationError,
                ("invalid",),
                {"message": "invalid", "field": None, "value": None},
            ),
            (GUIError, ("gui error",), {"message": "gui error"}),
            (
                FileOperationError,
                ("read", "error"),
                {"operation": "read", "message": "read failed: error", "file_path": None},
            ),
            (JSONParsingError, ("json error",), {"message": "json error"}),
            (
                FontError,
                ("font error",),
                {"message": "font error", "font_name": None, "font_path": None},
            ),
            (
                ThemeError,
                ("theme error",),
                {"message": "theme error", "theme_name": None, "component": None},
            ),
            (
                WindowError,
                ("window error",),
                {"message": "window error", "window_id": None, "property_name": None},
            ),
            (
                ViewError,
                ("view error",),
                {"message": "view error", "route": None, "view_name": None},
            ),
            (
                NavigationError,
                ("nav error",),
                {"message": "nav error", "route": None},
            ),
            (
                HomeViewError,
                ("home view error",),
                {"message": "home view error", "route": None, "view_name": None, "component": None},
            ),
            (
                ToolViewError,
                ("tool view error",),
                {"message": "tool view error", "route": None, "view_name": None, "component": None},
            ),
        ],
    )
    def test_exception_creation(self, exception_class, args, expected_attrs):
        """Test the creation and attribute values of various exception types.

        Args:
            exception_class: The exception class to test.
            args: Arguments to pass to the exception constructor.
            expected_attrs: Dictionary of expected attribute values.
        """
        exc = exception_class(*args)
        for attr, expected_value in expected_attrs.items():
            assert getattr(exc, attr) == expected_value
        assert isinstance(exc, TJDError)
        assert isinstance(exc, Exception)
