"""Test suite for the main module in the TJD-Toolkit.

This module provides comprehensive test coverage for the TJDToolkitApp class
and main function, including application lifecycle management, theme configuration,
window setup, navigation routing, and error handling across different scenarios.

The test suite covers:
    - TJDToolkitApp initialization and component setup
    - Theme management and configuration persistence
    - Window configuration and event handling
    - Navigation routing and view management
    - Comprehensive error handling and recovery
    - Integration workflows and edge cases

Example:
    Run the test suite with pytest:
        $ pytest test_main.py -v
"""

from unittest.mock import MagicMock, patch

import pytest

import gui.main as main
from gui.main import TJDToolkitApp
from internal.core.exceptions import (
    ConfigurationError,
    ThemeError,
    WindowError,
    ViewError,
    NavigationError,
)


@pytest.fixture(autouse=True)
def mock_flet_dependency():
    """Mock the flet module while keeping internal components real.

    Automatically applied to all tests to ensure flet UI framework
    is properly mocked without affecting internal logic and exception
    handling.

    Yields:
        MagicMock: Mocked flet module with theme modes configured.
    """
    with patch.dict("sys.modules", {"flet": MagicMock()}):
        with patch("gui.main.ft") as mock_ft:
            mock_ft.ThemeMode.LIGHT = "LIGHT"
            mock_ft.ThemeMode.DARK = "DARK"
            mock_ft.ThemeMode.SYSTEM = "SYSTEM"
            yield mock_ft


@pytest.fixture
def mock_page():
    """Create mock Flet page object for testing.

    Provides a standardized mock page object with all necessary
    attributes initialized for consistent testing across the suite.

    Returns:
        MagicMock: Mock page object with required attributes set.
    """
    page = MagicMock()
    page.route = "/"
    mock_views = MagicMock()
    mock_views.clear = MagicMock()
    mock_views.pop = MagicMock()
    mock_views.append = MagicMock()
    mock_views.__len__ = lambda x: 0
    mock_views.__bool__ = lambda x: False
    mock_views.__iter__ = lambda x: iter([])
    page.views = mock_views
    page.window = MagicMock()
    page.window.width = 1186
    page.window.height = 733
    page.theme_mode = None
    page.theme = None
    page.title = None
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
def mock_view_imports():
    """Mock all view imports that aren't/are ready (yet).

    This fixture mocks the HomeView and other view imports to allow
    testing without the actual view files being implemented.

    Yields:
        dict: Dictionary of mocked view classes and instances for test use.
    """
    with (
        patch("gui.main.HomeView") as mock_home_view,
        patch("gui.main.FeatureEinsView") as mock_feature_eins_view,
    ):

        # Setup HomeView mock
        mock_home_view.__name__ = "HomeView"
        mock_home_view_instance = MagicMock()
        mock_home_view_instance.route = "/"
        mock_home_view.return_value = mock_home_view_instance

        # Setup FeatureEinsView mock
        mock_feature_eins_view.__name__ = "FeatureEinsView"
        mock_feature_eins_view_instance = MagicMock()
        mock_feature_eins_view_instance.route = "/featureeins"
        mock_feature_eins_view.return_value = mock_feature_eins_view_instance

        yield {
            "HomeView": mock_home_view,
            "home_view_instance": mock_home_view_instance,
            "FeatureEinsView": mock_feature_eins_view,
            "feature_eins_view_instance": mock_feature_eins_view_instance,
        }


