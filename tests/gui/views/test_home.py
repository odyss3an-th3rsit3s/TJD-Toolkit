"""Test suite for the HomeView module in the TJD-Toolkit.

This module provides comprehensive test coverage for the HomeView class
and its component methods, including UI setup, navigation handling,
loading overlay management, and error handling across different scenarios.

The test suite covers:
    - HomeView initialization and component setup
    - UI component creation and management
    - Loading overlay functionality
    - Navigation and tool routing
    - Card interaction and hover effects
    - Available and coming soon tool card creation
    - Comprehensive error handling and recovery
    - Integration workflows and edge cases

Example:
    Run the test suite with pytest:
        $ pytest test_home.py -v
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from gui.views.home import HomeView
from internal.core.exceptions import HomeViewError


class MockPageClass:
    """Mock Page class that can be used with isinstance checks."""

    pass


@pytest.fixture(autouse=True)
def mock_flet_dependency():
    """Mock the flet module while keeping internal components real.

    Automatically applied to all tests to ensure flet UI framework
    is properly mocked without affecting internal logic and exception
    handling.

    Yields:
        MagicMock: Mocked flet module with UI components configured.
    """
    with patch("gui.views.home.ft") as mock_ft:
        # Configure flet components
        mock_ft.View = MagicMock()
        mock_ft.Text = MagicMock()
        mock_ft.Container = MagicMock()
        mock_ft.Stack = MagicMock()
        mock_ft.Column = MagicMock()
        mock_ft.ProgressRing = MagicMock()
        mock_ft.GridView = MagicMock()
        mock_ft.Card = MagicMock()
        mock_ft.Icon = MagicMock()
        mock_ft.Colors = MagicMock()
        mock_ft.CrossAxisAlignment = MagicMock()
        mock_ft.MainAxisAlignment = MagicMock()
        mock_ft.FontWeight = MagicMock()
        mock_ft.Icons = MagicMock()
        mock_ft.alignment = MagicMock()
        mock_ft.padding = MagicMock()

        mock_ft.Page = MockPageClass

        yield mock_ft


@pytest.fixture
def mock_page():
    """Create mock Flet page object for testing.

    Provides a standardized mock page object with all necessary
    attributes initialized for consistent testing across the suite.

    Returns:
        MagicMock: Mock page object with required attributes set.
    """
    page = MagicMock(spec=MockPageClass)
    page.go = MagicMock()
    page.update = MagicMock()
    return page


@pytest.fixture
def reset_global_state():
    """Reset any global state before each test.

    Ensures test isolation by resetting any module-level state
    that might persist between test executions.

    Yields:
        None: Context manager yields control to test execution.
    """
    # Reset any cached state if present
    yield


@pytest.fixture
def mock_fontify():
    """Mock the fontify utility function.

    Provides consistent mocking of the fontify function used
    throughout HomeView for text styling.

    Yields:
        MagicMock: Mocked fontify function.
    """
    with patch("gui.views.home.fontify") as mock:
        mock.return_value = MagicMock()
        yield mock


class TestHomeViewInitialization:
    """Test HomeView initialization and core setup functionality.

    This class contains tests for basic HomeView operations including
    initialization, component setup, and core property access functionality.
    """

    @patch("gui.views.home.fontify")
    def test_initialization_success_with_valid_page(
        self, mock_fontify, mock_page, reset_global_state
    ):
        """Test successful HomeView initialization with valid page.

        Validates that HomeView initializes correctly with all components
        properly set up and configured using real exception classes.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()

        # Act
        home_view = HomeView(mock_page)

        # Assert
        assert home_view.page == mock_page
        assert home_view.route == "/"
        assert home_view.title == "TJD Toolkit - Homepage"
        assert hasattr(home_view, "_loading_text")
        assert hasattr(home_view, "_loading_overlay")
        assert hasattr(home_view, "controls")

    def test_initialization_none_page_raises_error(self, reset_global_state):
        """Test HomeView initialization with None page raises HomeViewError.

        Validates that HomeViewError is properly raised and has correct
        attributes when page parameter is None.

        Args:
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when page is None.
        """
        # Act & Assert
        with pytest.raises(HomeViewError) as exc_info:
            HomeView(None)

        # Verify HomeViewError attributes
        error = exc_info.value
        assert "Cannot initialize HomeView with None page reference" in error.message
        assert hasattr(error, "cause")

    def test_available_tools_class_attribute(self):
        """Test that AVAILABLE_TOOLS class attribute is properly defined.

        Validates that the class-level constant is correctly configured
        and contains expected tool entries with proper structure.
        """
        # Assert
        assert hasattr(HomeView, "AVAILABLE_TOOLS")
        assert isinstance(HomeView.AVAILABLE_TOOLS, dict)
        assert "Feature Eins" in HomeView.AVAILABLE_TOOLS

        # Verify structure of available tools
        tool_config = HomeView.AVAILABLE_TOOLS["Feature Eins"]
        assert "description" in tool_config
        assert "icon" in tool_config
        assert "color" in tool_config

    def test_coming_soon_tools_class_attribute(self):
        """Test that COMING_SOON_TOOLS class attribute is properly defined.

        Validates that the class-level constant is correctly configured
        and contains expected tool entries.
        """
        # Assert
        assert hasattr(HomeView, "COMING_SOON_TOOLS")
        assert isinstance(HomeView.COMING_SOON_TOOLS, list)
        assert "Feature Zwei" in HomeView.COMING_SOON_TOOLS
        assert len(HomeView.COMING_SOON_TOOLS) >= 1


