"""Test suite for the font utilities module in the TJD-Toolkit.

This module contains comprehensive test coverage for the FontManager class and
fontify function, including font loading, error handling, and UI text styling
functionality.

The test suite covers:
    - FontManager initialization and setup
    - Font loading success and error scenarios
    - Theme generation based on font state
    - Text styling with the fontify function
    - Comprehensive error handling and edge cases
    - Integration workflows

Example:
    Run the test suite with pytest:
        $ pytest test_font_utils.py -v
"""

from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from gui.utils.font_utils import FontManager, fontify
from internal.core.exceptions import FontError


@pytest.fixture(autouse=True)
def mock_dependencies():
    """Mock external dependencies while keeping internal exceptions real.

    Automatically applied to all tests to ensure external dependencies
    like flet are properly mocked without affecting internal exception
    handling logic.

    Yields:
        None: Context manager yields control to test execution.
    """
    with patch.dict("sys.modules", {"flet": MagicMock()}):
        yield


@pytest.fixture
def mock_page():
    """Create mock Flet page object for testing.

    Provides a standardized mock page object with fonts attribute
    initialized as an empty dictionary for consistent testing.

    Returns:
        MagicMock: Mock page object with fonts attribute set.
    """
    page = MagicMock()
    page.fonts = {}
    return page


@pytest.fixture
def reset_fonts_loaded():
    """Reset the global _FONTS_LOADED variable before each test.

    Ensures test isolation by resetting the global font loading state
    to False before each test execution, preventing state leakage
    between tests.

    Yields:
        None: Context manager yields control to test execution.
    """
    with patch("gui.utils.font_utils._FONTS_LOADED", False):
        yield


class TestFontManagerCore:
    """Test FontManager initialization and core functionality.

    This class contains tests for basic FontManager operations including
    initialization and core property access functionality.
    """

    @patch("gui.utils.font_utils.ft")
    def test_initialization_stores_page_reference(self, mock_ft, mock_page):
        """Test FontManager initialization stores page reference correctly.

        Args:
            mock_ft: Mocked flet module.
            mock_page: Mock page fixture.
        """
        # Arrange & Act
        manager = FontManager(mock_page)

        # Assert
        assert manager.page == mock_page

    @pytest.mark.parametrize(
        "fonts_loaded_state,expected",
        [
            (True, True),
            (False, False),
        ],
    )
    @patch("gui.utils.font_utils.ft")
    def test_fonts_loaded_property(self, mock_ft, fonts_loaded_state, expected, mock_page):
        """Test fonts_loaded property returns correct state.

        Args:
            mock_ft: Mocked flet module.
            fonts_loaded_state (bool): State to set for _FONTS_LOADED.
            expected (bool): Expected return value.
            mock_page: Mock page fixture.
        """
        # Arrange
        manager = FontManager(mock_page)

        # Act & Assert
        with patch("gui.utils.font_utils._FONTS_LOADED", fonts_loaded_state):
            assert manager.fonts_loaded is expected