class TestTJDToolkitAppInitialization:
    """Test TJDToolkitApp initialization and core setup functionality.

    This class contains tests for basic TJDToolkitApp operations including
    initialization, component setup, and core property access functionality.
    """

    @patch("gui.main.FontManager")
    @patch("gui.main.config")
    def test_initialization_success_with_real_exceptions(
        self, mock_config, mock_font_manager_class, mock_page, reset_global_state, mock_view_imports
    ):
        """Test successful TJDToolkitApp initialization with real components.

        Validates that TJDToolkitApp initializes correctly with all components
        properly set up and configured using real exception classes.

        Args:
            mock_config: Mocked config module.
            mock_font_manager_class: Mocked FontManager class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
            mock_view_imports: Mocked view imports fixture.
        """
        # Arrange
        mock_font_manager = MagicMock()
        mock_font_manager_class.return_value = mock_font_manager
        mock_config.get.return_value = "system"

        # Act
        app = TJDToolkitApp(mock_page)

        # Assert
        assert app.page == mock_page
        assert app.font_manager == mock_font_manager
        mock_font_manager_class.assert_called_once_with(mock_page)
        mock_font_manager.setup_fonts.assert_called_once()
        mock_font_manager.get_theme.assert_called_once()

    @patch("gui.main.FontManager")
    @patch("gui.main.config")
    def test_initialization_theme_error_handling(
        self, mock_config, mock_font_manager_class, mock_page, reset_global_state, mock_view_imports
    ):
        """Test initialization handles ThemeError appropriately.

        Validates that ThemeError is properly raised and handled when
        theme setup fails during application initialization.

        Args:
            mock_config: Mocked config module.
            mock_font_manager_class: Mocked FontManager class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
            mock_view_imports: Mocked view imports fixture.

        Raises:
            ThemeError: Expected exception when theme setup fails.
        """
        # Arrange
        mock_font_manager = MagicMock()
        mock_font_manager_class.return_value = mock_font_manager
        config_error = ConfigurationError("Theme config failed")
        mock_font_manager.setup_fonts.side_effect = config_error

        # Act & Assert
        with pytest.raises(ThemeError) as exc_info:
            TJDToolkitApp(mock_page)

        # Verify ThemeError attributes
        error = exc_info.value
        assert "Failed to configure theme settings" in error.message
        assert error.cause == config_error
        assert error.component == "theme_setup"

    @patch("gui.main.FontManager")
    @patch("gui.main.config")
    def test_initialization_window_error_handling(
        self, mock_config, mock_font_manager_class, mock_page, reset_global_state, mock_view_imports
    ):
        """Test initialization handles WindowError appropriately.

        Validates that WindowError is properly raised when window
        setup fails during application initialization.

        Args:
            mock_config: Mocked config module.
            mock_font_manager_class: Mocked FontManager class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
            mock_view_imports: Mocked view imports fixture.

        Raises:
            WindowError: Expected exception when window setup fails.
        """
        # Arrange
        mock_font_manager = MagicMock()
        mock_font_manager_class.return_value = mock_font_manager
        mock_config.get.return_value = "system"

        # Simulate window setup failure
        def setup_page_failure(self):
            raise Exception("Page setup failed")

        with patch.object(TJDToolkitApp, "setup_page", setup_page_failure):
            # Act & Assert
            with pytest.raises(WindowError) as exc_info:
                TJDToolkitApp(mock_page)

            error = exc_info.value
            assert "Failed to setup page" in error.message
            assert error.property_name == "page_setup"

    @patch("gui.main.FontManager")
    @patch("gui.main.config")
    def test_initialization_navigation_error_handling(
        self, mock_config, mock_font_manager_class, mock_page, reset_global_state, mock_view_imports
    ):
        """Test initialization handles navigation setup errors appropriately.

        Validates that NavigationError is properly raised when navigation
        setup fails during application initialization.

        Args:
            mock_config: Mocked config module.
            mock_font_manager_class: Mocked FontManager class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
            mock_view_imports: Mocked view imports fixture.

        Raises:
            NavigationError: Expected exception when navigation setup fails.
        """
        # Arrange
        mock_font_manager = MagicMock()
        mock_font_manager_class.return_value = mock_font_manager
        mock_config.get.return_value = "system"

        # Simulate unexpected error in setup_navigation
        def setup_navigation_failure(self):
            raise OSError("Unexpected system error")

        with patch.object(TJDToolkitApp, "setup_navigation", setup_navigation_failure):
            # Act & Assert
            with pytest.raises(NavigationError) as exc_info:
                TJDToolkitApp(mock_page)

            error = exc_info.value
            assert "Failed to setup navigation" in error.message
            assert error.route == "/"
            assert isinstance(error.cause, OSError)

    @patch("gui.main.FontManager")
    @patch("gui.main.config")
    def test_initialization_truly_unexpected_error_handling(
        self, mock_config, mock_font_manager_class, mock_page, reset_global_state, mock_view_imports
    ):
        """Test initialization handles truly unexpected errors appropriately.

        Validates that unexpected exceptions during basic initialization are
        caught and converted to ThemeError with proper attributes.

        Args:
            mock_config: Mocked config module.
            mock_font_manager_class: Mocked FontManager class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
            mock_view_imports: Mocked view imports fixture.

        Raises:
            ThemeError: Expected exception with unexpected error cause.
        """
        # Arrange
        mock_font_manager_class.side_effect = OSError("System resource unavailable")

        # Act & Assert
        with pytest.raises(ThemeError) as exc_info:
            TJDToolkitApp(mock_page)

        error = exc_info.value
        assert "Unexpected error during application initialization" in error.message
        assert error.component == "app_init"
        assert isinstance(error.cause, OSError)