class TestHomeViewUIComponents:
    """Test HomeView UI component creation functionality.

    This class contains comprehensive tests for UI component setup,
    including header creation, tools grid setup, and loading overlay
    management with proper error handling.
    """

    @patch("gui.views.home.fontify")
    def test_create_loading_overlay_success(
        self, mock_fontify, mock_flet_dependency, mock_page, reset_global_state
    ):
        """Test successful creation of loading overlay component.

        Validates that loading overlay is created with proper components
        and configuration using the mocked Flet components.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        # Act
        result = home_view._create_loading_overlay()

        # Assert
        assert result is not None
        mock_flet_dependency.Stack.assert_called()

    @patch("gui.views.home.fontify")
    def test_create_loading_overlay_component_error(
        self, mock_fontify, mock_flet_dependency, mock_page, reset_global_state
    ):
        """Test loading overlay creation handles component errors.

        Validates that HomeViewError is properly raised when UI component
        creation fails during loading overlay setup.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when component creation fails.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)
        mock_flet_dependency.Stack.side_effect = RuntimeError("Component creation failed")

        # Act & Assert
        with pytest.raises(HomeViewError) as exc_info:
            home_view._create_loading_overlay()

        error = exc_info.value
        assert "Failed to create loading overlay" in error.message
        assert isinstance(error.cause, RuntimeError)

    @patch("gui.views.home.fontify")
    def test_create_header_success_workflow(
        self, mock_fontify, mock_flet_dependency, mock_page, reset_global_state
    ):
        """Test successful header creation workflow.

        Validates that header component is created with proper styling
        and text components using fontify utility and the mocked Flet components.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        # Act
        result = home_view._create_header()

        # Assert
        assert result is not None
        mock_flet_dependency.Container.assert_called()
        assert mock_fontify.call_count >= 2  # Title and subtitle

    @patch("gui.views.home.fontify")
    def test_create_header_fontify_error_handling(
        self, mock_fontify, mock_page, reset_global_state
    ):
        """Test header creation handles fontify errors appropriately.

        Validates that HomeViewError is properly raised when fontify
        utility fails during header creation.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when fontify fails.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        font_error = RuntimeError("Font loading failed")
        mock_fontify.side_effect = font_error

        # Act & Assert
        with pytest.raises(HomeViewError) as exc_info:
            home_view._create_header()

        error = exc_info.value
        assert "Failed to create header" in error.message
        assert error.cause == font_error

    @patch("gui.views.home.fontify")
    def test_create_tools_grid_success_with_all_cards(
        self, mock_fontify, mock_flet_dependency, mock_page, reset_global_state
    ):
        """Test successful tools grid creation with available and coming soon cards.

        Validates that tools grid is created with proper card components
        for both available tools and coming soon tools using the mocked Flet components.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        with (
            patch.object(home_view, "_create_tool_card") as mock_tool_card,
            patch.object(home_view, "_create_coming_soon_card") as mock_coming_soon_card,
        ):

            mock_tool_card.return_value = MagicMock()
            mock_coming_soon_card.return_value = MagicMock()

            # Act
            result = home_view._create_tools_grid()

            # Assert
            assert result is not None
            mock_flet_dependency.GridView.assert_called()

            # Verify available tool card creation
            for tool_name in HomeView.AVAILABLE_TOOLS.keys():
                tool_config = HomeView.AVAILABLE_TOOLS[tool_name]
                mock_tool_card.assert_any_call(
                    tool_name, tool_config["description"], tool_config["icon"], tool_config["color"]
                )

            # Verify coming soon card creation
            for tool in HomeView.COMING_SOON_TOOLS:
                mock_coming_soon_card.assert_any_call(tool)

    @patch("gui.views.home.fontify")
    def test_create_tools_grid_available_tool_card_error(
        self, mock_fontify, mock_page, reset_global_state
    ):
        """Test tools grid creation handles available tool card creation errors.

        Validates that HomeViewError is properly raised when available tool card creation
        fails for any tool in the grid.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when available tool card creation fails.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        with (
            patch.object(home_view, "_create_tool_card") as mock_tool_card,
            patch.object(home_view, "_create_coming_soon_card") as mock_coming_soon_card,
        ):

            card_error = RuntimeError("Available tool card creation failed")
            mock_tool_card.side_effect = card_error
            mock_coming_soon_card.return_value = MagicMock()

            # Act & Assert
            with pytest.raises(HomeViewError) as exc_info:
                home_view._create_tools_grid()

            error = exc_info.value
            assert "Failed to create card for" in error.message
            assert error.component == "available_tool_card"
            assert error.cause == card_error

    @patch("gui.views.home.fontify")
    def test_create_tools_grid_coming_soon_card_error(
        self, mock_fontify, mock_page, reset_global_state
    ):
        """Test tools grid creation handles coming soon card creation errors.

        Validates that HomeViewError is properly raised when coming soon card creation
        fails for any tool in the grid.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when coming soon card creation fails.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        with (
            patch.object(home_view, "_create_tool_card") as mock_tool_card,
            patch.object(home_view, "_create_coming_soon_card") as mock_coming_soon_card,
        ):

            mock_tool_card.return_value = MagicMock()
            card_error = RuntimeError("Coming soon card creation failed")
            mock_coming_soon_card.side_effect = card_error

            # Act & Assert
            with pytest.raises(HomeViewError) as exc_info:
                home_view._create_tools_grid()

            error = exc_info.value
            assert "Failed to create card for" in error.message
            assert error.component == "coming_soon_tool_card"
            assert error.cause == card_error

    @patch("gui.views.home.fontify")
    def test_create_tools_grid_general_exception_handling(
        self, mock_fontify, mock_flet_dependency, mock_page, reset_global_state
    ):
        """Test tools grid creation handles general exceptions during GridView creation.

        Validates that HomeViewError is properly raised when GridView creation
        fails with non-HomeViewError exceptions during grid setup.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when GridView creation fails.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        # Mock ft.GridView to raise a general exception during creation
        grid_error = RuntimeError("GridView creation failed")
        mock_flet_dependency.GridView.side_effect = grid_error

        # Act & Assert
        with pytest.raises(HomeViewError) as exc_info:
            home_view._create_tools_grid()

        error = exc_info.value
        assert "Failed to create tools grid" in error.message
        assert error.component == "tools_grid"
        assert error.cause == grid_error

    @patch("gui.views.home.fontify")
    def test_setup_ui_general_exception_handling(
        self, mock_fontify, mock_flet_dependency, mock_page, reset_global_state
    ):
        """Test setup_ui handles general exceptions during layout creation.

        Validates that HomeViewError is properly raised when layout creation
        fails with non-HomeViewError exceptions during UI setup.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when layout creation fails.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        # Mock ft.Stack to raise a general exception during layout creation
        layout_error = RuntimeError("Layout creation failed")
        mock_flet_dependency.Stack.side_effect = layout_error

        # Act & Assert
        with pytest.raises(HomeViewError) as exc_info:
            home_view.setup_ui()

        error = exc_info.value
        assert "Failed to setup UI components" in error.message
        assert error.component == "main_layout"
        assert error.cause == layout_error


class TestHomeViewLoadingManagement:
    """Test HomeView loading overlay management functionality.

    This class contains tests for loading overlay display, hiding,
    and message updating operations with comprehensive error handling.
    """

    @patch("gui.views.home.fontify")
    def test_show_loading_success_workflow(self, mock_fontify, mock_page, reset_global_state):
        """Test successful loading overlay display workflow.

        Validates that loading overlay is properly shown with correct
        message and visibility state.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        home_view.update = MagicMock()

        message = "Loading application..."

        # Act
        home_view._show_loading(message)

        # Assert
        assert home_view._loading_text.value == message
        assert home_view._loading_overlay.visible is True
        home_view.update.assert_called_once()

    @patch("gui.views.home.fontify")
    def test_show_loading_update_error_handling(self, mock_fontify, mock_page, reset_global_state):
        """Test loading display handles update errors appropriately.

        Validates that HomeViewError is properly raised when page update
        fails during loading overlay display.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when update fails.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        update_error = RuntimeError("Update failed")
        home_view.update = MagicMock(side_effect=update_error)

        # Act & Assert
        with pytest.raises(HomeViewError) as exc_info:
            home_view._show_loading("test message")

        error = exc_info.value
        assert "Failed to display loading overlay" in error.message
        assert error.cause == update_error

    @patch("gui.views.home.fontify")
    def test_hide_loading_success_workflow(self, mock_fontify, mock_page, reset_global_state):
        """Test successful loading overlay hiding workflow.

        Validates that loading overlay is properly hidden with correct
        visibility state and page update.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        home_view.update = MagicMock()

        # Act
        home_view._hide_loading()

        # Assert
        assert home_view._loading_overlay.visible is False
        home_view.update.assert_called_once()

    @patch("gui.views.home.fontify")
    def test_hide_loading_general_exception_handling(
        self, mock_fontify, mock_page, reset_global_state
    ):
        """Test loading overlay hiding handles general exceptions during update.

        Validates that HomeViewError is properly raised when update operation
        fails with general exceptions during loading overlay hiding.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when update fails during hiding.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        # Mock update to raise a general exception
        update_error = RuntimeError("Update operation failed")
        home_view.update = MagicMock(side_effect=update_error)

        # Act & Assert
        with pytest.raises(HomeViewError) as exc_info:
            home_view._hide_loading()

        error = exc_info.value
        assert "Failed to hide loading overlay" in error.message
        assert error.component == "loading_hide"
        assert error.cause == update_error

    @pytest.mark.parametrize(
        "loading_message,expected_behavior",
        [
            ("Loading tools...", "sets_message_and_shows"),
            ("", "handles_empty_message"),
            ("Very long loading message that might overflow", "handles_long_message"),
            ("Loading with special chars: éñ中文", "handles_unicode"),
        ],
    )
    @patch("gui.views.home.fontify")
    def test_show_loading_message_variations(
        self, mock_fontify, loading_message, expected_behavior, mock_page, reset_global_state
    ):
        """Test loading display with various message formats.

        Validates that loading overlay handles different message types
        and formats correctly using parametrized testing.

        Args:
            mock_fontify: Mocked fontify utility.
            loading_message (str): Loading message to test.
            expected_behavior (str): Expected behavior description.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        # Act
        home_view._show_loading(loading_message)

        # Assert
        assert home_view._loading_text.value == loading_message
        assert home_view._loading_overlay.visible is True