class TestFontManagerSetup:
    """Test FontManager font setup functionality.

    This class contains comprehensive tests for font setup operations
    including success scenarios, error handling, and edge cases.
    """

    @patch("gui.utils.font_utils.FONTS_DIR")
    @patch("gui.utils.font_utils.os.path.isfile")
    @patch("gui.utils.font_utils.ft")
    def test_setup_fonts_success_workflow(
        self, mock_ft, mock_isfile, mock_fonts_dir, mock_page, reset_fonts_loaded
    ):
        """Test successful font setup returns True and configures fonts.

        Args:
            mock_ft: Mocked flet module.
            mock_isfile: Mocked os.path.isfile function.
            mock_fonts_dir: Mocked FONTS_DIR constant.
            mock_page: Mock page fixture.
            reset_fonts_loaded: Font state reset fixture.
        """
        # Arrange
        mock_fonts_dir.exists.return_value = True
        mock_isfile.return_value = True
        manager = FontManager(mock_page)

        # Act
        result = manager.setup_fonts()

        # Assert
        assert result is True
        assert manager.page.fonts is not None

    @patch("gui.utils.font_utils.FONTS_DIR")
    @patch("gui.utils.font_utils.ft")
    def test_setup_fonts_directory_missing_with_detailed_error(
        self, mock_ft, mock_fonts_dir, mock_page, reset_fonts_loaded
    ):
        """Test setup_fonts raises FontError when directory missing.

        Validates that FontError contains correct attributes when the
        fonts directory is not found on the filesystem.

        Args:
            mock_ft: Mocked flet module.
            mock_fonts_dir: Mocked FONTS_DIR constant.
            mock_page: Mock page fixture.
            reset_fonts_loaded: Font state reset fixture.

        Raises:
            FontError: Expected exception when directory missing.
        """
        # Arrange
        mock_fonts_dir.exists.return_value = False
        mock_fonts_dir.__str__.return_value = "/missing/fonts/path"
        manager = FontManager(mock_page)

        # Act & Assert
        with pytest.raises(FontError) as exc_info:
            manager.setup_fonts()

        # Comprehensive error attribute validation
        error = exc_info.value
        assert "Fonts directory not found" in error.message
        assert error.font_path == "/missing/fonts/path"
        assert error.font_name is None
        assert error.cause is None

    @pytest.mark.parametrize(
        "missing_file,expected_result",
        [
            ("NotoSans-Regular.ttf", False),
            ("NotoSans-Bold.ttf", False),
        ],
    )
    @patch("gui.utils.font_utils.FONTS_DIR")
    @patch("gui.utils.font_utils.os.path.isfile")
    @patch("gui.utils.font_utils.ft")
    def test_setup_fonts_file_missing_scenarios(
        self,
        mock_ft,
        mock_isfile,
        mock_fonts_dir,
        missing_file,
        expected_result,
        mock_page,
        reset_fonts_loaded,
    ):
        """Test setup_fonts handles missing font files correctly.

        Args:
            mock_ft: Mocked flet module.
            mock_isfile: Mocked os.path.isfile function.
            mock_fonts_dir: Mocked FONTS_DIR constant.
            missing_file (str): Name of missing font file.
            expected_result (bool): Expected return value.
            mock_page: Mock page fixture.
            reset_fonts_loaded: Font state reset fixture.
        """
        # Arrange
        mock_fonts_dir.exists.return_value = True
        mock_fonts_dir.__truediv__.return_value = Path(f"/fonts/static/{missing_file}")
        mock_isfile.return_value = False
        manager = FontManager(mock_page)

        # Act
        result = manager.setup_fonts()

        # Assert
        assert result is expected_result
        assert manager.fonts_loaded is False

    @patch("gui.utils.font_utils.FONTS_DIR")
    @patch("gui.utils.font_utils.os.path.isfile")
    @patch("gui.utils.font_utils.ft")
    def test_setup_fonts_unexpected_error_with_cause_chain(
        self, mock_ft, mock_isfile, mock_fonts_dir, mock_page, reset_fonts_loaded
    ):
        """Test setup_fonts handles unexpected errors with cause chaining.

        Args:
            mock_ft: Mocked flet module.
            mock_isfile: Mocked os.path.isfile function.
            mock_fonts_dir: Mocked FONTS_DIR constant.
            mock_page: Mock page fixture.
            reset_fonts_loaded: Font state reset fixture.

        Raises:
            FontError: Expected exception with cause chain.
        """
        # Arrange
        mock_fonts_dir.exists.return_value = True
        mock_isfile.return_value = True
        original_error = ValueError("Unexpected system error")

        def fonts_setter(self, value):
            raise original_error

        type(mock_page).fonts = property(lambda x: {}, fonts_setter)
        manager = FontManager(mock_page)

        # Act & Assert
        with pytest.raises(FontError) as exc_info:
            manager.setup_fonts()

        # Verify error attributes and cause chain
        error = exc_info.value
        assert "Unexpected error during font setup" in error.message
        assert error.cause == original_error


class TestFontManagerTheme:
    """Test FontManager theme functionality.

    This class contains tests for theme generation based on font
    loading state and error handling in theme creation.
    """

    @pytest.mark.parametrize(
        "fonts_loaded,expected_font_family",
        [
            (True, "NotoSans"),
            (False, None),
        ],
    )
    @patch("gui.utils.font_utils.ft")
    def test_get_theme_based_on_font_state(
        self, mock_ft, fonts_loaded, expected_font_family, mock_page
    ):
        """Test get_theme returns appropriate theme based on font state.

        Args:
            mock_ft: Mocked flet module.
            fonts_loaded (bool): Font loading state to simulate.
            expected_font_family (str or None): Expected font family.
            mock_page: Mock page fixture.
        """
        # Arrange
        mock_theme = MagicMock()
        mock_ft.Theme.return_value = mock_theme
        manager = FontManager(mock_page)

        # Act
        with patch.object(
            FontManager, "fonts_loaded", new_callable=PropertyMock, return_value=fonts_loaded
        ):
            manager.get_theme()

        # Assert
        mock_ft.Theme.assert_called_once_with(font_family=expected_font_family, use_material3=True)

    @patch("gui.utils.font_utils.ft")
    def test_get_theme_exception_handling_with_detailed_error(self, mock_ft, mock_page):
        """Test get_theme raises FontError with proper attributes.

        Args:
            mock_ft: Mocked flet module.
            mock_page: Mock page fixture.

        Raises:
            FontError: Expected exception with proper cause.
        """
        # Arrange
        original_error = RuntimeError("Theme creation failed")
        mock_ft.Theme.side_effect = original_error
        manager = FontManager(mock_page)

        # Act & Assert
        with pytest.raises(FontError) as exc_info:
            manager.get_theme()

        # Verify comprehensive error details
        error = exc_info.value
        assert "Failed to create theme" in error.message
        assert error.cause == original_error