class TestTJDToolkitAppThemeManagement:
    """Test TJDToolkitApp theme management functionality.

    This class contains comprehensive tests for theme setup operations
    including success scenarios, error handling, and configuration persistence.
    """

    @pytest.mark.parametrize(
        "theme_mode_string,expected_enum",
        [
            ("light", "LIGHT"),
            ("dark", "DARK"),
            ("system", "SYSTEM"),
            ("LIGHT", "LIGHT"),  # Test case insensitivity
            ("invalid", "SYSTEM"),  # Test fallback
        ],
    )
    def test_get_theme_mode_conversion_comprehensive(
        self, theme_mode_string, expected_enum, mock_page, reset_global_state
    ):
        """Test _get_theme_mode converts strings to enum values correctly.

        Validates theme mode string conversion handles all valid modes,
        case variations, and provides appropriate fallbacks.

        Args:
            theme_mode_string (str): Input theme mode string.
            expected_enum (str): Expected enum value string.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page

        # Act
        result = app._get_theme_mode(theme_mode_string)

        # Assert
        assert result == expected_enum

    @patch("gui.main.FontManager")
    @patch("gui.main.config")
    def test_setup_theme_success_workflow(
        self, mock_config, mock_font_manager_class, mock_page, reset_global_state
    ):
        """Test successful theme setup workflow with real config.

        Validates complete theme setup process including font setup,
        theme application, and mode configuration.

        Args:
            mock_config: Mocked config module.
            mock_font_manager_class: Mocked FontManager class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_font_manager = MagicMock()
        mock_font_manager_class.return_value = mock_font_manager
        mock_theme = MagicMock()
        mock_font_manager.get_theme.return_value = mock_theme
        mock_config.get.return_value = "dark"

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page
        app.font_manager = mock_font_manager

        # Act
        app.setup_theme()

        # Assert
        mock_font_manager.setup_fonts.assert_called_once()
        mock_font_manager.get_theme.assert_called_once()
        assert mock_page.theme == mock_theme
        assert mock_page.theme_mode == "DARK"
        mock_page.update.assert_called_once()

    @patch("gui.main.FontManager")
    @patch("gui.main.config")
    def test_setup_theme_configuration_error_with_fallback(
        self, mock_config, mock_font_manager_class, mock_page, reset_global_state
    ):
        """Test theme setup handles ConfigurationError with proper fallback.

        Validates that ConfigurationError during theme setup results in
        appropriate fallback behavior and ThemeError raising.

        Args:
            mock_config: Mocked config module.
            mock_font_manager_class: Mocked FontManager class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            ThemeError: Expected exception with proper cause chain.
        """
        # Arrange
        mock_font_manager = MagicMock()
        mock_font_manager_class.return_value = mock_font_manager
        config_error = ConfigurationError("Config load failed")
        mock_font_manager.setup_fonts.side_effect = config_error

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page
        app.font_manager = mock_font_manager

        # Act & Assert
        with pytest.raises(ThemeError) as exc_info:
            app.setup_theme()

        # Verify fallback and error details
        assert mock_page.theme_mode == "SYSTEM"  # Fallback applied
        error = exc_info.value
        assert "Failed to configure theme settings" in error.message
        assert error.cause == config_error
        assert error.component == "theme_setup"

    @patch("gui.main.FontManager")
    def test_setup_theme_unexpected_error_handling(
        self, mock_font_manager_class, mock_page, reset_global_state
    ):
        """Test theme setup handles unexpected errors properly.

        Validates that unexpected exceptions during theme setup are
        caught and converted to ThemeError with proper cause chain.

        Args:
            mock_font_manager_class: Mocked FontManager class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            ThemeError: Expected exception with unexpected error cause.
        """
        # Arrange
        mock_font_manager = MagicMock()
        mock_font_manager_class.return_value = mock_font_manager
        unexpected_error = RuntimeError("Unexpected system error")
        mock_font_manager.setup_fonts.side_effect = unexpected_error

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page
        app.font_manager = mock_font_manager

        # Act & Assert
        with pytest.raises(ThemeError) as exc_info:
            app.setup_theme()

        # Verify error handling
        assert mock_page.theme_mode == "SYSTEM"  # Fallback applied
        error = exc_info.value
        assert "Unexpected error during theme setup" in error.message
        assert error.cause == unexpected_error
        assert error.component == "theme_setup"


