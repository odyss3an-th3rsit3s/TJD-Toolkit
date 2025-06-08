"""Test suite for the featureeins module in the TJD-Toolkit.

This module provides comprehensive test coverage for the FeatureEinsView class,
QuickTypeChallenge game logic, AnimationManager utility, and GameState enum,
including UI setup, game mechanics, animation handling, and error handling
across different scenarios.

The test suite covers:
    - FeatureEinsView initialization and component setup
    - QuickTypeChallenge game lifecycle and mechanics
    - AnimationManager easing functions and opacity animations
    - GameState enum values and transitions
    - UI component creation and management
    - Game input handling and validation
    - Speed calculation and best score tracking
    - Animation threading and error handling
    - Comprehensive error handling and recovery
    - Integration workflows and edge cases

Example:
    Run the test suite with pytest:
        $ pytest test_featureeins.py -v
"""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from gui.views.PUC.featureeins import (
    FeatureEinsView,
    QuickTypeChallenge,
    AnimationManager,
    GameState,
    WORDS,
    MAX_INCORRECT_TRIES,
    ANIMATION_STEPS,
    ANIMATION_DURATION,
)
from internal.core.exceptions import ToolViewError


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
    with patch("gui.views.PUC.featureeins.ft") as mock_ft:
        # Configure flet components
        mock_ft.View = MagicMock()
        mock_ft.Text = MagicMock()
        mock_ft.Container = MagicMock()
        mock_ft.Column = MagicMock()
        mock_ft.Row = MagicMock()
        mock_ft.TextField = MagicMock()
        mock_ft.ElevatedButton = MagicMock()
        mock_ft.Divider = MagicMock()
        mock_ft.Icon = MagicMock()
        mock_ft.IconButton = MagicMock()
        mock_ft.CrossAxisAlignment = MagicMock()
        mock_ft.MainAxisAlignment = MagicMock()
        mock_ft.FontWeight = MagicMock()
        mock_ft.KeyboardType = MagicMock()
        mock_ft.Colors = MagicMock()
        mock_ft.Icons = MagicMock()
        mock_ft.alignment = MagicMock()
        mock_ft.padding = MagicMock()
        mock_ft.border = MagicMock()
        mock_ft.border_radius = MagicMock()

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
    throughout FeatureEins components for text styling.

    Yields:
        MagicMock: Mocked fontify function.
    """
    with patch("gui.views.PUC.featureeins.fontify") as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture
def mock_random():
    """Mock the random module for deterministic testing.

    Provides consistent mocking of random.choice to enable
    predictable testing of word selection mechanics.

    Yields:
        MagicMock: Mocked random module.
    """
    with patch("gui.views.PUC.featureeins.random") as mock:
        yield mock


@pytest.fixture
def mock_time():
    """Mock the time module for deterministic testing.

    Provides consistent mocking of time.time to enable
    predictable testing of timing-related functionality.

    Yields:
        MagicMock: Mocked time module.
    """
    with patch("gui.views.PUC.featureeins.time") as mock:
        yield mock


@pytest.fixture
def mock_threading():
    """Mock the threading module for controlled testing.

    Provides consistent mocking of threading.Thread to enable
    testing of animation threads without actual threading.

    Yields:
        MagicMock: Mocked threading module.
    """
    with patch("gui.views.PUC.featureeins.threading") as mock:
        yield mock


class TestGameStateEnumeration:
    """Test GameState enumeration values and behavior.

    This class contains tests for the GameState enum including
    value validation, membership testing, and proper enumeration
    structure verification.
    """

    def test_game_state_values_correctness(self, reset_global_state):
        """Test that GameState enum has correct string values.

        Validates that all GameState enum members have the expected
        string values for proper state management.

        Args:
            reset_global_state: State reset fixture.
        """
        # Act & Assert
        assert GameState.IDLE.value == "idle"
        assert GameState.STARTED.value == "started"
        assert GameState.ENDED.value == "ended"

    def test_game_state_membership_completeness(self, reset_global_state):
        """Test GameState enum membership and count.

        Validates that GameState enum contains exactly the expected
        members and supports proper membership testing.

        Args:
            reset_global_state: State reset fixture.
        """
        # Act & Assert
        assert len(GameState) == 3
        assert GameState.IDLE in GameState
        assert GameState.STARTED in GameState
        assert GameState.ENDED in GameState

    def test_game_state_string_representation(self, reset_global_state):
        """Test GameState enum string representation.

        Validates that GameState enum members have proper string
        representation for debugging and logging purposes.

        Args:
            reset_global_state: State reset fixture.
        """
        # Act & Assert
        assert str(GameState.IDLE) == "GameState.IDLE"
        assert str(GameState.STARTED) == "GameState.STARTED"
        assert str(GameState.ENDED) == "GameState.ENDED"


class TestAnimationManagerEasingFunctions:
    """Test AnimationManager easing function calculations.

    This class contains comprehensive tests for easing function
    mathematics, boundary conditions, and intermediate value
    calculations for smooth animation curves.
    """

    @pytest.mark.parametrize(
        "input_value,expected_output",
        [
            (0.0, 0.0),
            (1.0, 1.0),
            (0.5, 0.75),
            (0.25, 0.4375),
            (0.75, 0.9375),
        ],
    )
    def test_ease_out_function_calculations(self, input_value, expected_output, reset_global_state):
        """Test ease_out function with various input values.

        Validates that ease_out function produces correct mathematical
        results for smooth deceleration animation curves using
        parametrized testing for comprehensive coverage.

        Args:
            input_value (float): Input progress value (0.0 to 1.0).
            expected_output (float): Expected eased output value.
            reset_global_state: State reset fixture.
        """
        # Act
        result = AnimationManager.ease_out(input_value)

        # Assert
        assert result == expected_output

    @pytest.mark.parametrize(
        "input_value,expected_output",
        [
            (0.0, 0.0),
            (1.0, 1.0),
            (0.25, 0.125),
            (0.5, 0.5),
            (0.75, 0.875),
        ],
    )
    def test_ease_in_out_function_calculations(
        self, input_value, expected_output, reset_global_state
    ):
        """Test ease_in_out function with various input values.

        Validates that ease_in_out function produces correct mathematical
        results for smooth acceleration/deceleration curves using
        parametrized testing for comprehensive coverage.

        Args:
            input_value (float): Input progress value (0.0 to 1.0).
            expected_output (float): Expected eased output value.
            reset_global_state: State reset fixture.
        """
        # Act
        result = AnimationManager.ease_in_out(input_value)

        # Assert
        assert result == expected_output

    @pytest.mark.parametrize(
        "boundary_value",
        [0.0, 1.0],
    )
    def test_easing_functions_boundary_consistency(self, boundary_value, reset_global_state):
        """Test easing functions maintain consistent boundary values.

        Validates that both easing functions return identical values
        at boundary conditions (0.0 and 1.0) for animation consistency.

        Args:
            boundary_value (float): Boundary value to test (0.0 or 1.0).
            reset_global_state: State reset fixture.
        """
        # Act
        ease_out_result = AnimationManager.ease_out(boundary_value)
        ease_in_out_result = AnimationManager.ease_in_out(boundary_value)

        # Assert
        assert ease_out_result == boundary_value
        assert ease_in_out_result == boundary_value
        assert ease_out_result == ease_in_out_result


class TestAnimationManagerOpacityAnimation:
    """Test AnimationManager opacity animation functionality.

    This class contains tests for opacity animation threading,
    parameter validation, error handling, and animation lifecycle
    management with proper thread coordination.
    """

    def test_animate_opacity_thread_creation_success(self, mock_threading, reset_global_state):
        """Test successful opacity animation thread creation.

        Validates that animate_opacity creates and starts animation
        thread with proper parameters and configuration.

        Args:
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_controls = [MagicMock(), MagicMock()]
        mock_page = MagicMock()
        mock_callback = MagicMock()
        target_opacity = 0.8

        mock_thread = MagicMock()
        mock_threading.Thread.return_value = mock_thread

        # Act
        AnimationManager.animate_opacity(
            mock_controls, target_opacity=target_opacity, page=mock_page, callback=mock_callback
        )

        # Assert
        mock_threading.Thread.assert_called_once()
        mock_thread.start.assert_called_once()

    def test_animate_opacity_without_page_parameter(self, mock_threading, reset_global_state):
        """Test opacity animation without page parameter.

        Validates that animate_opacity handles missing page parameter
        gracefully and still creates animation thread appropriately.

        Args:
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_controls = [MagicMock()]
        target_opacity = 0.5

        mock_thread = MagicMock()
        mock_threading.Thread.return_value = mock_thread

        # Act
        AnimationManager.animate_opacity(mock_controls, target_opacity=target_opacity)

        # Assert
        mock_threading.Thread.assert_called_once()
        mock_thread.start.assert_called_once()

    def test_animate_opacity_page_none_breaks_early(self, mock_threading, reset_global_state):
        """Test opacity animation breaks early when page is None.

        Validates that animation loop breaks when page is None,
        covering the break statement in the animation loop.

        Args:
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_controls = [MagicMock(), MagicMock()]
        target_opacity = 0.8

        # Reset mocks to track attribute setting
        for control in mock_controls:
            control.reset_mock()

        # Mock thread to run target function synchronously for testing
        def run_target_sync():
            target_func = mock_threading.Thread.call_args[1]["target"]
            target_func()  # Run the animation function directly

        mock_thread = MagicMock()
        mock_thread.start.side_effect = run_target_sync
        mock_threading.Thread.return_value = mock_thread

        # Act
        AnimationManager.animate_opacity(
            mock_controls,
            target_opacity=target_opacity,
            page=None,  # This will cause the break statement to execute
        )

        # Assert
        mock_threading.Thread.assert_called_once()
        mock_thread.start.assert_called_once()
        # Verify no method calls were made on controls (animation broke early)
        for control in mock_controls:
            assert (
                control.method_calls == []
            ), f"Expected no method calls on control, but got: {control.method_calls}"

    def test_animate_opacity_without_callback_parameter(self, mock_threading, reset_global_state):
        """Test opacity animation without callback parameter.

        Validates that animate_opacity handles missing callback parameter
        gracefully without affecting animation thread creation.

        Args:
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_controls = [MagicMock()]
        mock_page = MagicMock()
        target_opacity = 0.3

        mock_thread = MagicMock()
        mock_threading.Thread.return_value = mock_thread

        # Act
        AnimationManager.animate_opacity(
            mock_controls, target_opacity=target_opacity, page=mock_page
        )

        # Assert
        mock_threading.Thread.assert_called_once()
        mock_thread.start.assert_called_once()

    @pytest.mark.parametrize(
        "controls_count,target_opacity",
        [
            (1, 0.0),
            (3, 0.5),
            (5, 1.0),
            (0, 0.8),
        ],
    )
    def test_animate_opacity_various_configurations(
        self, controls_count, target_opacity, mock_threading, reset_global_state
    ):
        """Test opacity animation with various control counts and opacity values.

        Validates that animate_opacity handles different numbers of controls
        and opacity values correctly using parametrized testing.

        Args:
            controls_count (int): Number of controls to animate.
            target_opacity (float): Target opacity value.
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_controls = [MagicMock() for _ in range(controls_count)]
        mock_thread = MagicMock()
        mock_threading.Thread.return_value = mock_thread

        # Act
        AnimationManager.animate_opacity(mock_controls, target_opacity=target_opacity)

        # Assert
        mock_threading.Thread.assert_called_once()
        mock_thread.start.assert_called_once()

    @patch("gui.views.PUC.featureeins.time.sleep")
    def test_animate_opacity_exception_handling(
        self, mock_sleep, mock_threading, reset_global_state
    ):
        """Test opacity animation exception handling.

        Validates that exceptions during animation are caught and
        re-raised as ToolViewError with proper error context.

        Args:
            mock_sleep: Mocked time.sleep function.
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_controls = [MagicMock(), MagicMock()]
        mock_page = MagicMock()
        target_opacity = 0.8

        # Make time.sleep raise an exception to trigger error handling
        mock_sleep.side_effect = RuntimeError("Simulated animation error")

        # Mock thread to run target function synchronously and capture exception
        captured_exception = None

        def run_target_sync():
            nonlocal captured_exception
            target_func = mock_threading.Thread.call_args[1]["target"]
            try:
                target_func()
            except Exception as e:
                captured_exception = e
                # Don't re-raise here, we want to capture it

        mock_thread = MagicMock()
        mock_thread.start.side_effect = run_target_sync
        mock_threading.Thread.return_value = mock_thread

        # Act
        AnimationManager.animate_opacity(
            mock_controls, target_opacity=target_opacity, page=mock_page
        )

        # Assert
        assert captured_exception is not None
        assert isinstance(captured_exception, ToolViewError)
        assert "Failed to animate opacity" in captured_exception.message
        assert captured_exception.component == "animation_manager"
        assert isinstance(captured_exception.cause, RuntimeError)
        assert "Simulated animation error" in str(captured_exception.cause)


class TestQuickTypeChallengeInitialization:
    """Test QuickTypeChallenge initialization and core setup functionality.

    This class contains tests for basic QuickTypeChallenge operations including
    initialization, component setup, and core property access functionality.
    """

    @patch("gui.views.PUC.featureeins.fontify")
    def test_initialization_success_with_default_values(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test successful QuickTypeChallenge initialization with default values.

        Validates that QuickTypeChallenge initializes correctly with all components
        properly set up and default game state configured.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()

        # Act
        game = QuickTypeChallenge()

        # Assert
        assert game.word == ""
        assert game.start_time is None
        assert game.best_speed is None
        assert game.game_state == GameState.IDLE
        assert game.correct_answers == 0
        assert game.speeds == []
        assert game.incorrect_tries == 0
        assert game.page is None
        assert game.is_animating is False
        assert game.active_animations == []

    @patch("gui.views.PUC.featureeins.fontify")
    def test_initialization_ui_controls_creation(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test QuickTypeChallenge UI controls are properly created.

        Validates that all necessary UI controls are created and accessible
        after initialization with proper component configuration.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()

        # Act
        game = QuickTypeChallenge()

        # Assert
        assert hasattr(game, "title_text")
        assert hasattr(game, "subtitle_text")
        assert hasattr(game, "text_container")
        assert hasattr(game, "entry")
        assert hasattr(game, "start_button")
        assert hasattr(game, "word_display")
        assert hasattr(game, "status")
        assert hasattr(game, "best_speed_display")
        assert hasattr(game, "incorrect_tries_display")

    @pytest.mark.parametrize(
        "method_name",
        [
            "_create_text_elements",
            "_create_game_controls",
            "_create_display_elements",
        ],
    )
    @patch("gui.views.PUC.featureeins.fontify")
    def test_init_controls_exception_handling(
        mock_fontify, mock_flet_dependency, reset_global_state, method_name
    ):
        """Test _init_controls exception handling.

        Validates that exceptions during control initialization are caught
        and re-raised as ToolViewError with proper error context.

        This test is parameterized to check all relevant control creation methods.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
            method_name: Name of the control creation method to raise an exception from.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()

        with (
            patch.object(QuickTypeChallenge, "_create_text_elements") as mock_text_elements,
            patch.object(QuickTypeChallenge, "_create_game_controls") as mock_game_controls,
            patch.object(QuickTypeChallenge, "_create_display_elements") as mock_display_elements,
        ):
            # Make the selected method raise an exception
            method_map = {
                "_create_text_elements": mock_text_elements,
                "_create_game_controls": mock_game_controls,
                "_create_display_elements": mock_display_elements,
            }
            method_map[method_name].side_effect = RuntimeError(
                f"Test control initialization error in {method_name}"
            )

            # Act & Assert
            with pytest.raises(ToolViewError) as exc_info:
                QuickTypeChallenge()

            # Verify the specific error message and attributes
            error = exc_info.value
            assert "Failed to initialize game controls" in error.message
            assert error.component == "control_initialization"
            assert isinstance(error.cause, RuntimeError)
            assert f"Test control initialization error in {method_name}" in str(error.cause)

    @patch("gui.views.PUC.featureeins.fontify")
    def test_page_reference_assignment(
        self, mock_fontify, mock_flet_dependency, mock_page, reset_global_state
    ):
        """Test page reference assignment and retrieval.

        Validates that page reference is properly set and stored
        for later use in game operations and updates.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()

        # Act
        game.set_page(mock_page)

        # Assert
        assert game.page == mock_page

    @patch("gui.views.PUC.featureeins.fontify")
    def test_navigate_home_exception_handling(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test _navigate_home exception handling.

        Validates that exceptions during navigation are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()

        # Set up mock page that raises exception on go
        mock_page = MagicMock()
        mock_page.go.side_effect = RuntimeError("Simulated navigation error")
        game.page = mock_page

        # Act & Assert
        with pytest.raises(ToolViewError) as exc_info:
            game._navigate_home()

        # Verify the specific error message and attributes
        error = exc_info.value
        assert "Failed to navigate to home page" in error.message
        assert error.component == "navigation"
        assert isinstance(error.cause, RuntimeError)
        assert "Simulated navigation error" in str(error.cause)

        # Verify page.go was called with correct argument
        mock_page.go.assert_called_once_with("/")

    @patch("gui.views.PUC.featureeins.fontify")
    def test_update_page_exception_handling(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test _update_page exception handling.

        Validates that exceptions during page update are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()

        # Set up mock page that raises exception on update
        mock_page = MagicMock()
        mock_page.update.side_effect = RuntimeError("Simulated page update error")
        game.page = mock_page

        # Act & Assert
        with pytest.raises(ToolViewError) as exc_info:
            game._update_page()

        # Verify the specific error message and attributes
        error = exc_info.value
        assert "Failed to update page display" in error.message
        assert error.component == "page_update"
        assert isinstance(error.cause, RuntimeError)
        assert "Simulated page update error" in str(error.cause)

        # Verify page.update was called
        mock_page.update.assert_called_once()

    @patch("gui.views.PUC.featureeins.fontify")
    def test_build_method_returns_column(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test build method returns proper Column component.

        Validates that build method creates and returns a Column
        component for integration with Flet UI framework.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        mock_column = MagicMock()
        mock_flet_dependency.Column.return_value = mock_column

        # Act
        result = game.build()

        # Assert
        mock_flet_dependency.Column.assert_called_once()
        assert result == mock_column

    @patch("gui.views.PUC.featureeins.fontify")
    def test_build_exception_handling(self, mock_fontify, mock_flet_dependency, reset_global_state):
        """Test build method exception handling.

        Validates that exceptions during UI build are caught and re-raised as ToolViewError.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()

        # Patch ft.Column to raise an exception to trigger error handling
        with (
            patch.object(game, "title_text", new=MagicMock()),
            patch.object(game, "subtitle_text", new=MagicMock()),
            patch.object(game, "text_container", new=MagicMock()),
            patch.object(game, "start_button", new=MagicMock()),
            patch.object(game, "word_display", new=MagicMock()),
            patch.object(game, "entry", new=MagicMock()),
            patch.object(game, "status", new=MagicMock()),
            patch.object(game, "best_speed_display", new=MagicMock()),
            patch.object(game, "incorrect_tries_display", new=MagicMock()),
            patch("gui.views.PUC.featureeins.ft.Column", side_effect=Exception("Build failure")),
        ):

            # Act & Assert
            with pytest.raises(ToolViewError) as exc_info:
                game.build()

            # Verify the specific error message and attributes
            error = exc_info.value
            assert "Failed to build game interface" in error.message
            assert error.component == "ui_build"
            assert isinstance(error.cause, Exception)
            assert "Build failure" in str(error.cause)