class TestHomeViewNavigationManagement:
    """Test HomeView navigation and routing functionality.

    This class contains comprehensive tests for navigation handling,
    tool routing, parameter validation, and error recovery scenarios.
    """

    @patch("gui.views.home.fontify")
    def test_navigate_to_tool_success_workflow(self, mock_fontify, mock_page, reset_global_state):
        """Test successful navigation to tool workflow.

        Validates that navigation properly displays loading overlay
        and navigates to the specified route.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)
        route = "/password-generator"
        tool_name = "Password Generator"

        with patch.object(home_view, "_show_loading") as mock_show_loading:
            # Act
            home_view._navigate_to_tool(route, tool_name)

            # Assert
            mock_show_loading.assert_called_once_with(f"Loading {tool_name} ...")
            mock_page.go.assert_called_once_with(route)

    @pytest.mark.parametrize(
        "route,tool_name,error_condition",
        [
            ("", "Tool", "empty_route"),
            ("/valid", "", "empty_tool_name"),
            (None, "Tool", "none_route"),
            ("/valid", None, "none_tool_name"),
            ("", "", "both_empty"),
        ],
    )
    @patch("gui.views.home.fontify")
    def test_navigate_to_tool_parameter_validation(
        self, mock_fontify, route, tool_name, error_condition, mock_page, reset_global_state
    ):
        """Test navigation parameter validation with various invalid inputs.

        Validates that HomeViewError is properly raised for invalid
        route and tool name combinations using parametrized testing.

        Args:
            mock_fontify: Mocked fontify utility.
            route (str): Navigation route to test.
            tool_name (str): Tool name to test.
            error_condition (str): Error condition description.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception for invalid parameters.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        # Act & Assert
        with pytest.raises(HomeViewError) as exc_info:
            home_view._navigate_to_tool(route, tool_name)

        error = exc_info.value
        assert "Navigation requires valid route and tool name" in error.message

    @patch("gui.views.home.fontify")
    def test_navigate_to_tool_page_navigation_error(
        self, mock_fontify, mock_page, reset_global_state
    ):
        """Test navigation handles page.go errors appropriately.

        Validates that HomeViewError is properly raised when page.go
        fails and loading overlay is properly hidden.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when page.go fails.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)
        nav_error = RuntimeError("Navigation failed")
        mock_page.go.side_effect = nav_error
        tool_name = "Test Tool"

        with (
            patch.object(home_view, "_show_loading") as mock_show_loading,
            patch.object(home_view, "_hide_loading") as mock_hide_loading,
        ):

            # Act & Assert
            with pytest.raises(HomeViewError) as exc_info:
                home_view._navigate_to_tool("/test", tool_name)

            error = exc_info.value
            assert f"Failed to navigate to {tool_name}" in error.message
            assert error.cause == nav_error
            mock_show_loading.assert_called_once()
            mock_hide_loading.assert_called_once()

    @patch("gui.views.home.fontify")
    def test_navigate_to_tool_show_loading_error_recovery(
        self, mock_fontify, mock_page, reset_global_state
    ):
        """Test navigation handles HomeViewError from show_loading with proper recovery.

        Validates that when _show_loading raises HomeViewError, the navigation
        method properly hides loading overlay and re-raises the exception.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when show_loading fails.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        # Mock _show_loading to raise HomeViewError
        loading_error = HomeViewError(
            "Failed to display loading overlay",
            route=home_view.route,
            view_name="HomeView",
            component="loading_display",
        )

        with (
            patch.object(home_view, "_show_loading") as mock_show_loading,
            patch.object(home_view, "_hide_loading") as mock_hide_loading,
        ):

            mock_show_loading.side_effect = loading_error

            # Act & Assert
            with pytest.raises(HomeViewError) as exc_info:
                home_view._navigate_to_tool("/test-route", "Test Tool")

            # Verify the original HomeViewError is re-raised
            assert exc_info.value == loading_error
            # Verify loading overlay is hidden on error
            mock_hide_loading.assert_called_once()