class TestTJDToolkitAppWindowManagement:
    """Test TJDToolkitApp window configuration functionality.

    This class contains tests for window setup operations including
    dimension configuration, error handling, and configuration persistence.
    """

    @patch("gui.main.config")
    def test_setup_page_success_with_config_values(
        self, mock_config, mock_page, reset_global_state
    ):
        """Test successful page setup with configuration values.

        Validates that page setup correctly applies configuration
        values for window dimensions and properties.

        Args:
            mock_config: Mocked config module.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_config.get.side_effect = lambda key, default: {
            "window.width": 1200,
            "window.height": 800,
        }.get(key, default)

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page
        app.DEFAULT_WIDTH = 1186
        app.DEFAULT_HEIGHT = 733

        # Act
        app.setup_page()

        # Assert
        assert mock_page.title == "TJD Toolkit"
        assert mock_page.window.width == 1200
        assert mock_page.window.height == 800

    @patch("gui.main.config")
    def test_setup_page_configuration_error_fallback(
        self, mock_config, mock_page, reset_global_state
    ):
        """Test page setup handles ConfigurationError with defaults.

        Validates that ConfigurationError during page setup results
        in graceful fallback to default values.

        Args:
            mock_config: Mocked config module.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        config_error = ConfigurationError("Window config failed")
        mock_config.get.side_effect = config_error

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page
        app.DEFAULT_WIDTH = 1186
        app.DEFAULT_HEIGHT = 733

        # Act
        app.setup_page()

        # Assert - Should use defaults
        assert mock_page.title == "TJD Toolkit"
        assert mock_page.window.width == 1186
        assert mock_page.window.height == 733

    @patch("gui.main.config")
    def test_setup_page_unexpected_error_handling(self, mock_config, mock_page, reset_global_state):
        """Test page setup handles unexpected errors appropriately.

        Validates that unexpected exceptions during page setup are
        caught and converted to WindowError with proper attributes.

        Args:
            mock_config: Mocked config module.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            WindowError: Expected exception with proper cause.
        """
        # Arrange
        mock_config.get.return_value = 1200
        unexpected_error = RuntimeError("Page title assignment failed")

        def title_setter(self, value):
            raise unexpected_error

        type(mock_page).title = property(fget=lambda x: "", fset=title_setter)

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page

        # Act & Assert
        with pytest.raises(WindowError) as exc_info:
            app.setup_page()

        error = exc_info.value
        assert "Failed to setup page" in error.message
        assert error.property_name == "page_setup"
        assert error.cause == unexpected_error