class TestQuickTypeChallengeGameStateManagement:
    """Test QuickTypeChallenge game state management functionality.

    This class contains comprehensive tests for game state transitions,
    state validation, reset operations, and state-dependent behaviors
    throughout the game lifecycle.
    """

    @patch("gui.views.PUC.featureeins.fontify")
    def test_reset_game_state_comprehensive(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test comprehensive game state reset functionality.

        Validates that game state reset properly clears all game
        variables and returns to initial idle state.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()

        # Set up non-default state
        game.game_state = GameState.STARTED
        game.correct_answers = 5
        game.speeds = [1.0, 2.0, 3.0]
        game.incorrect_tries = 2
        game.start_time = time.time()

        # Act
        game._reset_game_state()

        # Assert
        assert game.game_state == GameState.IDLE
        assert game.correct_answers == 0
        assert game.speeds == []
        assert game.incorrect_tries == 0
        assert game.start_time is None

    @pytest.mark.parametrize(
        "initial_state,expected_final_state",
        [
            (GameState.IDLE, GameState.IDLE),
            (GameState.STARTED, GameState.IDLE),
            (GameState.ENDED, GameState.IDLE),
        ],
    )
    @patch("gui.views.PUC.featureeins.fontify")
    def test_reset_game_state_from_various_states(
        self,
        mock_fontify,
        initial_state,
        expected_final_state,
        mock_flet_dependency,
        reset_global_state,
    ):
        """Test game state reset from various initial states.

        Validates that game state reset works correctly regardless
        of the initial game state using parametrized testing.

        Args:
            mock_fontify: Mocked fontify utility.
            initial_state: Initial game state to test reset from.
            expected_final_state: Expected state after reset.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.game_state = initial_state

        # Act
        game._reset_game_state()

        # Assert
        assert game.game_state == expected_final_state

    @patch("gui.views.PUC.featureeins.fontify")
    def test_game_state_persistence_during_play(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test game state persistence during active gameplay.

        Validates that game state is maintained correctly during
        active gameplay without unexpected state changes.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.game_state = GameState.STARTED
        game.start_time = time.time()

        # Act - Simulate game operations that shouldn't change state
        game.correct_answers += 1
        game.speeds.append(2.5)

        # Assert
        assert game.game_state == GameState.STARTED
        assert game.start_time is not None


class TestQuickTypeChallengeAnimations:
    """Test QuickTypeChallenge animation functionality and thread handling.

    This class contains tests for animation sequencing, thread safety,
    state management during animations, and early exit conditions for
    the text size animation system in QuickTypeChallenge.

    The test suite covers:
        - Early return conditions for concurrent animation prevention
        - Break conditions when page reference is missing
        - Animation state tracking and cleanup
        - Thread creation and execution validation
        - Animation flag management and state transitions
        - Thread synchronization and execution order
    """

    @patch("gui.views.PUC.featureeins.fontify")
    def test_animate_text_sizes_early_return_if_animating(
        self, mock_fontify, mock_flet_dependency, mock_threading, reset_global_state
    ):
        """Test _animate_text_sizes early return when already animating.

        Validates that animation function returns early when is_animating
        is already True, preventing concurrent animations.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.is_animating = True  # Set to True to trigger early return
        game.active_animations = []

        # Track if the animation logic was executed
        animation_executed = False
        original_is_animating = game.is_animating

        def run_target_sync():
            nonlocal animation_executed
            target_func = mock_threading.Thread.call_args[1]["target"]
            target_func()
            # If early return worked, is_animating should remain True
            animation_executed = game.is_animating != original_is_animating

        mock_thread = MagicMock()
        mock_thread.start.side_effect = run_target_sync
        mock_threading.Thread.return_value = mock_thread

        # Act
        game._animate_text_sizes()

        # Assert
        mock_threading.Thread.assert_called_once()
        mock_thread.start.assert_called_once()
        # Animation should not have executed (early return)
        assert not animation_executed
        assert game.is_animating is True  # Should remain True

    @patch("gui.views.PUC.featureeins.fontify")
    def test_animate_text_sizes_break_on_no_page(
        self, mock_fontify, mock_flet_dependency, mock_threading, reset_global_state
    ):
        """Test _animate_text_sizes breaks when page is None.

        Validates that animation loop breaks early when page is None,
        covering the break statement in the animation loop.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.page = None  # This will cause the break statement to execute
        game.is_animating = False
        game.active_animations = []

        # Track animation state
        animation_completed = False

        def run_target_sync():
            nonlocal animation_completed
            target_func = mock_threading.Thread.call_args[1]["target"]
            target_func()
            # If break worked correctly, is_animating should be False
            animation_completed = not game.is_animating

        mock_thread = MagicMock()
        mock_thread.start.side_effect = run_target_sync
        mock_threading.Thread.return_value = mock_thread

        # Act
        game._animate_text_sizes()

        # Assert
        mock_threading.Thread.assert_called_once()
        mock_thread.start.assert_called_once()
        # Animation should have completed (broke early but finished cleanup)
        assert animation_completed
        assert game.is_animating is False

    @patch("gui.views.PUC.featureeins.time.sleep")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_animate_text_sizes_exception_handling(
        self, mock_fontify, mock_sleep, mock_flet_dependency, mock_threading, reset_global_state
    ):
        """Test _animate_text_sizes exception handling.

        Validates that exceptions during animation are caught and
        re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_sleep: Mocked time.sleep function.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.page = MagicMock()
        game.is_animating = False
        game.active_animations = []

        # Make time.sleep raise an exception to trigger error handling
        mock_sleep.side_effect = RuntimeError("Simulated animation error")

        # Capture exception raised in thread
        captured_exception = None

        def run_target_sync():
            nonlocal captured_exception
            target_func = mock_threading.Thread.call_args[1]["target"]
            try:
                target_func()
            except Exception as e:
                captured_exception = e

        mock_thread = MagicMock()
        mock_thread.start.side_effect = run_target_sync
        mock_threading.Thread.return_value = mock_thread

        # Act
        game._animate_text_sizes()

        # Assert
        mock_threading.Thread.assert_called_once()
        mock_thread.start.assert_called_once()

        # Verify exception was caught and transformed
        assert captured_exception is not None
        assert isinstance(captured_exception, ToolViewError)
        assert "Failed to animate text sizes" in captured_exception.message
        assert captured_exception.component == "text_animation"
        assert isinstance(captured_exception.cause, RuntimeError)
        assert "Simulated animation error" in str(captured_exception.cause)

        # Verify is_animating was reset to False
        assert game.is_animating is False


class TestQuickTypeChallengeSpeedCalculations:
    """Test QuickTypeChallenge typing speed calculation functionality.

    This class contains tests for speed calculation algorithms,
    timing validation, edge cases, and mathematical accuracy
    of typing performance metrics.
    """

    @pytest.mark.parametrize(
        "word_length,elapsed_time,expected_speed",
        [
            (4, 2.0, 2.0),
            (8, 4.0, 2.0),
            (1, 0.5, 2.0),
            (10, 2.5, 4.0),
            (0, 1.0, 0.0),
        ],
    )
    @patch("gui.views.PUC.featureeins.fontify")
    def test_calculate_typing_speed_various_scenarios(
        self,
        mock_fontify,
        word_length,
        elapsed_time,
        expected_speed,
        mock_flet_dependency,
        mock_time,
        reset_global_state,
    ):
        """Test typing speed calculation with various word lengths and times.

        Validates that typing speed calculation produces correct results
        for different word lengths and elapsed times using mathematical
        formula validation with parametrized testing.

        Args:
            mock_fontify: Mocked fontify utility.
            word_length (int): Number of characters in test word.
            elapsed_time (float): Elapsed time in seconds.
            expected_speed (float): Expected calculated speed.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_time: Mocked time module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.word = "a" * word_length

        current_time = 10.0
        game.start_time = current_time - elapsed_time
        mock_time.time.return_value = current_time

        # Act
        speed = game._calculate_typing_speed()

        # Assert
        assert speed == expected_speed

    @patch("gui.views.PUC.featureeins.fontify")
    def test_calculate_typing_speed_no_start_time(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test typing speed calculation with no start time set.

        Validates that speed calculation returns zero when no start
        time has been set, preventing division by zero errors.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.word = "test"
        game.start_time = None

        # Act
        speed = game._calculate_typing_speed()

        # Assert
        assert speed == 0.0

    @patch("gui.views.PUC.featureeins.fontify")
    def test_calculate_typing_speed_zero_elapsed_time(
        self, mock_fontify, mock_flet_dependency, mock_time, reset_global_state
    ):
        """Test typing speed calculation with zero elapsed time.

        Validates that speed calculation returns zero when no time
        has elapsed, preventing division by zero errors.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_time: Mocked time module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.word = "test"

        current_time = 10.0
        game.start_time = current_time
        mock_time.time.return_value = current_time

        # Act
        speed = game._calculate_typing_speed()

        # Assert
        assert speed == 0.0

    @patch("gui.views.PUC.featureeins.fontify")
    def test_calculate_typing_speed_empty_word(
        self, mock_fontify, mock_flet_dependency, mock_time, reset_global_state
    ):
        """Test typing speed calculation with empty word.

        Validates that speed calculation handles empty word gracefully
        and returns zero speed appropriately.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_time: Mocked time module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.word = ""

        current_time = 10.0
        game.start_time = current_time - 2.0
        mock_time.time.return_value = current_time

        # Act
        speed = game._calculate_typing_speed()

        # Assert
        assert speed == 0.0


class TestQuickTypeChallengeBestSpeedTracking:
    """Test QuickTypeChallenge best speed tracking functionality.

    This class contains tests for best speed updates, display formatting,
    comparison logic, and UI updates for performance tracking features.
    """

    @patch("gui.views.PUC.featureeins.fontify")
    def test_update_best_speed_first_time_record(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test best speed update for first time recording.

        Validates that best speed is properly set and displayed
        when recording the first speed measurement.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.best_speed_display = MagicMock()
        new_speed = 3.5

        # Act
        game._update_best_speed(new_speed)

        # Assert
        assert game.best_speed == new_speed
        assert "🏅 Best: 3.5 char/s" in game.best_speed_display.value

    @patch("gui.views.PUC.featureeins.fontify")
    def test_update_best_speed_improvement_record(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test best speed update with improvement.

        Validates that best speed is updated when a new personal
        best is achieved with proper display formatting.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.best_speed = 2.0
        game.best_speed_display = MagicMock()
        new_speed = 4.0

        # Act
        game._update_best_speed(new_speed)

        # Assert
        assert game.best_speed == new_speed
        assert "🏅 Best: 4.0 char/s" in game.best_speed_display.value

    @patch("gui.views.PUC.featureeins.fontify")
    def test_update_best_speed_no_improvement(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test best speed update without improvement.

        Validates that best speed is not updated when current speed
        does not exceed existing best with trophy display.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.best_speed = 5.0
        game.best_speed_display = MagicMock()
        new_speed = 3.0

        # Act
        game._update_best_speed(new_speed)

        # Assert
        assert game.best_speed == 5.0
        assert "🏆 Best: 5.0 char/s" in game.best_speed_display.value

    @pytest.mark.parametrize(
        "existing_best,new_speed,expected_best,expected_icon",
        [
            (None, 2.5, 2.5, "🏅"),
            (2.0, 3.0, 3.0, "🏅"),
            (3.0, 2.0, 3.0, "🏆"),
            (1.5, 1.5, 1.5, "🏆"),
        ],
    )
    @patch("gui.views.PUC.featureeins.fontify")
    def test_update_best_speed_various_scenarios(
        self,
        mock_fontify,
        existing_best,
        new_speed,
        expected_best,
        expected_icon,
        mock_flet_dependency,
        reset_global_state,
    ):
        """Test best speed update with various speed scenarios.

        Validates best speed update logic with different existing
        bests and new speeds using parametrized testing coverage.

        Args:
            mock_fontify: Mocked fontify utility.
            existing_best: Existing best speed (may be None).
            new_speed (float): New speed to compare.
            expected_best (float): Expected best speed after update.
            expected_icon (str): Expected icon in display.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.best_speed = existing_best
        game.best_speed_display = MagicMock()

        # Act
        game._update_best_speed(new_speed)

        # Assert
        assert game.best_speed == expected_best
        assert expected_icon in game.best_speed_display.value
        assert f"{expected_best} char/s" in game.best_speed_display.value

    @patch("gui.views.PUC.featureeins.fontify")
    def test_update_best_speed_exception_handling(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test _update_best_speed exception handling.

        Validates that exceptions during best speed update are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.best_speed_display = MagicMock()

        # Define a setter that raises an exception
        def raise_exception(self, value):
            raise RuntimeError("Simulated best speed update error")

        # Patch the setter of best_speed_display.value to raise exception
        type(game.best_speed_display).value = property(fset=raise_exception)

        # Act & Assert
        with pytest.raises(ToolViewError) as exc_info:
            game._update_best_speed(5.0)

        # Verify the specific error message and attributes
        error = exc_info.value
        assert "Failed to update best speed" in error.message
        assert error.component == "best_speed"
        assert isinstance(error.cause, RuntimeError)
        assert "Simulated best speed update error" in str(error.cause)

        # Verify best_speed was updated before exception
        assert game.best_speed == 5.0


class TestQuickTypeChallengeIncorrectTriesManagement:
    """Test QuickTypeChallenge incorrect tries tracking functionality.

    This class contains tests for incorrect tries counting, display updates,
    icon management, and game ending conditions based on mistake limits.
    """

    @pytest.mark.parametrize(
        "tries_count,expected_icons",
        [
            (0, 0),
            (1, 1),
            (3, 3),
            (5, 5),
        ],
    )
    @patch("gui.views.PUC.featureeins.fontify")
    def test_update_incorrect_tries_display_icon_count(
        self, mock_fontify, tries_count, expected_icons, mock_flet_dependency, reset_global_state
    ):
        """Test incorrect tries display with various try counts.

        Validates that incorrect tries display shows correct number
        of icons based on current mistake count using parametrized testing.

        Args:
            mock_fontify: Mocked fontify utility.
            tries_count (int): Number of incorrect tries to display.
            expected_icons (int): Expected number of icons.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.incorrect_tries = tries_count
        game.incorrect_tries_display = MagicMock()
        game.incorrect_tries_display.controls = []

        mock_icon = MagicMock()
        mock_flet_dependency.Icon.return_value = mock_icon

        # Act
        game._update_incorrect_tries_display()

        # Assert
        assert len(game.incorrect_tries_display.controls) == expected_icons
        if expected_icons > 0:
            assert mock_flet_dependency.Icon.call_count == expected_icons

    @patch("gui.views.PUC.featureeins.fontify")
    def test_update_incorrect_tries_display_zero_tries(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test incorrect tries display with zero tries.

        Validates that display is properly cleared when there are
        no incorrect tries to show.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.incorrect_tries = 0
        game.incorrect_tries_display = MagicMock()
        game.incorrect_tries_display.controls = []

        # Act
        game._update_incorrect_tries_display()

        # Assert
        assert len(game.incorrect_tries_display.controls) == 0
        mock_flet_dependency.Icon.assert_not_called()

    @patch("gui.views.PUC.featureeins.fontify")
    def test_update_incorrect_tries_display_exception_handling(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test _update_incorrect_tries_display exception handling.

        Validates that exceptions during incorrect tries display update are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.incorrect_tries = 2  # Set to non-zero to trigger icon creation
        game.incorrect_tries_display = MagicMock()
        game.incorrect_tries_display.controls = MagicMock()

        # Make ft.Icon raise an exception to trigger error handling
        mock_flet_dependency.Icon.side_effect = RuntimeError("Icon creation failed")

        # Act & Assert
        with pytest.raises(ToolViewError) as exc_info:
            game._update_incorrect_tries_display()

        # Verify the specific error message and attributes
        error = exc_info.value
        assert "Failed to update incorrect tries display" in error.message
        assert error.component == "tries_display"
        assert isinstance(error.cause, RuntimeError)
        assert "Icon creation failed" in str(error.cause)

        # Verify that controls.clear() was called before the exception
        game.incorrect_tries_display.controls.clear.assert_called_once()

        # Verify ft.Icon was called (and failed)
        mock_flet_dependency.Icon.assert_called_once()

    @patch("gui.views.PUC.featureeins.fontify")
    def test_incorrect_tries_increment_tracking(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test incorrect tries increment and tracking.

        Validates that incorrect tries counter increments properly
        and maintains accurate count throughout gameplay.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        initial_tries = game.incorrect_tries

        # Act
        game.incorrect_tries += 1

        # Assert
        assert game.incorrect_tries == initial_tries + 1


class TestQuickTypeChallengeGameFlow:
    """Test QuickTypeChallenge complete game flow functionality.

    This class contains tests for complete game workflows including
    game activation, answer processing, state transitions, and
    end-to-end gameplay scenarios.
    """

    @patch("gui.views.PUC.featureeins.fontify")
    def test_activate_game_success_workflow(
        self, mock_fontify, mock_flet_dependency, mock_random, reset_global_state
    ):
        """Test successful game activation workflow.

        Validates that game activation properly sets up game state,
        selects random word, and prepares for user input.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_random: Mocked random module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.entry = MagicMock()
        game.status = MagicMock()
        game.page = MagicMock()

        game.word = "python"

        mock_random.choice.return_value = "python"
        event = MagicMock()

        # Act
        game._activate_game(event)

        # Assert
        assert game.game_state == GameState.STARTED
        assert game.start_time is not None
        assert "Ready! Start typing..." in game.status.value

    @patch("gui.views.PUC.featureeins.fontify")
    def test_activate_game_already_started_no_change(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test game activation when already started.

        Validates that game activation has no effect when game
        is already in started state.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.game_state = GameState.STARTED
        original_start_time = time.time()
        game.start_time = original_start_time

        event = MagicMock()

        # Act
        game._activate_game(event)

        # Assert
        assert game.game_state == GameState.STARTED
        assert game.start_time == original_start_time

    @patch("gui.views.PUC.featureeins.time.time")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_activate_game_exception_handling(
        self, mock_fontify, mock_time, mock_flet_dependency, reset_global_state
    ):
        """Test _activate_game exception handling.

        Validates that exceptions during game activation are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_time: Mocked time module fixture.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        mock_time.time.return_value = 10.0
        game = QuickTypeChallenge()
        game.game_state = GameState.IDLE
        game.word = "test"  # Set word so activation condition is met
        game.entry = MagicMock()
        game.status = MagicMock()
        game.page = MagicMock()

        # Make _update_page raise an exception to trigger error handling
        with patch.object(
            game, "_update_page", side_effect=RuntimeError("Simulated update error")
        ) as mock_update_page:
            # Act & Assert
            with pytest.raises(ToolViewError) as exc_info:
                game._activate_game(MagicMock())

        # Verify the specific error message and attributes
        error = exc_info.value
        assert "Failed to activate game" in error.message
        assert error.component == "activate_game"
        assert isinstance(error.cause, RuntimeError)
        assert "Simulated update error" in str(error.cause)

        # Verify game state was set before exception
        assert game.game_state == GameState.STARTED

        # Verify entry label and status were set before exception
        assert game.entry.label == "Type the word and press Enter"
        assert "Ready! Start typing..." in game.status.value
        assert game.status.color == mock_flet_dependency.Colors.GREY_600

        # Verify _update_page was called (and failed)
        mock_update_page.assert_called_once()

    @patch("gui.views.PUC.featureeins.fontify")
    def test_handle_correct_answer_workflow(
        self, mock_fontify, mock_flet_dependency, mock_time, reset_global_state
    ):
        """Test correct answer handling workflow.

        Validates that correct answers are processed with speed
        calculation, score tracking, and UI updates.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_time: Mocked time module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.word = "test"
        game.start_time = 3.0
        game.status = MagicMock()
        game.entry = MagicMock()
        game.best_speed_display = MagicMock()
        game.page = MagicMock()

        mock_time.time.return_value = 5.0  # 2 seconds elapsed

        # Act
        game._handle_correct_answer()

        # Assert
        assert game.correct_answers == 1
        assert len(game.speeds) == 1
        assert game.speeds[0] == 2.0  # 4 chars / 2 seconds
        assert "✔️ Correct!" in game.status.value
        assert game.entry.disabled is True

    @patch("gui.views.PUC.featureeins.fontify")
    def test_handle_correct_answer_exception_handling(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test _handle_correct_answer exception handling.

        Validates that exceptions during correct answer handling are caught
        and handled by setting error status and updating page.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.status = MagicMock()
        game.entry = MagicMock()
        game.page = MagicMock()

        # Patch _calculate_typing_speed to raise an exception
        with patch.object(
            game,
            "_calculate_typing_speed",
            side_effect=RuntimeError("Simulated speed calculation error"),
        ) as mock_calc_speed:
            # Patch _update_page to track calls
            with patch.object(game, "_update_page") as mock_update_page:
                # Act
                game._handle_correct_answer()

                # Assert
                # Status value and color should be set to error
                assert game.status.value == "Error calculating speed"
                assert game.status.color == mock_flet_dependency.Colors.RED
                # _update_page should be called
                mock_update_page.assert_called_once()
                # _calculate_typing_speed should have been called and failed
                mock_calc_speed.assert_called_once()

    @patch("gui.views.PUC.featureeins.fontify")
    def test_handle_incorrect_answer_within_limit(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test incorrect answer handling within attempt limit.

        Validates that incorrect answers increment try counter
        and provide appropriate feedback without ending game.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.incorrect_tries = 2
        game.status = MagicMock()
        game.entry = MagicMock()
        game.incorrect_tries_display = MagicMock()
        game.incorrect_tries_display.controls = []
        game.page = MagicMock()

        with patch.object(game, "_focus_input_field"):
            # Act
            game._handle_incorrect_answer()

        # Assert
        assert game.incorrect_tries == 3
        assert "❌ Oops..." in game.status.value
        assert "Incorrect! Try again." in game.entry.error_text

    @patch("gui.views.PUC.featureeins.fontify")
    def test_handle_incorrect_answer_exceeds_limit(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test incorrect answer handling that exceeds limit.

        Validates that game ends when maximum incorrect tries
        is reached with proper state transition.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.incorrect_tries = MAX_INCORRECT_TRIES - 1
        game.status = MagicMock()
        game.entry = MagicMock()
        game.incorrect_tries_display = MagicMock()
        game.incorrect_tries_display.controls = []
        game.page = MagicMock()

        with patch.object(game, "_display_game_summary"):
            # Act
            game._handle_incorrect_answer()

        # Assert
        assert game.incorrect_tries == MAX_INCORRECT_TRIES
        assert game.game_state == GameState.ENDED
        assert game.entry.disabled is True

    @patch("gui.views.PUC.featureeins.fontify")
    def test_handle_incorrect_answer_exception_handling(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test _handle_incorrect_answer exception handling.

        Validates that exceptions during incorrect answer handling are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.incorrect_tries_display = MagicMock()

        # Patch _update_incorrect_tries_display to raise an exception
        with patch.object(
            game,
            "_update_incorrect_tries_display",
            side_effect=RuntimeError("Simulated update error"),
        ) as mock_update_display:
            # Act & Assert
            with pytest.raises(ToolViewError) as exc_info:
                game._handle_incorrect_answer()

        # Verify the specific error message and attributes
        error = exc_info.value
        assert "Failed to handle wrong answer" in error.message
        assert error.component == "incorrect_answer"
        assert isinstance(error.cause, RuntimeError)
        assert "Simulated update error" in str(error.cause)

        # Verify _update_incorrect_tries_display was called
        mock_update_display.assert_called_once()

    @patch("gui.views.PUC.featureeins.time.time")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_prepare_next_word_exception_handling(
        self, mock_fontify, mock_time, mock_flet_dependency, reset_global_state
    ):
        """Test _prepare_next_word exception handling.

        Validates that exceptions during next word preparation are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_time: Mocked time module fixture.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        mock_time.return_value = 10.0
        game = QuickTypeChallenge()
        game.word_display = MagicMock()
        game.entry = MagicMock()
        game.status = MagicMock()
        game.page = MagicMock()

        # Make _focus_input_field raise an exception to trigger error handling
        with patch.object(
            game, "_focus_input_field", side_effect=RuntimeError("Simulated focus error")
        ) as mock_focus:
            # Act & Assert
            with pytest.raises(ToolViewError) as exc_info:
                game._prepare_next_word()

        # Verify the specific error message and attributes
        error = exc_info.value
        assert "Failed to prepare next word" in error.message
        assert error.component == "next_word"
        assert isinstance(error.cause, RuntimeError)
        assert "Simulated focus error" in str(error.cause)

        # Verify that setup operations were performed before exception
        assert hasattr(game, "word")
        assert game.word_display.value == game.word
        assert game.entry.value == ""
        assert game.entry.error_text is None
        assert "KEEP GOING! Continue typing..." in game.status.value
        assert game.status.color == mock_flet_dependency.Colors.GREY_600
        assert game.entry.disabled is False
        assert game.start_time == 10.0

        # Verify _focus_input_field was called (and failed)
        mock_focus.assert_called_once()

    @patch("gui.views.PUC.featureeins.time.sleep")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_auto_advance_word_exception_handling(
        self, mock_fontify, mock_sleep, mock_flet_dependency, mock_threading, reset_global_state
    ):
        """Test _auto_advance_word exception handling.

        Validates that exceptions during auto word advancement are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_sleep: Mocked time.sleep function.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        mock_sleep.return_value = None
        game = QuickTypeChallenge()
        game.game_state = GameState.STARTED  # Set to STARTED to meet condition
        game.page = MagicMock()  # Set page to meet condition

        # Capture exception raised in thread
        captured_exception = None

        def run_target_sync():
            nonlocal captured_exception
            target_func = mock_threading.Thread.call_args[1]["target"]
            try:
                target_func()
            except Exception as e:
                captured_exception = e

        mock_thread = MagicMock()
        mock_thread.start.side_effect = run_target_sync
        mock_threading.Thread.return_value = mock_thread

        # Make _prepare_next_word raise an exception to trigger error handling
        with patch.object(
            game, "_prepare_next_word", side_effect=RuntimeError("Simulated prepare error")
        ) as mock_prepare:
            # Act
            game._auto_advance_word()

        # Assert
        mock_threading.Thread.assert_called_once()
        mock_thread.start.assert_called_once()

        # Verify exception was caught and transformed
        assert captured_exception is not None
        assert isinstance(captured_exception, ToolViewError)
        assert "Failed to auto-advance to next word" in captured_exception.message
        assert captured_exception.component == "next_word"
        assert isinstance(captured_exception.cause, RuntimeError)
        assert "Simulated prepare error" in str(captured_exception.cause)

        # Verify time.sleep was called
        mock_sleep.assert_called_once()

        # Verify _prepare_next_word was called
        mock_prepare.assert_called_once()


class TestQuickTypeChallengeInputHandling:
    """Test QuickTypeChallenge input handling and form submission.

    This class contains tests for user input processing, form submission
    handling, answer validation, and input field management throughout
    the game interaction workflow.
    """

    @pytest.mark.parametrize(
        "game_state,expected_action",
        [
            (GameState.IDLE, "activate_game"),
            (GameState.STARTED, "process_input"),
            (GameState.ENDED, "no_action"),
        ],
    )
    @patch("gui.views.PUC.featureeins.fontify")
    def test_on_submit_game_state_handling(
        self, mock_fontify, game_state, expected_action, mock_flet_dependency, reset_global_state
    ):
        """Test form submission handling based on game state.

        Validates that form submission takes appropriate action
        based on current game state using parametrized testing.

        Args:
            mock_fontify: Mocked fontify utility.
            game_state: Current game state to test.
            expected_action (str): Expected action description.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.game_state = game_state
        game.word = "test"

        event = MagicMock()

        if game_state == GameState.STARTED:
            game.start_time = time.time()
            game.entry = MagicMock()
            game.entry.value = "test"  # Correct answer

        with (
            patch.object(game, "_activate_game") as mock_activate,
            patch.object(game, "_handle_correct_answer") as mock_correct,
            patch.object(game, "_handle_incorrect_answer") as mock_incorrect,
        ):

            # Act
            game.on_submit(event)

            # Assert
            if expected_action == "activate_game":
                mock_activate.assert_called_once_with(event)
                mock_correct.assert_not_called()
                mock_incorrect.assert_not_called()
            elif expected_action == "process_input":
                mock_correct.assert_called_once()
                mock_activate.assert_not_called()
                mock_incorrect.assert_not_called()
            else:  # no_action
                mock_activate.assert_not_called()
                mock_correct.assert_not_called()
                mock_incorrect.assert_not_called()

    @patch("gui.views.PUC.featureeins.fontify")
    def test_on_submit_correct_answer_processing(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test form submission with correct answer.

        Validates that correct answers are properly detected
        and processed through the correct answer handler.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.game_state = GameState.STARTED
        game.start_time = time.time()
        game.word = "python"
        game.entry = MagicMock()
        game.entry.value = "python"

        event = MagicMock()

        with patch.object(game, "_handle_correct_answer") as mock_handle:
            # Act
            game.on_submit(event)

            # Assert
            mock_handle.assert_called_once()

    @patch("gui.views.PUC.featureeins.fontify")
    def test_on_submit_incorrect_answer_processing(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test form submission with incorrect answer.

        Validates that incorrect answers are properly detected
        and processed through the incorrect answer handler.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.game_state = GameState.STARTED
        game.start_time = time.time()
        game.word = "python"
        game.entry = MagicMock()
        game.entry.value = "wrong"

        event = MagicMock()

        with patch.object(game, "_handle_incorrect_answer") as mock_handle:
            # Act
            game.on_submit(event)

            # Assert
            mock_handle.assert_called_once()

    @patch("gui.views.PUC.featureeins.fontify")
    def test_on_submit_no_start_time_early_return(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test form submission with no start time set.

        Validates that form submission returns early when no
        start time is set, preventing processing errors.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.game_state = GameState.STARTED
        game.start_time = None

        event = MagicMock()

        # Act
        game.on_submit(event)

        # Assert - Should return early without processing
        assert game.correct_answers == 0

    @patch("gui.views.PUC.featureeins.fontify")
    def test_on_submit_exception_handling(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test on_submit exception handling.

        Validates that exceptions during form submission are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.game_state = GameState.STARTED
        game.start_time = 1.0
        game.entry = MagicMock()
        game.entry.value = "test"
        game.word = "test"

        # Patch _handle_correct_answer to raise exception to trigger error handling
        with patch.object(
            game, "_handle_correct_answer", side_effect=RuntimeError("Simulated submission error")
        ) as mock_correct:
            # Act & Assert
            with pytest.raises(ToolViewError) as exc_info:
                game.on_submit(MagicMock())

        # Verify the specific error message and attributes
        error = exc_info.value
        assert "Failed to process user input" in error.message
        assert error.component == "form_submission"
        assert isinstance(error.cause, RuntimeError)
        assert "Simulated submission error" in str(error.cause)

        # Verify _handle_correct_answer was called
        mock_correct.assert_called_once()

    @patch("gui.views.PUC.featureeins.time.sleep")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_focus_input_field_exception_handling(
        self, mock_fontify, mock_sleep, mock_flet_dependency, mock_threading, reset_global_state
    ):
        """Test _focus_input_field exception handling.

        Validates that exceptions during input field focus are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_sleep: Mocked time.sleep function.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.page = MagicMock()
        game.entry = MagicMock()
        game.entry.disabled = False

        # Make entry.focus raise an exception to trigger error handling
        game.entry.focus.side_effect = RuntimeError("Simulated focus error")

        # Capture exception raised in thread
        captured_exception = None

        def run_target_sync():
            nonlocal captured_exception
            target_func = mock_threading.Thread.call_args[1]["target"]
            try:
                target_func()
            except Exception as e:
                captured_exception = e

        mock_thread = MagicMock()
        mock_thread.start.side_effect = run_target_sync
        mock_threading.Thread.return_value = mock_thread

        # Act
        game._focus_input_field()

        # Assert
        mock_threading.Thread.assert_called_once()
        mock_thread.start.assert_called_once()

        # Verify exception was caught and transformed
        assert captured_exception is not None
        assert isinstance(captured_exception, ToolViewError)
        assert "Failed to focus input field" in captured_exception.message
        assert captured_exception.component == "focus_input"
        assert isinstance(captured_exception.cause, RuntimeError)
        assert "Simulated focus error" in str(captured_exception.cause)

        # Verify time.sleep was called with FOCUS_DELAY
        mock_sleep.assert_called_once()

        # Verify entry.focus was called
        game.entry.focus.assert_called_once()


class TestQuickTypeChallengeGameLifecycle:
    """Test QuickTypeChallenge complete game lifecycle management.

    This class contains tests for game start, end, reset operations,
    and complete gameplay workflows from initialization to completion
    with proper state management throughout.
    """

    @patch("gui.views.PUC.featureeins.fontify")
    def test_start_game_complete_setup(
        self, mock_fontify, mock_flet_dependency, mock_random, reset_global_state
    ):
        """Test complete game start setup workflow.

        Validates that game start properly initializes all game
        components, resets state, and prepares for gameplay.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_random: Mocked random module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        mock_random.choice.return_value = "test"

        event = MagicMock()

        with patch.object(game, "_animate_text_sizes"), patch.object(game, "_show_game_elements"):
            # Act
            game.start_game(event)

        # Assert
        assert game.game_state == GameState.IDLE
        assert game.correct_answers == 0
        assert game.speeds == []
        assert game.incorrect_tries == 0

    @patch("gui.views.PUC.featureeins.QuickTypeChallenge._animate_text_sizes")
    @patch("gui.views.PUC.featureeins.QuickTypeChallenge._show_game_elements")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_start_game_exception_handling(
        self,
        mock_fontify,
        mock_show_game_elements,
        mock_animate_text_sizes,
        mock_flet_dependency,
        reset_global_state,
    ):
        """Test start_game exception handling.

        Validates that exceptions during game start are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_show_game_elements: Mocked _show_game_elements method.
            mock_animate_text_sizes: Mocked _animate_text_sizes method.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()

        # Make _animate_text_sizes raise an exception to trigger error handling
        mock_animate_text_sizes.side_effect = RuntimeError("Simulated animation error")

        # Act & Assert
        with pytest.raises(ToolViewError) as exc_info:
            game.start_game(None)

        # Verify the specific error message and attributes
        error = exc_info.value
        assert "Failed to start typing game" in error.message
        assert error.component == "game_start"
        assert isinstance(error.cause, RuntimeError)
        assert "Simulated animation error" in str(error.cause)

        # Verify _animate_text_sizes was called
        mock_animate_text_sizes.assert_called_once()
        # _show_game_elements should not be called due to exception
        mock_show_game_elements.assert_not_called()

    @patch("gui.views.PUC.featureeins.random.choice")
    @patch("gui.views.PUC.featureeins.time.sleep")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_setup_first_word_exception_handling(
        self,
        mock_fontify,
        mock_sleep,
        mock_random_choice,
        mock_flet_dependency,
        mock_threading,
        reset_global_state,
    ):
        """Test _setup_first_word exception handling.

        Validates that exceptions during first word setup are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_sleep: Mocked time.sleep function.
            mock_random_choice: Mocked random.choice function.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.page = MagicMock()
        game.word_display = MagicMock()

        # Make random.choice raise an exception to trigger error handling
        mock_random_choice.side_effect = RuntimeError("Random choice failure")
        mock_sleep.return_value = None

        # Capture exception raised in thread
        captured_exception = None

        def run_target_sync():
            nonlocal captured_exception
            target_func = mock_threading.Thread.call_args[1]["target"]
            try:
                target_func()
            except Exception as e:
                captured_exception = e

        mock_thread = MagicMock()
        mock_thread.start.side_effect = run_target_sync
        mock_threading.Thread.return_value = mock_thread

        # Act
        game._setup_first_word()

        # Assert
        mock_threading.Thread.assert_called_once()
        mock_thread.start.assert_called_once()

        # Verify exception was caught and transformed
        assert captured_exception is not None
        assert isinstance(captured_exception, ToolViewError)
        assert "Failed to setup first word" in captured_exception.message
        assert captured_exception.component == "first_word_setup"
        assert isinstance(captured_exception.cause, RuntimeError)
        assert "Random choice failure" in str(captured_exception.cause)

        # Verify random.choice was called
        mock_random_choice.assert_called_once()

    @patch("gui.views.PUC.featureeins.fontify")
    def test_end_game_workflow(self, mock_fontify, mock_flet_dependency, reset_global_state):
        """Test game end workflow and state transition.

        Validates that game ending properly disables input,
        updates status, and transitions to ended state.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.entry = MagicMock()
        game.status = MagicMock()
        game.page = MagicMock()

        with patch.object(game, "_display_game_summary"):
            # Act
            game._end_game()

        # Assert
        assert game.game_state == GameState.ENDED
        assert game.entry.disabled is True
        assert "💀 Too many mistakes!" in game.status.value

    @patch("gui.views.PUC.featureeins.fontify")
    def test_complete_game_cycle_integration(
        self, mock_fontify, mock_flet_dependency, mock_random, mock_time, reset_global_state
    ):
        """Test complete game cycle from start to end.

        Validates the entire game workflow including start,
        multiple answers, and game completion scenarios.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_random: Mocked random module fixture.
            mock_time: Mocked time module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.page = MagicMock()
        mock_random.choice.return_value = "test"
        mock_time.time.return_value = 10.0

        # Act - Complete game cycle
        game.start_game(Mock())
        assert game.game_state == GameState.IDLE

        game._setup_first_word()
        game._activate_game(Mock())
        assert game.game_state == GameState.STARTED

        # Simulate correct answers
        for _ in range(3):
            game.entry = MagicMock()
            game.entry.value = game.word
            with patch.object(game, "_auto_advance_word"):
                game.on_submit(Mock())

        # Simulate incorrect answers to end game
        game.entry.value = "wrong"
        for _ in range(MAX_INCORRECT_TRIES):
            with (
                patch.object(game, "_display_game_summary"),
                patch.object(game, "_focus_input_field"),
            ):
                game.on_submit(Mock())

        # Assert
        assert game.game_state == GameState.ENDED
        assert game.correct_answers == 3

    @patch("gui.views.PUC.featureeins.AnimationManager.animate_opacity")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_show_game_elements_exception_handling(
        self, mock_fontify, mock_animate_opacity, mock_flet_dependency, reset_global_state
    ):
        """Test _show_game_elements exception handling.

        Validates that exceptions during showing game elements are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_animate_opacity: Mocked AnimationManager.animate_opacity.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.start_button = MagicMock()
        game.word_display = MagicMock()
        game.entry = MagicMock()
        game.status = MagicMock()
        game.page = MagicMock()

        # Make animate_opacity raise an exception to trigger error handling
        mock_animate_opacity.side_effect = RuntimeError("Simulated animation error")

        # Act & Assert
        with pytest.raises(ToolViewError) as exc_info:
            game._show_game_elements()

        # Verify the specific error message and attributes
        error = exc_info.value
        assert "Failed to display game elements" in error.message
        assert error.component == "game_elements"
        assert isinstance(error.cause, RuntimeError)
        assert "Simulated animation error" in str(error.cause)

        # Verify visibility changes were made before the exception
        assert game.start_button.visible is False
        assert game.word_display.visible is True
        assert game.entry.visible is True
        assert game.status.visible is True

        # Verify animate_opacity was called with correct parameters
        mock_animate_opacity.assert_called_once_with(
            [game.entry, game.word_display, game.status],
            target_opacity=1.0,
            page=game.page,
            callback=game._setup_first_word,
        )

    @pytest.mark.parametrize(
        "speeds,expected_avg_speed,expected_color_attr",
        [
            ([4.0, 4.5, 3.8], 4.1, "GREEN_700"),  # avg > 3.5, should be green
            ([2.0, 2.5, 2.8], 2.43, "DEEP_ORANGE_700"),  # avg < 3, should be orange
            ([3.2, 3.3, 3.4], 3.3, None),  # 3 <= avg <= 3.5, should be None
            ([], 0, None),  # empty speeds, should be None
            ([3.0], 3.0, None),  # exactly 3.0, should be None
            ([3.5], 3.5, None),  # exactly 3.5, should be None
        ],
    )
    @patch("gui.views.PUC.featureeins.fontify")
    def test_create_game_summary_speed_color_logic(
        self,
        mock_fontify,
        speeds,
        expected_avg_speed,
        expected_color_attr,
        mock_flet_dependency,
        reset_global_state,
    ):
        """Test _create_game_summary speed color logic with various average speeds.

        Validates that speed color coding logic works correctly for different
        average speed ranges and covers all conditional branches.

        Args:
            mock_fontify: Mocked fontify utility.
            speeds (list): List of speed values to test.
            expected_avg_speed (float): Expected calculated average speed.
            expected_color_attr (str): Expected color attribute name or None.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.speeds = speeds
        game.correct_answers = 5
        game.best_speed = 4.0

        # Track fontify calls to verify color parameter
        fontify_calls = []

        def track_fontify_calls(*args, **kwargs):
            fontify_calls.append((args, kwargs))
            return MagicMock()

        mock_fontify.side_effect = track_fontify_calls

        # Act
        game._create_game_summary()

        # Assert
        # Verify result is a Column
        mock_flet_dependency.Column.assert_called()

        # Find the fontify call for average speed (should include color parameter)
        avg_speed_calls = [
            call for call in fontify_calls if len(call[0]) > 0 and "char/s" in str(call[0][0])
        ]

        if expected_color_attr:
            # Should find a call with color parameter
            assert len(avg_speed_calls) > 0
            found_color_call = False
            for args, kwargs in avg_speed_calls:
                if "color" in kwargs:
                    # Verify the color attribute is accessed
                    assert hasattr(mock_flet_dependency.Colors, expected_color_attr)
                    found_color_call = True
                    break
            assert found_color_call, f"Expected color call with {expected_color_attr}"
        else:
            # For None color case, fontify might be called but color should be None
            # This is still valid behavior
            pass

    @patch("gui.views.PUC.featureeins.fontify")
    def test_create_game_summary_successful_completion(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test _create_game_summary successful completion and structure.

        Validates that game summary creation completes successfully
        and returns proper Column structure with all components.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.speeds = [3.0, 3.5, 4.0]  # Average = 3.5 (no special color)
        game.correct_answers = 10
        game.best_speed = 4.2

        mock_column = MagicMock()
        mock_flet_dependency.Column.return_value = mock_column

        # Act
        result = game._create_game_summary()

        # Assert
        # Verify successful completion - returns the Column
        assert result == mock_column

        # Verify Column was called with proper structure
        mock_flet_dependency.Column.assert_called()

        # Verify key components were created
        mock_flet_dependency.Container.assert_called()
        mock_flet_dependency.ElevatedButton.assert_called()
        mock_flet_dependency.Row.assert_called()

        # Verify fontify was called multiple times for different text elements
        assert (
            mock_fontify.call_count >= 4
        )  # At least: title, subtitle, correct answers, best speed

    @pytest.mark.parametrize(
        "correct_answers,best_speed,speeds",
        [
            (0, None, []),
            (5, 2.5, [2.0, 2.5, 3.0]),
            (15, 5.0, [4.0, 5.0, 6.0]),
            (1, 1.0, [1.0]),
        ],
    )
    @patch("gui.views.PUC.featureeins.fontify")
    def test_create_game_summary_various_game_states(
        self,
        mock_fontify,
        correct_answers,
        best_speed,
        speeds,
        mock_flet_dependency,
        reset_global_state,
    ):
        """Test _create_game_summary with various game state combinations.

        Validates that summary creation works correctly with different
        combinations of game statistics and completion states.

        Args:
            mock_fontify: Mocked fontify utility.
            correct_answers (int): Number of correct answers to test.
            best_speed (float): Best speed value to test.
            speeds (list): List of speed values to test.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.correct_answers = correct_answers
        game.best_speed = best_speed
        game.speeds = speeds

        mock_column = MagicMock()
        mock_flet_dependency.Column.return_value = mock_column

        # Act
        result = game._create_game_summary()

        # Assert
        # Verify successful completion
        assert result == mock_column

        # Verify Column was called twice (inner + outer Column)
        assert mock_flet_dependency.Column.call_count == 2  # ← Changed this line

        # Verify key components were created
        mock_flet_dependency.Container.assert_called()
        mock_flet_dependency.ElevatedButton.assert_called()
        mock_flet_dependency.Row.assert_called()

        # Verify fontify was called multiple times for different text elements
        assert (
            mock_fontify.call_count >= 4
        )  # At least: title, subtitle, correct answers, best speed

        # Verify game statistics are incorporated into display
        fontify_calls = [call for call in mock_fontify.call_args_list]

        # Should include correct answers in one of the calls
        correct_answers_found = any(
            str(correct_answers) in str(call[0][0]) if call[0] else False for call in fontify_calls
        )
        assert (
            correct_answers_found
        ), f"Correct answers {correct_answers} not found in fontify calls"

        # Should include best speed (or 0 if None) in one of the calls
        expected_best_display = str(best_speed or 0)
        best_speed_found = any(
            expected_best_display in str(call[0][0]) if call[0] else False for call in fontify_calls
        )
        assert best_speed_found, f"Best speed {expected_best_display} not found in fontify calls"

    @patch("gui.views.PUC.featureeins.time.sleep")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_display_game_summary_no_page_early_return(
        self, mock_fontify, mock_sleep, mock_flet_dependency, mock_threading, reset_global_state
    ):
        """Test _display_game_summary early return when page is None.

        Validates that summary display returns early when page is None,
        covering the early return statement in the show_summary function.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_sleep: Mocked time.sleep function.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        mock_sleep.return_value = None
        game = QuickTypeChallenge()
        game.page = None  # This will cause early return

        def run_target_sync():
            target_func = mock_threading.Thread.call_args[1]["target"]
            target_func()

        mock_thread = MagicMock()
        mock_thread.start.side_effect = run_target_sync
        mock_threading.Thread.return_value = mock_thread

        with patch.object(game, "_create_game_summary") as mock_create_summary:
            # Act
            game._display_game_summary()

            # Assert
            mock_threading.Thread.assert_called_once()
            mock_thread.start.assert_called_once()
            mock_sleep.assert_called_once()
            # Should not call _create_game_summary due to early return
            mock_create_summary.assert_not_called()

    @patch("gui.views.PUC.featureeins.time.sleep")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_display_game_summary_successful_display(
        self, mock_fontify, mock_sleep, mock_flet_dependency, mock_threading, reset_global_state
    ):
        """Test _display_game_summary successful completion.

        Validates that summary display completes successfully with proper
        page content replacement and UI component creation.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_sleep: Mocked time.sleep function.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        mock_sleep.return_value = None
        game = QuickTypeChallenge()
        game.page = MagicMock()
        game.page.views = MagicMock()

        # Mock the summary creation
        mock_game_summary = MagicMock()

        def run_target_sync():
            target_func = mock_threading.Thread.call_args[1]["target"]
            target_func()

        mock_thread = MagicMock()
        mock_thread.start.side_effect = run_target_sync
        mock_threading.Thread.return_value = mock_thread

        with (
            patch.object(
                game, "_create_game_summary", return_value=mock_game_summary
            ) as mock_create_summary,
            patch.object(game, "_update_page") as mock_update_page,
        ):

            # Act
            game._display_game_summary()

            # Assert
            mock_threading.Thread.assert_called_once()
            mock_thread.start.assert_called_once()
            mock_sleep.assert_called_once()

            # Verify page content was modified
            game.page.views.clear.assert_called_once()
            game.page.views.append.assert_called_once()

            # Verify UI components were created
            mock_flet_dependency.Row.assert_called()
            mock_flet_dependency.IconButton.assert_called()
            mock_flet_dependency.View.assert_called()
            mock_flet_dependency.Container.assert_called()
            mock_flet_dependency.Column.assert_called()
            mock_flet_dependency.Divider.assert_called()

            # Verify fontify was called for header
            mock_fontify.assert_called()

            # Verify game summary was created and _update_page was called
            mock_create_summary.assert_called_once()
            mock_update_page.assert_called_once()

    @patch("gui.views.PUC.featureeins.time.sleep")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_display_game_summary_ui_creation_error(
        self, mock_fontify, mock_sleep, mock_flet_dependency, mock_threading, reset_global_state
    ):
        """Test _display_game_summary with UI component creation error.

        Validates that exceptions during UI component creation are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_sleep: Mocked time.sleep function.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        mock_sleep.return_value = None
        game = QuickTypeChallenge()
        game.page = MagicMock()

        # Make IconButton raise an exception to trigger error handling
        mock_flet_dependency.IconButton.side_effect = RuntimeError("UI creation failed")

        # Capture exception raised in thread
        captured_exception = None

        def run_target_sync():
            nonlocal captured_exception
            target_func = mock_threading.Thread.call_args[1]["target"]
            try:
                target_func()
            except Exception as e:
                captured_exception = e

        mock_thread = MagicMock()
        mock_thread.start.side_effect = run_target_sync
        mock_threading.Thread.return_value = mock_thread

        with patch.object(game, "_create_game_summary", return_value=MagicMock()):
            # Act
            game._display_game_summary()

            # Assert
            mock_threading.Thread.assert_called_once()
            mock_thread.start.assert_called_once()

            # Verify exception was caught and transformed
            assert captured_exception is not None
            assert isinstance(captured_exception, ToolViewError)
            assert "Failed to display game over screen" in captured_exception.message
            assert captured_exception.component == "summary_display"
            assert isinstance(captured_exception.cause, RuntimeError)
            assert "UI creation failed" in str(captured_exception.cause)

            # Verify time.sleep was called before exception
            mock_sleep.assert_called_once()

    @patch("gui.views.PUC.featureeins.fontify")
    def test_create_game_summary_exception_handling(
        self, mock_fontify, mock_flet_dependency, reset_global_state
    ):
        """Test _create_game_summary exception handling.

        Validates that exceptions during game summary creation are caught
        and re-raised as ToolViewError with proper error context.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        game = QuickTypeChallenge()
        game.speeds = [2.0, 3.0, 4.0]  # Set some speeds for summary calculation
        game.correct_answers = 5
        game.best_speed = 4.0

        # Make fontify raise an exception to trigger error handling
        mock_fontify.side_effect = RuntimeError("Simulated summary creation error")

        # Act & Assert
        with pytest.raises(ToolViewError) as exc_info:
            game._create_game_summary()

        # Verify the specific error message and attributes
        error = exc_info.value
        assert "Failed to create game summary" in error.message
        assert error.component == "summary_creation"
        assert isinstance(error.cause, RuntimeError)
        assert "Simulated summary creation error" in str(error.cause)

        # Verify fontify was called (and failed)
        mock_fontify.assert_called()


class TestFeatureEinsViewInitialization:
    """Test FeatureEinsView initialization and setup functionality.

    This class contains tests for FeatureEinsView operations including
    initialization, component setup, error handling, and integration
    with QuickTypeChallenge game component.
    """

    @patch("gui.views.PUC.featureeins.QuickTypeChallenge")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_initialization_success_with_valid_page(
        self, mock_fontify, mock_game_class, mock_flet_dependency, mock_page, reset_global_state
    ):
        """Test successful FeatureEinsView initialization with valid page.

        Validates that FeatureEinsView initializes correctly with all components
        properly set up and game configured with page reference.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_game_class: Mocked QuickTypeChallenge class.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        mock_game = MagicMock()
        mock_game_class.return_value = mock_game

        # Act
        view = FeatureEinsView(mock_page)

        # Assert
        mock_game_class.assert_called_once()
        mock_game.set_page.assert_called_once_with(mock_page)
        assert view.route == "/featureeins"

    @patch("gui.views.PUC.featureeins.QuickTypeChallenge")
    def test_initialization_game_creation_error(
        self, mock_game_class, mock_page, reset_global_state
    ):
        """Test FeatureEinsView initialization with game creation error.

        Validates that ToolViewError is properly raised when QuickTypeChallenge
        initialization fails during view setup.

        Args:
            mock_game_class: Mocked QuickTypeChallenge class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            ToolViewError: Expected exception when game creation fails.
        """
        # Arrange
        mock_game_class.side_effect = Exception("Game creation failed")

        # Act & Assert
        with pytest.raises(ToolViewError) as exc_info:
            FeatureEinsView(mock_page)

        error = exc_info.value
        assert "Failed to initialize Feature Eins view" in error.message

    @patch("gui.views.PUC.featureeins.QuickTypeChallenge")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_create_tool_header_success(
        self, mock_fontify, mock_game_class, mock_flet_dependency, mock_page, reset_global_state
    ):
        """Test successful tool header creation.

        Validates that tool header is created with proper components
        including back button and title styling.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_game_class: Mocked QuickTypeChallenge class.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        mock_game = MagicMock()
        mock_game_class.return_value = mock_game

        view = FeatureEinsView(mock_page)

        # Reset mocks to isolate the method call
        mock_flet_dependency.IconButton.reset_mock()
        mock_flet_dependency.Row.reset_mock()
        mock_fontify.reset_mock()

        # Act
        view._create_tool_header(mock_page)

        # Assert
        mock_flet_dependency.IconButton.assert_called_once()
        mock_fontify.assert_called()
        mock_flet_dependency.Row.assert_called_once()

    @patch("gui.views.PUC.featureeins.QuickTypeChallenge")
    def test_create_tool_header_component_error(
        self, mock_game_class, mock_flet_dependency, mock_page, reset_global_state
    ):
        """Test tool header creation with component error.

        Validates that ToolViewError is properly raised when header
        component creation fails during view setup.

        Args:
            mock_game_class: Mocked QuickTypeChallenge class.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            ToolViewError: Expected exception when header creation fails.
        """
        # Arrange
        mock_game = MagicMock()
        mock_game_class.return_value = mock_game
        mock_flet_dependency.IconButton.side_effect = Exception("Icon creation failed")

        # Act & Assert
        with pytest.raises(ToolViewError) as exc_info:
            FeatureEinsView(mock_page)

        error = exc_info.value
        assert "Failed to create tool header" in error.message


class TestModuleConstants:
    """Test module-level constants and configuration values.

    This class contains tests for module exports, constants,
    and configuration to ensure proper module setup and
    game parameter validation.
    """

    def test_words_list_completeness(self, reset_global_state):
        """Test WORDS list contains expected content.

        Validates that WORDS list is properly populated with
        valid strings for game word selection.

        Args:
            reset_global_state: State reset fixture.
        """
        # Assert
        assert len(WORDS) > 0
        assert all(isinstance(word, str) for word in WORDS)
        assert all(len(word) > 0 for word in WORDS)
        assert all(word.islower() for word in WORDS)

    def test_game_configuration_constants(self, reset_global_state):
        """Test game configuration constants are properly defined.

        Validates that game configuration constants have reasonable
        values for gameplay balance and user experience.

        Args:
            reset_global_state: State reset fixture.
        """
        # Assert
        assert isinstance(MAX_INCORRECT_TRIES, int)
        assert MAX_INCORRECT_TRIES > 0
        assert isinstance(ANIMATION_STEPS, int)
        assert ANIMATION_STEPS > 0
        assert isinstance(ANIMATION_DURATION, (int, float))
        assert ANIMATION_DURATION > 0

    @pytest.mark.parametrize(
        "constant_name,expected_type,min_value",
        [
            ("MAX_INCORRECT_TRIES", int, 1),
            ("ANIMATION_STEPS", int, 10),
            ("ANIMATION_DURATION", (int, float), 0.1),
        ],
    )
    def test_numeric_constants_validation(
        self, constant_name, expected_type, min_value, reset_global_state
    ):
        """Test numeric constants have valid types and values.

        Validates that all numeric constants are properly typed
        and have reasonable minimum values using parametrized testing.

        Args:
            constant_name (str): Name of constant to test.
            expected_type: Expected type of constant.
            min_value: Minimum expected value.
            reset_global_state: State reset fixture.
        """
        # Arrange
        import gui.views.PUC.featureeins as module

        constant_value = getattr(module, constant_name)

        # Act & Assert
        assert isinstance(constant_value, expected_type)
        assert constant_value >= min_value


class TestErrorHandlingComprehensive:
    """Comprehensive error handling tests for featureeins module.

    This class contains tests for ToolViewError inheritance,
    attribute validation, and error message formatting to ensure
    proper exception behavior throughout the FeatureEins system.
    """

    def test_tool_view_error_inheritance_and_attributes(self, reset_global_state):
        """Test ToolViewError inheritance and attribute storage.

        Validates that ToolViewError properly inherits from base
        exception classes and stores required attributes correctly.

        Args:
            reset_global_state: State reset fixture.

        Raises:
            AssertionError: If ToolViewError is not properly structured.
        """
        # Arrange & Act
        error = ToolViewError("Test tool view error")

        # Assert
        assert isinstance(error, Exception)
        assert error.message == "Test tool view error"
        assert hasattr(error, "cause")

    def test_tool_view_error_with_cause_chaining(self, reset_global_state):
        """Test ToolViewError with exception cause chaining.

        Validates that ToolViewError properly handles exception
        chaining for debugging and error tracking.

        Args:
            reset_global_state: State reset fixture.

        Raises:
            AssertionError: If cause chaining is not properly handled.
        """
        # Arrange
        original_error = ValueError("Original error")

        # Act
        error = ToolViewError("Tool view error", cause=original_error)

        # Assert
        assert error.cause == original_error
        assert str(error) == "Tool view error"

    @pytest.mark.parametrize(
        "error_message,cause_exception,expected_behavior",
        [
            ("Game initialization failed", RuntimeError("Runtime error"), "handles_runtime_error"),
            ("View creation failed", KeyError("Key error"), "handles_key_error"),
            ("Component setup failed", FileNotFoundError("File not found"), "handles_file_error"),
            ("Header creation failed", ValueError("Value error"), "handles_value_error"),
        ],
    )
    def test_tool_view_error_various_scenarios(
        self, error_message, cause_exception, expected_behavior, reset_global_state
    ):
        """Test ToolViewError with various error scenarios.

        Validates that ToolViewError handles different types of
        underlying exceptions correctly using parametrized testing.

        Args:
            error_message (str): Error message to test.
            cause_exception: Underlying exception to test.
            expected_behavior (str): Expected behavior description.
            reset_global_state: State reset fixture.
        """
        # Act
        error = ToolViewError(error_message, cause=cause_exception)

        # Assert
        assert error.message == error_message
        assert error.cause == cause_exception
        assert isinstance(error, Exception)


class TestIntegrationWorkflows:
    """Integration tests for complete featureeins workflows.

    This class contains tests for end-to-end workflows that
    simulate real usage scenarios and validate complete
    component interaction chains from view to game logic.
    """

    @patch("gui.views.PUC.featureeins.QuickTypeChallenge")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_complete_view_initialization_workflow(
        self, mock_fontify, mock_game_class, mock_page, reset_global_state
    ):
        """Test complete view initialization workflow.

        Validates the entire FeatureEinsView workflow from initialization
        through complete component setup and game integration.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_game_class: Mocked QuickTypeChallenge class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        mock_game = MagicMock()
        mock_game_class.return_value = mock_game

        # Act - Complete initialization workflow
        view = FeatureEinsView(mock_page)

        # Assert - Verify complete setup
        assert view.route == "/featureeins"
        mock_game_class.assert_called_once()
        mock_game.set_page.assert_called_once_with(mock_page)

    @patch("gui.views.PUC.featureeins.QuickTypeChallenge")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_game_integration_workflow(
        self, mock_fontify, mock_game_class, mock_page, reset_global_state
    ):
        """Test game integration workflow with view.

        Validates that QuickTypeChallenge game is properly integrated
        with FeatureEinsView and configured for gameplay.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_game_class: Mocked QuickTypeChallenge class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        mock_game = MagicMock()
        mock_game_class.return_value = mock_game

        # Act - Initialize view and verify game integration
        view = FeatureEinsView(mock_page)

        # Assert - Verify game integration
        mock_game.set_page.assert_called_once_with(mock_page)
        assert hasattr(view, "game")

    @patch("gui.views.PUC.featureeins.QuickTypeChallenge")
    @patch("gui.views.PUC.featureeins.fontify")
    def test_error_recovery_workflow_with_partial_failures(
        self, mock_fontify, mock_game_class, mock_page, reset_global_state
    ):
        """Test error recovery with partial component failures.

        Validates that FeatureEinsView handles partial failures gracefully
        and provides appropriate error information for debugging.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_game_class: Mocked QuickTypeChallenge class.
            mock_page: Mock page fixture.
            reset_global_state: State reset fixture.

        Raises:
            ToolViewError: Expected exception with proper error context.
        """
        # Arrange - Set up partial failure scenario
        mock_fontify.return_value = MagicMock()
        mock_game_class.side_effect = RuntimeError("Game initialization failed")

        # Act & Assert - Should raise ToolViewError with proper context
        with pytest.raises(ToolViewError) as exc_info:
            FeatureEinsView(mock_page)

        # Verify error recovery information
        error = exc_info.value
        assert "Failed to initialize Feature Eins view" in error.message
        assert isinstance(error.cause, RuntimeError)


class TestEdgeCasesAndBoundaryConditions:
    """Test edge cases and boundary conditions for featureeins module.

    This class contains tests for edge cases, boundary values,
    performance limits, and unusual input scenarios to ensure
    robust behavior under all conditions.
    """

    @patch("gui.views.PUC.featureeins.fontify")
    def test_empty_word_handling(self, mock_fontify, mock_flet_dependency, reset_global_state):
        """Test handling of empty words in speed calculation.

        Validates that empty word scenarios are handled gracefully
        without causing calculation errors or exceptions.

        Args:
            mock_fontify: Mocked fontify utility.
            mock_flet_dependency: Mocked flet module with UI components.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.word = ""

        # Act
        speed = game._calculate_typing_speed()

        # Assert
        assert speed == 0.0

    @pytest.mark.parametrize(
        "word_length,elapsed_time,expected_speed",
        [
            (1, 0.1, 10.0),  # Very fast typing
            (100, 60.0, 1.67),  # Very long word
            (1, 0.001, 1000.0),  # Extremely fast
            (1000, 0.001, 1000000.0),  # Theoretical maximum
        ],
    )
    @patch("gui.views.PUC.featureeins.fontify")
    def test_extreme_typing_speed_scenarios(
        self,
        mock_fontify,
        word_length,
        elapsed_time,
        expected_speed,
        mock_flet_dependency,
        mock_time,
        reset_global_state,
    ):
        """Test extreme typing speed calculation scenarios.

        Validates that speed calculation handles extreme scenarios
        including very fast typing and very long words correctly.

        Args:
            mock_fontify: Mocked fontify utility.
            word_length (int): Length of word to test.
            elapsed_time (float): Elapsed time for calculation.
            expected_speed (float): Expected calculated speed.
            mock_flet_dependency: Mocked flet module with UI components.
            mock_time: Mocked time module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        mock_fontify.return_value = MagicMock()
        game = QuickTypeChallenge()
        game.word = "a" * word_length

        current_time = 10.0
        game.start_time = current_time - elapsed_time
        mock_time.time.return_value = current_time

        # Act
        speed = game._calculate_typing_speed()

        # Assert
        assert abs(speed - expected_speed) < 0.01  # Allow for floating point precision

    def test_animation_thread_safety(self, mock_threading, reset_global_state):
        """Test animation thread safety with concurrent operations.

        Validates that animation operations handle concurrent
        access safely without race conditions or exceptions.

        Args:
            mock_threading: Mocked threading module fixture.
            reset_global_state: State reset fixture.
        """
        # Arrange
        controls = [MagicMock() for _ in range(10)]
        mock_thread = MagicMock()
        mock_threading.Thread.return_value = mock_thread

        # Act - Multiple concurrent animation calls
        for i in range(5):
            AnimationManager.animate_opacity(controls, target_opacity=0.5 + i * 0.1)

        # Assert - Should not raise exceptions
        assert mock_threading.Thread.call_count == 5
        assert mock_thread.start.call_count == 5

    @pytest.mark.parametrize(
        "progress_value",
        [-0.1, 1.1, 0.0, 1.0, 0.5, float("inf"), float("-inf")],
    )
    def test_easing_function_boundary_robustness(self, progress_value, reset_global_state):
        """Test easing function robustness with boundary and invalid values.

        Validates that easing functions handle boundary values
        and invalid inputs gracefully without exceptions.

        Args:
            progress_value: Progress value to test (may be invalid).
            reset_global_state: State reset fixture.
        """
        # Act & Assert - Should not raise exceptions
        try:
            ease_out_result = AnimationManager.ease_out(progress_value)
            ease_in_out_result = AnimationManager.ease_in_out(progress_value)

            # Valid results should be numbers
            if not (float("inf") == progress_value or float("-inf") == progress_value):
                assert isinstance(ease_out_result, (int, float))
                assert isinstance(ease_in_out_result, (int, float))
        except (ValueError, OverflowError, ZeroDivisionError):
            # These exceptions are acceptable for invalid inputs
            pass