class TestHomeViewCardInteraction:
    """Test HomeView card interaction and hover functionality.

    This class contains tests for card hover effects, event handling,
    and visual feedback mechanisms with proper error handling.
    """

    @pytest.mark.parametrize(
        "hover_data,expected_elevation",
        [
            ("true", 8),
            ("false", 2),
        ],
    )
    @patch("gui.views.home.fontify")
    def test_handle_card_hover_elevation_changes(
        self, mock_fontify, hover_data, expected_elevation, mock_page, reset_global_state
    ):
        """Test card hover handling with elevation changes.

        Validates that card elevation changes correctly based on hover
        state using parametrized testing for different hover conditions.

        Args:
            mock_fontify: Mocked fontify utility.
            hover_data (str): Hover event data to test.
            expected_elevation (int): Expected card elevation.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)
        mock_event = MagicMock()
        mock_event.data = hover_data
        mock_card = MagicMock()

        # Act
        home_view._handle_card_hover(mock_event, mock_card)

        # Assert
        assert mock_card.elevation == expected_elevation
        mock_card.update.assert_called_once()

    @patch("gui.views.home.fontify")
    def test_handle_card_hover_error_resilience(self, mock_fontify, mock_page, reset_global_state):
        """Test card hover handling with error resilience.

        Validates that card hover handling gracefully handles errors
        without propagating exceptions to the UI layer.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)
        mock_event = MagicMock()
        mock_event.data = "true"
        mock_card = MagicMock()
        mock_card.update.side_effect = RuntimeError("Update failed")

        # Act - Should not raise exception
        home_view._handle_card_hover(mock_event, mock_card)

        # Assert - Method completes without exception

    @pytest.mark.parametrize(
        "event,card,scenario",
        [
            (None, MagicMock(), "none_event"),
            (MagicMock(), None, "none_card"),
            (None, None, "both_none"),
        ],
    )
    @patch("gui.views.home.fontify")
    def test_handle_card_hover_null_parameter_handling(
        self, mock_fontify, event, card, scenario, mock_page, reset_global_state
    ):
        """Test card hover handling with null parameters.

        Validates that card hover handling gracefully handles null
        parameters without raising exceptions.

        Args:
            mock_fontify: Mocked fontify utility.
            event: Event object to test (may be None).
            card: Card object to test (may be None).
            scenario (str): Test scenario description.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        # Act - Should not raise exception
        home_view._handle_card_hover(event, card)

        # Assert - Method completes without exception


class TestHomeViewCardCreation:
    """Test HomeView card creation functionality for both available and coming soon tools.

    This class contains tests for individual card creation, styling,
    and error handling during card component initialization for both
    interactive available tool cards and placeholder coming soon cards.
    """

    @pytest.mark.parametrize(
        "tool_name",
        [
            "Feature Zwei",
            "Another Coming Soon Tool",
            "Tool with Spaces",
            "Tool-with-Dashes",
            "Tool_with_Underscores",
            "",
        ],
    )
    @patch("gui.views.home.fontify")
    def test_create_coming_soon_card_various_names(
        self, mock_fontify, mock_flet_dependency, tool_name, mock_page, reset_global_state
    ):
        """Test coming soon card creation with various tool names.

        Validates that card creation handles different tool name formats
        and special characters correctly using parametrized testing.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            tool_name (str): Tool name to test card creation with.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        # Act
        result = home_view._create_coming_soon_card(tool_name)

        # Assert
        assert result is not None
        mock_flet_dependency.Card.assert_called()

    @patch("gui.views.home.fontify")
    def test_create_coming_soon_card_component_error(
        self, mock_fontify, mock_flet_dependency, mock_page, reset_global_state
    ):
        """Test coming soon card creation handles component errors.

        Validates that HomeViewError is properly raised when card
        component creation fails.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when card creation fails.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)
        tool_name = "Test Tool"
        card_error = RuntimeError("Card creation failed")
        mock_flet_dependency.Card.side_effect = card_error

        # Act & Assert
        with pytest.raises(HomeViewError) as exc_info:
            home_view._create_coming_soon_card(tool_name)

        error = exc_info.value
        assert f"Failed to create coming soon card for {tool_name}" in error.message
        assert error.cause == card_error

    @pytest.mark.parametrize(
        "tool_name,description",
        [
            ("Feature Eins", "Test description"),
            ("Password Generator", "Generate secure passwords"),
            ("Network Scanner", "Scan network for devices"),
            ("Tool with Spaces", "Description with spaces"),
        ],
    )
    @patch("gui.views.home.fontify")
    def test_create_tool_card_various_configurations(
        self,
        mock_fontify,
        mock_flet_dependency,
        tool_name,
        description,
        mock_page,
        reset_global_state,
    ):
        """Test available tool card creation with various tool configurations.

        Validates that interactive tool card creation handles different tool
        configurations correctly using parametrized testing.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            tool_name (str): Tool name to test card creation with.
            description (str): Tool description to test.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)

        # Use mock Flet components for icon and color
        mock_icon = mock_flet_dependency.Icons.REFRESH
        mock_color = mock_flet_dependency.Colors.BLUE

        # Act
        result = home_view._create_tool_card(tool_name, description, mock_icon, mock_color)

        # Assert
        assert result is not None
        mock_flet_dependency.Card.assert_called()

    @patch("gui.views.home.fontify")
    def test_create_tool_card_component_error(
        self, mock_fontify, mock_flet_dependency, mock_page, reset_global_state
    ):
        """Test available tool card creation handles component errors.

        Validates that HomeViewError is properly raised when interactive
        tool card component creation fails.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception when tool card creation fails.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        home_view = HomeView(mock_page)
        tool_name = "Test Tool"
        description = "Test description"
        mock_icon = mock_flet_dependency.Icons.REFRESH
        mock_color = mock_flet_dependency.Colors.BLUE

        card_error = RuntimeError("Tool card creation failed")
        mock_flet_dependency.Card.side_effect = card_error

        # Act & Assert
        with pytest.raises(HomeViewError) as exc_info:
            home_view._create_tool_card(tool_name, description, mock_icon, mock_color)

        error = exc_info.value
        assert f"Failed to create coming soon card for {tool_name}" in error.message
        assert error.cause == card_error


class TestHomeViewIntegrationWorkflows:
    """Integration tests for complete HomeView workflows.

    This class contains tests for end-to-end workflows that
    simulate real usage scenarios and validate complete
    component interaction chains.
    """

    @patch("gui.views.home.fontify")
    def test_complete_initialization_to_ui_setup_workflow(
        self, mock_fontify, mock_page, reset_global_state
    ):
        """Test complete initialization to UI setup workflow.

        Validates the entire HomeView workflow from initialization
        through complete UI setup and component integration.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()

        # Act - Complete initialization workflow
        home_view = HomeView(mock_page)

        # Assert - Verify complete setup
        assert home_view.page == mock_page
        assert home_view.route == "/"
        assert home_view.title == "TJD Toolkit - Homepage"
        assert hasattr(home_view, "_loading_text")
        assert hasattr(home_view, "_loading_overlay")
        assert hasattr(home_view, "controls")

    @patch("gui.views.home.fontify")
    def test_error_recovery_workflow_with_partial_failures(
        self, mock_fontify, mock_page, reset_global_state
    ):
        """Test error recovery with partial component failures.

        Validates that HomeView handles partial failures gracefully
        and provides appropriate error information for debugging.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            HomeViewError: Expected exception with proper error context.
        """
        # Arrange - Set up partial failure scenario
        mock_fontify.side_effect = [MagicMock(), RuntimeError("Font loading failed")]

        # Act & Assert - Should raise HomeViewError with proper context
        with pytest.raises(HomeViewError) as exc_info:
            HomeView(mock_page)

        # Verify error recovery information
        error = exc_info.value
        assert "Failed to create header" in error.message
        assert isinstance(error.cause, RuntimeError)

    @patch("gui.views.home.fontify")
    @patch("gui.views.home.logger")
    def test_logging_integration_throughout_workflow(
        self, mock_logger, mock_fontify, mock_page, reset_global_state
    ):
        """Test logging integration throughout HomeView workflow.

        Validates that logging occurs at appropriate points during
        HomeView operations and error conditions.

        Args:
            mock_logger: Mocked logger instance.
            mock_fontify: Mocked fontify utility.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()

        # Act - Initialize and trigger operations that should log
        home_view = HomeView(mock_page)

        # Trigger an error condition for logging
        home_view.update = Mock(side_effect=RuntimeError("Update error"))
        try:
            home_view._show_loading("test")
        except HomeViewError:
            pass

        # Assert - Verify logging occurred
        assert mock_logger.error.called


class TestHomeViewErrorHandlingComprehensive:
    """Comprehensive error handling tests for HomeView.

    This class contains tests for HomeViewError inheritance,
    attribute validation, and error message formatting to ensure
    proper exception behavior throughout the HomeView system.
    """

    def test_home_view_error_inheritance_and_attributes(self):
        """Test HomeViewError inheritance and attribute storage.

        Validates that HomeViewError properly inherits from base
        exception classes and stores required attributes correctly.

        Raises:
            AssertionError: If HomeViewError is not properly structured.
        """
        # Arrange & Act
        error = HomeViewError("Test home view error")

        # Assert inheritance and attributes
        assert isinstance(error, Exception)
        assert error.message == "Test home view error"
        assert hasattr(error, "cause")

    def test_home_view_error_with_cause_chaining(self):
        """Test HomeViewError with exception cause chaining.

        Validates that HomeViewError properly handles exception
        chaining for debugging and error tracking.

        Raises:
            AssertionError: If cause chaining is not properly handled.
        """
        # Arrange
        original_error = ValueError("Original error")

        # Act
        error = HomeViewError("Home view error", cause=original_error)

        # Assert
        assert error.cause == original_error
        assert str(error) == "Home view error"

    @pytest.mark.parametrize(
        "error_message,cause_exception,expected_behavior",
        [
            ("UI component failed", RuntimeError("Runtime error"), "handles_runtime_error"),
            ("Navigation failed", KeyError("Key error"), "handles_key_error"),
            ("Font loading failed", FileNotFoundError("File not found"), "handles_file_error"),
            ("Theme application failed", ValueError("Value error"), "handles_value_error"),
        ],
    )
    def test_home_view_error_various_scenarios(
        self, error_message, cause_exception, expected_behavior
    ):
        """Test HomeViewError with various error scenarios.

        Validates that HomeViewError handles different types of
        underlying exceptions correctly using parametrized testing.

        Args:
            error_message (str): Error message to test.
            cause_exception: Underlying exception to test.
            expected_behavior (str): Expected behavior description.
        """
        # Act
        error = HomeViewError(error_message, cause=cause_exception)

        # Assert
        assert error.message == error_message
        assert error.cause == cause_exception
        assert isinstance(error, Exception)


class TestModuleConstants:
    """Test module-level constants and attributes.

    This class contains tests for module exports, constants,
    and configuration to ensure proper module setup.
    """

    def test_home_view_class_constants(self):
        """Test HomeView class-level constants.

        Validates that both AVAILABLE_TOOLS and COMING_SOON_TOOLS class constants
        are properly defined and have expected values and types.

        Raises:
            AssertionError: If constants are not properly defined.
        """
        # Test AVAILABLE_TOOLS
        assert hasattr(HomeView, "AVAILABLE_TOOLS")
        assert isinstance(HomeView.AVAILABLE_TOOLS, dict)
        assert len(HomeView.AVAILABLE_TOOLS) > 0

        # Verify expected available tools are present
        expected_available_tools = ["Feature Eins"]
        for tool in expected_available_tools:
            assert tool in HomeView.AVAILABLE_TOOLS
            tool_config = HomeView.AVAILABLE_TOOLS[tool]
            assert "description" in tool_config
            assert "icon" in tool_config
            assert "color" in tool_config

        # Test COMING_SOON_TOOLS
        assert hasattr(HomeView, "COMING_SOON_TOOLS")
        assert isinstance(HomeView.COMING_SOON_TOOLS, list)
        assert len(HomeView.COMING_SOON_TOOLS) > 0

        # Verify expected coming soon tools are present
        expected_coming_soon_tools = ["Feature Zwei"]
        for tool in expected_coming_soon_tools:
            assert tool in HomeView.COMING_SOON_TOOLS