class TestTJDToolkitAppNavigationManagement:
    """Test TJDToolkitApp navigation and routing functionality.

    This class contains comprehensive tests for navigation setup,
    route handling, view management, error recovery scenarios,
    and mocked view behavior for all implemented + to-be implemented routes.
    """

    def test_setup_navigation_success_workflow(self, mock_page, reset_global_state):
        """Test successful navigation setup workflow.

        Validates that navigation setup correctly configures route handlers
        and initializes navigation to the home route.

        Args:
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page

        # Act
        app.setup_navigation()

        # Assert
        assert mock_page.on_route_change == app._handle_route_change
        assert mock_page.on_view_pop == app._handle_view_pop
        mock_page.go.assert_called_once_with("/")

    def test_setup_navigation_error_handling(self, mock_page, reset_global_state):
        """Test navigation setup handles errors appropriately.

        Validates that exceptions during navigation setup are caught
        and converted to NavigationError with proper attributes.

        Args:
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            NavigationError: Expected exception when navigation setup fails.
        """
        # Arrange
        navigation_error = RuntimeError("Navigation init failed")
        mock_page.go.side_effect = navigation_error

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page

        # Act & Assert
        with pytest.raises(NavigationError) as exc_info:
            app.setup_navigation()

        error = exc_info.value
        assert "Failed to setup navigation" in error.message
        assert error.route == "/"
        assert error.cause == navigation_error

    def test_setup_navigation_unexpected_error_handling(self, mock_page, reset_global_state):
        """Test navigation setup handles unexpected errors appropriately.

        Validates that unexpected exceptions during navigation setup are
        caught and converted to NavigationError with proper attributes.

        Args:
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            NavigationError: Expected exception when navigation setup fails.
        """

        # Arrange
        # Simulate an unexpected error during route handler assignment
        def broken_assignment(self, value):
            raise OSError("System filesystem error")

        type(mock_page).on_route_change = property(fget=lambda x: None, fset=broken_assignment)

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page

        # Act & Assert
        with pytest.raises(NavigationError) as exc_info:
            app.setup_navigation()

        error = exc_info.value
        assert "Failed to setup navigation" in error.message
        assert error.route == "/"
        assert isinstance(error.cause, OSError)

    @pytest.mark.parametrize(
        "route,expected_view_key,expected_instance_key",
        [
            ("/", "HomeView", "home_view_instance"),
            ("/featureeins", "FeatureEinsView", "feature_eins_view_instance"),
        ],
    )
    def test_handle_route_change_success_all_routes(
        self,
        route,
        expected_view_key,
        expected_instance_key,
        mock_page,
        reset_global_state,
        mock_view_imports,
    ):
        """Test route change handling for all implemented routes.

        Validates that all route changes are handled correctly with
        proper view initialization and page updates using mocked views.

        Args:
            route (str): Route path to test.
            expected_view_key (str): Key for expected view class in mock_view_imports.
            expected_instance_key (str): Key for expected view instance in mock_view_imports.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
            mock_view_imports: Mocked view imports fixture.
        """
        # Arrange
        mock_view_class = mock_view_imports[expected_view_key]
        mock_view_instance = mock_view_imports[expected_instance_key]

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page
        mock_page.route = route

        route_event = MagicMock()

        # Act
        app._handle_route_change(route_event)

        # Assert
        mock_page.views.clear.assert_called_once()
        mock_view_class.assert_called_once_with(mock_page)
        mock_page.views.append.assert_called_once_with(mock_view_instance)
        mock_page.update.assert_called_once()

    def test_handle_route_change_unknown_route_error(
        self, mock_page, reset_global_state, mock_view_imports
    ):
        """Test route change handling for unknown routes.

        Validates that unknown routes trigger appropriate error handling
        and redirect to home route.

        Args:
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
            mock_view_imports: Mocked view imports fixture.

        Raises:
            ViewError: Expected exception for unknown routes.
        """
        # Arrange
        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page
        mock_page.route = "/unknown-route"

        route_event = MagicMock()

        # Act & Assert
        with pytest.raises(ViewError) as exc_info:
            app._handle_route_change(route_event)

        # Verify error and redirect
        error = exc_info.value
        assert "Unknown route: /unknown-route" in error.message
        assert error.route == "/unknown-route"
        mock_page.go.assert_called_with("/")  # Redirect to home

    @pytest.mark.parametrize(
        "route,view_class_key,view_name",
        [
            ("/", "HomeView", "HomeView"),
            ("/featureeins", "FeatureEinsView", "FeatureEinsView"),
        ],
    )
    def test_handle_route_change_view_initialization_error_all_routes(
        self, route, view_class_key, view_name, mock_page, reset_global_state, mock_view_imports
    ):
        """Test route change handling with view initialization failure for all routes.

        Validates that view initialization errors are properly handled
        with appropriate error conversion and home redirect for all routes.

        Args:
            route (str): Route path being tested.
            view_class_key (str): Key for view class in mock_view_imports.
            view_name (str): Expected view name in error.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
            mock_view_imports: Mocked view imports fixture.

        Raises:
            ViewError: Expected exception with view initialization failure.
        """
        # Arrange
        view_init_error = RuntimeError("View initialization failed")
        mock_view_class = mock_view_imports[view_class_key]
        mock_view_class.side_effect = view_init_error

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page
        mock_page.route = route

        route_event = MagicMock()

        # Act & Assert
        with pytest.raises(ViewError) as exc_info:
            app._handle_route_change(route_event)

        # Verify error details and redirect
        error = exc_info.value
        assert f"Failed to initialize view for route {route}" in error.message
        assert error.route == route
        assert error.view_name == view_name
        assert error.cause == view_init_error
        mock_page.go.assert_called_with("/")

    def test_handle_route_change_unexpected_error_handling(
        self, mock_page, reset_global_state, mock_view_imports
    ):
        """Test route change handling with unexpected system errors.

        Validates that unexpected exceptions during route handling are
        caught and converted to NavigationError appropriately.

        Args:
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
            mock_view_imports: Mocked view imports fixture.

        Raises:
            NavigationError: Expected exception for unexpected errors.
        """
        # Arrange
        # Simulate an unexpected error during page.views.clear()
        mock_page.views.clear.side_effect = OSError("Disk full error")

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page
        mock_page.route = "/"

        route_event = MagicMock()

        # Act & Assert
        with pytest.raises(NavigationError) as exc_info:
            app._handle_route_change(route_event)

        # Verify error details and redirect
        error = exc_info.value
        assert "Unexpected error handling route /" in error.message
        assert error.route == "/"
        assert isinstance(error.cause, OSError)
        mock_page.go.assert_called_with("/")  # Redirect to home

    def test_handle_view_pop_success_workflow(self, mock_page, reset_global_state):
        """Test successful view pop handling workflow.

        Validates that view pop operations correctly manage the view
        stack and navigate to the appropriate route.

        Args:
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_view1 = MagicMock()
        mock_view1.route = "/view1"
        mock_view2 = MagicMock()
        mock_view2.route = "/view2"

        # Set up the mock views list behavior
        mock_page.views.__bool__ = MagicMock(return_value=True)
        mock_page.views.__len__ = MagicMock(return_value=2)
        mock_page.views.__getitem__ = MagicMock(side_effect=lambda i: [mock_view1, mock_view2][i])

        # Set up pop to modify the mock behavior after being called
        def pop_side_effect():
            # After pop, there should be 1 item left
            mock_page.views.__len__ = MagicMock(return_value=1)
            mock_page.views.__getitem__ = MagicMock(side_effect=lambda i: [mock_view1][i])
            mock_page.views.__bool__ = MagicMock(return_value=True)

        mock_page.views.pop.side_effect = pop_side_effect

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page

        view_to_pop = MagicMock()

        # Act
        app._handle_view_pop(view_to_pop)

        # Assert
        mock_page.views.pop.assert_called_once()
        mock_page.go.assert_called_once_with("/view1")

    def test_handle_view_pop_empty_stack(self, mock_page, reset_global_state):
        """Test view pop handling with empty view stack.

        Validates that view pop operations handle empty view stacks
        gracefully without attempting navigation.

        Args:
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange - keep default behavior (empty list)
        # The fixture already sets __bool__ to False and __len__ to 0

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page

        view_to_pop = MagicMock()

        # Act
        app._handle_view_pop(view_to_pop)

        # Assert
        mock_page.views.pop.assert_not_called()  # Should not attempt to pop
        mock_page.go.assert_not_called()  # No navigation when empty

    def test_handle_view_pop_error_handling(self, mock_page, reset_global_state):
        """Test view pop error handling with NavigationError.

        Validates that exceptions during view pop operations are
        caught and converted to NavigationError appropriately.

        Args:
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            NavigationError: Expected exception when view pop fails.
        """
        # Arrange
        pop_error = RuntimeError("View stack corruption")

        # Override mock to have items so the if condition passes
        mock_page.views.__bool__ = MagicMock(return_value=True)
        mock_page.views.pop.side_effect = pop_error

        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page

        view_to_pop = MagicMock()

        # Act & Assert
        with pytest.raises(NavigationError) as exc_info:
            app._handle_view_pop(view_to_pop)

        error = exc_info.value
        assert "Error handling view pop" in error.message
        assert error.cause == pop_error

    def test_navigation_error_handling_without_real_views(self, mock_page, reset_global_state):
        """Test navigation error handling when no views are available.

        Validates that navigation errors are handled properly
        when views cannot be instantiated.

        Args:
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            ViewError: Expected exception for non-existent routes.
        """
        # Arrange
        app = TJDToolkitApp.__new__(TJDToolkitApp)
        app.page = mock_page
        mock_page.route = "/nonexistent"

        # Act & Assert
        route_event = MagicMock()
        with pytest.raises(ViewError) as exc_info:
            app._handle_route_change(route_event)

        error = exc_info.value
        assert "Unknown route" in error.message
        assert "/nonexistent" in error.message


class TestMainFunctionality:
    """Test the main function and application lifecycle.

    This class contains tests for the main function including
    application initialization, window event handling, and
    error scenarios during startup.
    """

    @patch("gui.main.TJDToolkitApp")
    @patch("gui.main.config")
    def test_main_function_success_workflow(
        self, mock_config, mock_app_class, mock_page, reset_global_state
    ):
        """Test successful main function execution workflow.

        Validates that the main function correctly initializes the
        application and sets up window event handling.

        Args:
            mock_config: Mocked config module.
            mock_app_class: Mocked TJDToolkitApp class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        # Act
        main.main(mock_page)

        # Assert
        mock_app_class.assert_called_once_with(mock_page)
        assert hasattr(mock_page.window, "on_event")
        assert callable(mock_page.window.on_event)

    @patch("gui.main.TJDToolkitApp")
    def test_main_function_app_initialization_error(
        self, mock_app_class, mock_page, reset_global_state
    ):
        """Test main function handles app initialization errors.

        Validates that application initialization errors are
        properly propagated from the main function.

        Args:
            mock_app_class: Mocked TJDToolkitApp class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            ThemeError: Expected exception during app initialization.
        """
        # Arrange
        theme_error = ThemeError("Theme setup failed", component="main")
        mock_app_class.side_effect = theme_error

        # Act & Assert
        with pytest.raises(ThemeError):
            main.main(mock_page)

    @pytest.mark.parametrize(
        "event_type,setup_page_window,expected_config_calls",
        [
            (
                "resize",
                {"window.width": 1200, "window.height": 800},
                [("window.width", 1200), ("window.height", 800)],
            ),
            ("close", {}, []),
        ],
    )
    @patch("gui.main.TJDToolkitApp")
    @patch("gui.main.config")
    def test_window_event_handler_success_scenarios(
        self,
        mock_config,
        mock_app_class,
        event_type,
        setup_page_window,
        expected_config_calls,
        mock_page,
        reset_global_state,
    ):
        """Test window event handler for different event types.

        Validates that window events are properly handled with appropriate
        configuration persistence for resize and close events.

        Args:
            mock_config: Mocked config module.
            mock_app_class: Mocked TJDToolkitApp class.
            event_type (str): Type of window event to test.
            setup_page_window (dict): Window properties to set up.
            expected_config_calls (list): Expected config.set calls.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        # Set up page window properties
        for prop, value in setup_page_window.items():
            setattr(mock_page.window, prop.split(".")[1], value)

        main.main(mock_page)
        event_handler = mock_page.window.on_event

        test_event = MagicMock()
        test_event.type = event_type

        # Act
        event_handler(test_event)

        # Assert
        for call_args in expected_config_calls:
            mock_config.set.assert_any_call(*call_args)
        mock_config.save.assert_called()

    @pytest.mark.parametrize(
        "error_type,expected_message_fragment",
        [
            (ConfigurationError("Save failed"), "Failed to save window settings"),
            (RuntimeError("System failure"), "Unexpected error handling window event"),
        ],
    )
    @patch("gui.main.TJDToolkitApp")
    @patch("gui.main.config")
    def test_window_event_handler_error_scenarios(
        self,
        mock_config,
        mock_app_class,
        error_type,
        expected_message_fragment,
        mock_page,
        reset_global_state,
    ):
        """Test window event handler error handling scenarios.

        Validates that both ConfigurationError and unexpected errors during
        window event handling are caught and converted to WindowError.

        Args:
            mock_config: Mocked config module.
            mock_app_class: Mocked TJDToolkitApp class.
            error_type: Type of error to simulate.
            expected_message_fragment (str): Expected error message fragment.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            WindowError: Expected exception with appropriate cause.
        """
        # Arrange
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_config.set.side_effect = error_type

        main.main(mock_page)
        event_handler = mock_page.window.on_event

        resize_event = MagicMock()
        resize_event.type = "resize"

        # Act & Assert
        with pytest.raises(WindowError) as exc_info:
            event_handler(resize_event)

        error = exc_info.value
        assert expected_message_fragment in error.message
        assert error.property_name == "window_event"
        assert error.cause == error_type


class TestModuleConstants:
    """Test module-level constants and attributes.

    This class contains tests for module exports, constants,
    and configuration to ensure proper module setup.
    """

    def test_module_exports_completeness(self):
        """Test __all__ exports contain expected components.

        Validates that the module exports all required public
        interfaces through the __all__ attribute.

        Raises:
            AssertionError: If expected exports are missing.
        """
        assert hasattr(main, "__all__")
        expected_exports = ["TJDToolkitApp", "main"]

        for export in expected_exports:
            assert export in main.__all__

    def test_default_dimensions_constants(self):
        """Test default window dimension constants.

        Validates that default window dimensions are properly
        defined and have reasonable values.

        Raises:
            AssertionError: If constants are not properly defined.
        """
        assert hasattr(TJDToolkitApp, "DEFAULT_WIDTH")
        assert hasattr(TJDToolkitApp, "DEFAULT_HEIGHT")
        assert TJDToolkitApp.DEFAULT_WIDTH == 1186
        assert TJDToolkitApp.DEFAULT_HEIGHT == 733
        assert isinstance(TJDToolkitApp.DEFAULT_WIDTH, int)
        assert isinstance(TJDToolkitApp.DEFAULT_HEIGHT, int)


class TestErrorHandlingComprehensive:
    """Test comprehensive error scenarios and edge cases.

    This class contains tests for custom exception inheritance
    and attribute validation to ensure proper exception behavior.
    """

    @pytest.mark.parametrize(
        "exception_class,message,kwargs,expected_attrs",
        [
            (
                ThemeError,
                "Test theme error",
                {"theme_name": "test_theme", "component": "test_component"},
                ["theme_name", "component"],
            ),
            (
                WindowError,
                "Test window error",
                {"property_name": "test_property"},
                ["property_name"],
            ),
            (NavigationError, "Test navigation error", {"route": "/test"}, ["route"]),
        ],
    )
    def test_custom_exception_inheritance_and_attributes(
        self, exception_class, message, kwargs, expected_attrs
    ):
        """Test custom exception inheritance and attribute storage.

        Validates that all custom exceptions properly inherit from base
        exception classes and store their specific attributes correctly.

        Args:
            exception_class: Exception class to test.
            message (str): Error message for the exception.
            kwargs (dict): Keyword arguments for exception initialization.
            expected_attrs (list): List of expected attribute names.

        Raises:
            AssertionError: If exception is not properly structured.
        """
        # Arrange & Act
        error = exception_class(message, **kwargs)

        # Assert inheritance and attributes
        assert isinstance(error, Exception)
        assert str(error) == message

        for attr in expected_attrs:
            assert hasattr(error, attr)
            assert getattr(error, attr) == kwargs[attr]

    def test_theme_error_inheritance_and_attributes(self):
        """Test ThemeError inheritance and attribute storage.

        Validates that ThemeError properly inherits from base
        exception classes and stores required attributes.

        Raises:
            AssertionError: If ThemeError is not properly structured.
        """
        # Arrange & Act
        theme_error = ThemeError(
            "Test theme error", theme_name="test_theme", component="test_component"
        )

        # Assert inheritance and attributes
        assert isinstance(theme_error, Exception)
        assert theme_error.message == "Test theme error"
        assert hasattr(theme_error, "theme_name")
        assert hasattr(theme_error, "component")

    def test_window_error_inheritance_and_attributes(self):
        """Test WindowError inheritance and attribute storage.

        Validates that WindowError properly inherits from base
        exception classes and stores required attributes.

        Raises:
            AssertionError: If WindowError is not properly structured.
        """
        # Arrange & Act
        window_error = WindowError("Test window error", property_name="test_property")

        # Assert inheritance and attributes
        assert isinstance(window_error, Exception)
        assert window_error.message == "Test window error"
        assert hasattr(window_error, "property_name")

    def test_navigation_error_inheritance_and_attributes(self):
        """Test NavigationError inheritance and attribute storage.

        Validates that NavigationError properly inherits from base
        exception classes and stores required attributes.

        Raises:
            AssertionError: If NavigationError is not properly structured.
        """
        # Arrange & Act
        nav_error = NavigationError("Test navigation error", route="/test")

        # Assert inheritance and attributes
        assert isinstance(nav_error, Exception)
        assert nav_error.message == "Test navigation error"
        assert hasattr(nav_error, "route")


class TestIntegrationWorkflows:
    """Integration tests for complete application workflows.

    This class contains tests for end-to-end workflows that
    simulate real usage scenarios with mocked view components
    for all routes and features.
    """

    @patch("gui.main.FontManager")
    @patch("gui.main.config")
    @pytest.mark.parametrize(
        "test_route,view_key",
        [
            ("/", "HomeView"),
            ("/featureeins", "FeatureEinsView"),
        ],
    )
    def test_complete_application_lifecycle_all_routes(
        self,
        mock_config,
        mock_font_manager_class,
        test_route,
        view_key,
        mock_page,
        reset_global_state,
        mock_view_imports,
    ):
        """Test complete application lifecycle with all routes and mocked views.

        Validates the entire application workflow from initialization
        through navigation using mocked view components for all implemented routes.

        Args:
            mock_config: Mocked config module.
            mock_font_manager_class: Mocked FontManager class.
            test_route (str): Route to test in the lifecycle.
            view_key (str): Key for view class in mock_view_imports.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
            mock_view_imports: Mocked view imports fixture.
        """
        # Arrange
        mock_font_manager = MagicMock()
        mock_font_manager_class.return_value = mock_font_manager
        mock_config.get.return_value = "system"

        # Act - Initialize application
        app = TJDToolkitApp(mock_page)

        # Simulate route change with mocked view
        mock_page.route = test_route
        route_event = MagicMock()
        app._handle_route_change(route_event)

        # Assert complete workflow
        assert app.page == mock_page
        assert app.font_manager == mock_font_manager
        mock_font_manager.setup_fonts.assert_called_once()
        mock_view_imports[view_key].assert_called_once_with(mock_page)
        mock_page.views.append.assert_called_once()

    @patch("gui.main.FontManager")
    @patch("gui.main.config")
    def test_error_recovery_with_mocked_components(
        self, mock_config, mock_font_manager_class, mock_page, reset_global_state, mock_view_imports
    ):
        """Test error recovery with mocked view components.

        Validates that the application handles error conditions
        gracefully when using mocked view components.

        Args:
            mock_config: Mocked config module.
            mock_font_manager_class: Mocked FontManager class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
            mock_view_imports: Mocked view imports fixture.

        Raises:
            ThemeError: Expected exception with proper fallback behavior.
        """
        # Arrange - Set up partial failure scenario
        mock_font_manager = MagicMock()
        mock_font_manager_class.return_value = mock_font_manager
        mock_config.get.return_value = "dark"
        config_error = ConfigurationError("Theme config error")
        mock_font_manager.setup_fonts.side_effect = config_error

        # Act & Assert - Should raise ThemeError with fallback
        with pytest.raises(ThemeError) as exc_info:
            TJDToolkitApp(mock_page)

        # Verify error handling and fallback
        error = exc_info.value
        assert error.cause == config_error
        assert error.component == "theme_setup"
        assert mock_page.theme_mode == "SYSTEM"  # Fallback applied