class TestFontifyFunctionality:
    """Test fontify function with comprehensive styling scenarios.

    This class contains tests for the fontify function covering all
    style combinations, parameters, and error handling scenarios.
    """

    @pytest.mark.parametrize(
        "bold,italic,expected_family",
        [
            (False, False, "NotoSans"),
            (True, False, "NotoSansBold"),
            (False, True, "NotoSansItalic"),
            (True, True, "NotoSansBoldItalic"),
        ],
    )
    @patch("gui.utils.font_utils._FONTS_LOADED", True)
    @patch("gui.utils.font_utils.ft")
    def test_fontify_style_combinations_comprehensive(self, mock_ft, bold, italic, expected_family):
        """Test fontify applies correct font family for style combinations.

        Args:
            mock_ft: Mocked flet module.
            bold (bool): Bold styling flag.
            italic (bool): Italic styling flag.
            expected_family (str): Expected font family name.
        """
        # Arrange
        mock_text = MagicMock()
        mock_ft.Text.return_value = mock_text

        # Act
        fontify("Test Text", bold=bold, italic=italic)

        # Assert
        mock_ft.Text.assert_called_once_with("Test Text", font_family=expected_family, size=None)

    @pytest.mark.parametrize(
        "size,extra_kwargs",
        [
            (16, {}),
            (None, {"color": "red"}),
            (20, {"color": "blue", "weight": "bold"}),
        ],
    )
    @patch("gui.utils.font_utils._FONTS_LOADED", True)
    @patch("gui.utils.font_utils.ft")
    def test_fontify_parameters_and_kwargs(self, mock_ft, size, extra_kwargs):
        """Test fontify handles size and additional kwargs correctly.

        Args:
            mock_ft: Mocked flet module.
            size (int or None): Font size parameter.
            extra_kwargs (dict): Additional keyword arguments.
        """
        # Arrange
        mock_text = MagicMock()
        mock_ft.Text.return_value = mock_text

        # Act
        fontify("Test Text", size=size, **extra_kwargs)

        # Assert
        expected_call = {"font_family": "NotoSans", "size": size, **extra_kwargs}
        mock_ft.Text.assert_called_once_with("Test Text", **expected_call)

    @patch("gui.utils.font_utils._FONTS_LOADED", False)
    @patch("gui.utils.font_utils.ft")
    def test_fontify_fallback_behavior_when_fonts_not_loaded(self, mock_ft):
        """Test fontify gracefully falls back when fonts not loaded.

        Args:
            mock_ft: Mocked flet module.
        """
        # Arrange
        mock_text = MagicMock()
        mock_ft.Text.return_value = mock_text

        # Act
        fontify("Fallback Text", size=14, color="red")

        # Assert
        mock_ft.Text.assert_called_once_with("Fallback Text", size=14, color="red")

    @patch("gui.utils.font_utils._FONTS_LOADED", True)
    @patch("gui.utils.font_utils.ft")
    def test_fontify_exception_handling_with_detailed_error(self, mock_ft):
        """Test fontify raises FontError with proper cause on exception.

        Args:
            mock_ft: Mocked flet module.

        Raises:
            FontError: Expected exception with proper cause.
        """
        # Arrange
        original_error = RuntimeError("Text creation failed")
        mock_ft.Text.side_effect = original_error

        # Act & Assert
        with pytest.raises(FontError) as exc_info:
            fontify("Error Text")

        # Verify comprehensive error information
        error = exc_info.value
        assert "Failed to create styled text" in error.message
        assert error.cause == original_error


