"""Font management and text styling utilities for TJD-Toolkit GUI.

This module handles:
- Noto Sans font family loading and configuration
- Font variant management
- Text styling utilities for GUI components
- Theme integration with font settings

Example:
    >>> from gui.utils.font_utils import FontManager, fontify
    >>> manager = FontManager(page)
    >>> manager.setup_fonts()
    >>> styled_text = fontify("Hello", bold=True, size=16)
    >>> assert text.font_family == "NotoSansBold"

Attributes:
    __all__ (List[str]): Public interface exports.
    logger (logging.Logger): Module logger instance.
    GUI_DIR (Path): Base directory for GUI components.
    ASSETS_DIR (Path): Directory containing application assets.
    FONTS_DIR (Path): Directory containing Noto Sans font files.
    FONT_FILES (Dict[str, str]): Mapping of font variants to filenames.
    _FONTS_LOADED (bool): Flag indicating font loading status.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Optional

import flet as ft

from internal.core.exceptions import FontError

__all__ = ["FontManager", "fontify"]

logger: logging.Logger = logging.getLogger(__name__)

# Module-level constants and type annotations
GUI_DIR: Path = Path(__file__).parent.parent
ASSETS_DIR: Path = GUI_DIR / "assets"
FONTS_DIR: Path = ASSETS_DIR / "fonts" / "static" / "Noto_Sans"

FONT_FILES: Dict[str, str] = {
    "NotoSans": "NotoSans-Regular.ttf",
    "NotoSansBold": "NotoSans-Bold.ttf",
    "NotoSansItalic": "NotoSans-Italic.ttf",
    "NotoSansBoldItalic": "NotoSans-BoldItalic.ttf",
}

# Module-level font status
_FONTS_LOADED: bool = False


class FontManager:
    """Handle font loading and configuration.

    Manage Noto Sans font variants and their registration with the
    application's GUI system.

    Attributes:
        page (ft.Page): Target page for font registration.

    Example:
        >>> manager = FontManager(page)
        >>> manager.setup_fonts()
        >>> assert manager.fonts_loaded
    """

    def __init__(self, page: ft.Page) -> None:
        """Initialize font manager with target page.

        Args:
            page (ft.Page): Page instance for font registration.
        """
        self.page: ft.Page = page

    def setup_fonts(self) -> bool:
        """Load and register Noto Sans font variants.

        Load font files and register them with the application's GUI
        system for use in text styling.

        Returns:
            bool: True if all fonts loaded successfully.

        Raises:
            FontError: If fonts cannot be loaded or validated.

        Example:
            >>> success = manager.setup_fonts()
            >>> assert success is True
        """
        global _FONTS_LOADED
        _FONTS_LOADED = False

        # Check fonts directory exists
        if not FONTS_DIR.exists():
            error_msg = f"Fonts directory not found: {FONTS_DIR}"
            logger.error(error_msg)
            raise FontError(error_msg, font_path=str(FONTS_DIR))

        # Load and validate files
        fonts: Dict[str, str] = {}
        try:
            for font_name, filename in FONT_FILES.items():
                font_path = str(FONTS_DIR / filename)
                if not os.path.isfile(font_path):
                    error_msg = f"Font file not found: {font_path}"
                    logger.error(error_msg)
                    raise FontError(error_msg, font_name=font_name, font_path=font_path)
                fonts[font_name] = font_path

            # All fonts loaded successfully
            self.page.fonts = fonts
            _FONTS_LOADED = True
            return True

        except FontError:
            return False
        except Exception as e:
            error_msg = f"Unexpected error during font setup: {e}"
            logger.error(error_msg)
            raise FontError(error_msg, cause=e) from e

    @property
    def fonts_loaded(self) -> bool:
        """Return font loading status.

        Returns:
            bool: True if fonts are loaded and ready.

        Raises:
            FontError: If status check fails.

        Example:
            >>> assert manager.fonts_loaded is True
        """
        try:
            return bool(_FONTS_LOADED)
        except Exception as e:
            error_msg = f"Failed to check font loaded status: {e}"
            logger.error(error_msg)
            raise FontError(error_msg, cause=e) from e

    def get_theme(self) -> ft.Theme:
        """Create theme with appropriate font configuration.

        Returns:
            ft.Theme: Theme with Noto Sans if loaded, else system default.

        Raises:
            FontError: If theme creation fails.

        Example:
            >>> theme = manager.get_theme()
            >>> assert isinstance(theme, ft.Theme)
        """
        try:
            default_font = "NotoSans" if self.fonts_loaded else None
            return ft.Theme(font_family=default_font, use_material3=True)
        except Exception as e:
            error_msg = f"Failed to create theme: {e}"
            logger.error(error_msg)
            raise FontError(error_msg, cause=e) from e


def fontify(
    text: str,
    *,
    bold: bool = False,
    italic: bool = False,
    size: Optional[int] = None,
    **text_kwargs,
) -> ft.Text:
    """Create text widget with Noto Sans styling.

    Apply font styling using appropriate Noto Sans variant based on
    requested attributes.

    Args:
        text (str): Content to display.
        bold (bool, optional): Use bold weight. Defaults to False.
        italic (bool, optional): Use italic style. Defaults to False.
        size (Optional[int], optional): Text size in pixels.
        **text_kwargs: Additional Text widget parameters.

    Returns:
        ft.Text: Styled text widget.

    Raises:
        FontError: If styling fails (except font loading case).

    Example:
        >>> styled_text = fontify("Hello", bold=True, size=16)
        >>> styled_text.font_family
        'NotoSansBold'

    Raises:
        FontError: If text styling fails (except unloaded fonts case).
    """
    if not _FONTS_LOADED:
        logger.warning("Fonts not loaded, falling back to system default")
        return ft.Text(text, size=size, **text_kwargs)

    try:
        font_family = "NotoSans"
        if bold and italic:
            font_family = "NotoSansBoldItalic"
        elif bold:
            font_family = "NotoSansBold"
        elif italic:
            font_family = "NotoSansItalic"

        return ft.Text(
            text,
            font_family=font_family,
            size=size,
            **text_kwargs,
        )
    except Exception as e:
        error_msg = f"Failed to create styled text: {e}"
        logger.error(error_msg)
        raise FontError(error_msg, cause=e) from e