class TestErrorHandlingComprehensive:
    """Test comprehensive error scenarios and edge cases.

    This class contains tests for various error conditions and edge
    cases that may occur during font operations.
    """

    @patch("gui.utils.font_utils.ft")
    def test_fonts_loaded_property_exception_with_detailed_attributes(self, mock_ft, mock_page):
        """Test fonts_loaded property exception handling.

        Validates comprehensive error details when the fonts_loaded
        property encounters an unexpected exception.

        Args:
            mock_ft: Mocked flet module.
            mock_page: Mock page fixture.

        Raises:
            FontError: Expected exception with proper cause.
        """
        # Arrange
        manager = FontManager(mock_page)
        original_error = RuntimeError("System error")

        class ExceptionRaiser:
            def __bool__(self):
                raise original_error

        # Act & Assert
        with patch("gui.utils.font_utils._FONTS_LOADED", ExceptionRaiser()):
            with pytest.raises(FontError) as exc_info:
                _ = manager.fonts_loaded

            # Verify comprehensive error details
            error = exc_info.value
            assert "Failed to check font loaded status" in error.message
            assert error.cause == original_error

    def test_font_error_inheritance_and_attributes_comprehensive(self):
        """Test FontError inheritance chain and attribute storage.

        Validates that FontError properly inherits from base exception
        classes and stores all required attributes correctly.
        """
        # Arrange
        from internal.core.exceptions import GUIError, TJDError

        # Act
        font_error = FontError("Test error", font_name="TestFont", font_path="/test/path")

        # Assert
        # Test inheritance chain
        assert isinstance(font_error, FontError)
        assert isinstance(font_error, GUIError)
        assert isinstance(font_error, TJDError)
        assert isinstance(font_error, Exception)

        # Test attribute storage
        assert font_error.font_name == "TestFont"
        assert font_error.font_path == "/test/path"
        assert font_error.message == "Test error"


class TestModuleConstantsAndIntegration:
    """Test module constants and integration workflows.

    This class contains tests for module-level constants and complete
    integration workflows that combine multiple components.
    """

    def test_font_files_mapping_completeness_and_structure(self):
        """Test FONT_FILES constant contains all expected font variants.

        Validates that the FONT_FILES constant is complete and has the
        correct structure for all required font style combinations.
        """
        # Arrange
        from gui.utils.font_utils import FONT_FILES

        expected_files = {
            "NotoSans": "NotoSans-Regular.ttf",
            "NotoSansBold": "NotoSans-Bold.ttf",
            "NotoSansItalic": "NotoSans-Italic.ttf",
            "NotoSansBoldItalic": "NotoSans-BoldItalic.ttf",
        }

        # Act & Assert
        assert FONT_FILES == expected_files
        assert len(FONT_FILES) == 4  # Ensure completeness

    @patch("gui.utils.font_utils.FONTS_DIR")
    @patch("gui.utils.font_utils.os.path.isfile")
    @patch("gui.utils.font_utils.ft")
    def test_complete_success_workflow_end_to_end(
        self, mock_ft, mock_isfile, mock_fonts_dir, mock_page, reset_fonts_loaded
    ):
        """Test complete successful workflow from initialization to text.

        Validates the entire successful workflow from FontManager
        initialization through font setup to styled text creation.

        Args:
            mock_ft: Mocked flet module.
            mock_isfile: Mocked os.path.isfile function.
            mock_fonts_dir: Mocked FONTS_DIR constant.
            mock_page: Mock page fixture.
            reset_fonts_loaded: Font state reset fixture.
        """
        # Arrange
        mock_fonts_dir.exists.return_value = True
        mock_isfile.return_value = True
        mock_text = MagicMock()
        mock_ft.Text.return_value = mock_text

        # Act
        manager = FontManager(mock_page)
        setup_result = manager.setup_fonts()
        manager.get_theme()
        fontify("Test Text", bold=True, size=16)

        # Assert
        assert setup_result is True
        assert manager.fonts_loaded is True
        mock_ft.Text.assert_called_with("Test Text", font_family="NotoSansBold", size=16)

    @patch("gui.utils.font_utils.FONTS_DIR")
    @patch("gui.utils.font_utils.ft")
    def test_complete_error_workflow_with_graceful_degradation(
        self, mock_ft, mock_fonts_dir, mock_page, reset_fonts_loaded
    ):
        """Test complete workflow handles errors gracefully.

        Validates that the system handles errors gracefully and provides
        appropriate fallback behavior when font loading fails.

        Args:
            mock_ft: Mocked flet module.
            mock_fonts_dir: Mocked FONTS_DIR constant.
            mock_page: Mock page fixture.
            reset_fonts_loaded: Font state reset fixture.

        Raises:
            FontError: Expected exception during setup phase.
        """
        # Arrange
        mock_fonts_dir.exists.return_value = False
        mock_fonts_dir.__str__.return_value = "/missing/fonts"
        mock_text = MagicMock()
        mock_ft.Text.return_value = mock_text

        # Act & Assert
        manager = FontManager(mock_page)

        # Test error during setup
        with pytest.raises(FontError) as exc_info:
            manager.setup_fonts()

        error = exc_info.value
        assert "Fonts directory not found" in error.message
        assert error.font_path == "/missing/fonts"

        # Test graceful fallback in fontify
        fontify("Fallback Text", size=14)
        mock_ft.Text.assert_called_with("Fallback Text", size=14)
