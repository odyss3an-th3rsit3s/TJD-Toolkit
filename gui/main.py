"""Main entry point and core functionality for TJD-Toolkit GUI.

This module provides:
- Application lifecycle management
- Window setup and configuration
- Theme management and persistence
- Navigation routing and view handling

Example:
    >>> import flet as ft
    >>> ft.app(target=main)
    >>> # Application window opens with configured theme

Attributes:
    __all__ (List[str]): Public interface exports.
    logger (logging.Logger): Module-level logger instance.
"""

from __future__ import annotations

import logging
from typing import Any

import flet as ft

from internal.core.config import config
from internal.core.exceptions import (
    ConfigurationError,
    ThemeError,
    WindowError,
    ViewError,
    NavigationError,
)
from gui.utils.font_utils import FontManager
from gui.views.home import HomeView
from gui.views.PUC.featureeins import FeatureEinsView

__all__ = ["TJDToolkitApp", "main"]

logger = logging.getLogger(__name__)


class TJDToolkitApp:
    """Manage core application functionality and lifecycle.

    Handle window setup, theme configuration, routing and view management.
    Coordinates all GUI components and maintains application state.

    Attributes:
        DEFAULT_WIDTH (int): Initial window width in pixels.
        DEFAULT_HEIGHT (int): Initial window height in pixels.
        page (ft.Page): Main Flet UI container.
        font_manager (FontManager): Font configuration utility.

    Example:
        >>> page = ft.Page()
        >>> app = TJDToolkitApp(page)
        >>> assert isinstance(app.page, ft.Page)
    """

    DEFAULT_WIDTH: int = 1186
    DEFAULT_HEIGHT: int = 733

    def __init__(self, page: ft.Page) -> None:
        """Initialize application components and configuration.

        Args:
            page (ft.Page): Flet page instance for UI construction.

        Raises:
            ThemeError: If theme setup fails.
            WindowError: If window setup fails.
            NavigationError: If navigation setup fails.
        """
        try:
            self.page: ft.Page = page
            self.font_manager: FontManager = FontManager(page)

            # Setup components in order
            self.setup_theme()

            try:
                self.setup_page()
            except Exception as e:
                logger.error(f"Failed to setup page: {e}")
                raise WindowError("Failed to setup page", property_name="page_setup", cause=e)

            try:
                self.setup_navigation()
            except Exception as e:
                logger.error(f"Failed to setup navigation: {e}")
                raise NavigationError("Failed to setup navigation", route="/", cause=e)

            logger.info("TJDToolkitApp initialized successfully")

        except (ThemeError, WindowError, NavigationError):
            raise
        except Exception as e:
            # Catch any other unexpected exceptions
            logger.error(f"Unexpected error during TJDToolkitApp initialization: {e}")
            raise ThemeError(
                "Unexpected error during application initialization", component="app_init", cause=e
            )

    def _get_theme_mode(self, mode: str) -> ft.ThemeMode:
        """Convert string theme mode to Flet enum value.

        Args:
            mode (str): Theme identifier ("light", "dark" or "system").

        Returns:
            ft.ThemeMode: Corresponding Flet theme mode enum.

        Example:
            >>> app._get_theme_mode("dark")
            <ThemeMode.DARK: 'dark'>
        """
        theme_map = {
            "light": ft.ThemeMode.LIGHT,
            "dark": ft.ThemeMode.DARK,
            "system": ft.ThemeMode.SYSTEM,
        }
        return theme_map.get(mode.lower(), ft.ThemeMode.SYSTEM)

    def setup_theme(self) -> None:
        """Configure application theme and fonts.

        Set up font management, apply theme configuration and handle fallbacks
        for error cases.

        Raises:
            ThemeError: If theme configuration fails to load or apply.

        Note:
            Falls back to system theme mode on error.
        """
        try:
            self.font_manager.setup_fonts()
            self.page.theme = self.font_manager.get_theme()
            theme_mode = config.get("theme", "system")
            self.page.theme_mode = self._get_theme_mode(theme_mode)
            self.page.update()
        except ConfigurationError as e:
            logger.error(f"Failed to setup theme: {e}")
            # Fallback to system theme mode
            self.page.theme_mode = ft.ThemeMode.SYSTEM
            raise ThemeError(
                "Failed to configure theme settings",
                theme_name=config.get("theme", "system"),
                component="theme_setup",
                cause=e,
            )
        except Exception as e:
            error_msg = f"Unexpected error during theme setup: {e}"
            logger.error(error_msg)
            # Fallback to system theme
            self.page.theme_mode = ft.ThemeMode.SYSTEM
            raise ThemeError(error_msg, component="theme_setup", cause=e)

    def setup_page(self) -> None:
        """Initialize main application window.

        Configure window title, dimensions and other properties using saved
        settings or defaults.

        Raises:
            WindowError: If window setup fails.
            ConfigurationError: If loading window settings fails.
        """
        try:
            self.page.title = "TJD Toolkit"

            # Try to get window dimensions from config, fallback to defaults
            try:
                window_width = config.get("window.width", self.DEFAULT_WIDTH)
                window_height = config.get("window.height", self.DEFAULT_HEIGHT)
            except ConfigurationError as e:
                logger.warning(f"Failed to load window config, using defaults: {e}")
                window_width = self.DEFAULT_WIDTH
                window_height = self.DEFAULT_HEIGHT

            self.page.window.width = window_width
            self.page.window.height = window_height

        except Exception as e:
            error_msg = f"Failed to setup page: {e}"
            logger.error(error_msg)
            raise WindowError(error_msg, property_name="page_setup", cause=e)

    def setup_navigation(self) -> None:
        """Configure application routing.

        Set up route handlers and initialize navigation to home view.

        Raises:
            NavigationError: If navigation setup fails.
        """
        try:
            self.page.on_route_change = self._handle_route_change
            self.page.on_view_pop = self._handle_view_pop
            self.page.go("/")
        except Exception as e:
            error_msg = f"Failed to setup navigation: {e}"
            logger.error(error_msg)
            raise NavigationError(error_msg, route="/", cause=e)

    def _handle_route_change(self, route: ft.RouteChangeEvent) -> None:
        """Process navigation route changes.

        Clear view stack, load new view for route, handle errors gracefully.

        Args:
            route (ft.RouteChangeEvent): Navigation event data.

        Raises:
            ViewError: If route is invalid or view fails to load.
            NavigationError: If navigation state becomes invalid.

        Note:
            Redirects to home view on error.
        """
        current_route = str(self.page.route or "/")

        try:
            self.page.views.clear()

            route_map = {
                "/": HomeView,
                "/featureeins": FeatureEinsView,
                # Add tool routes here
            }

            view_class = route_map.get(current_route)
            if view_class is None:
                error_msg = f"Unknown route: {current_route}"
                logger.error(error_msg)
                self.page.go("/")  # Redirect to home on invalid route
                raise ViewError(error_msg, route=current_route)

            try:
                view = view_class(self.page)
                self.page.views.append(view)
                self.page.update()
            except Exception as e:
                error_msg = f"Failed to initialize view for route {current_route}"
                logger.error(f"{error_msg}: {e}")
                self.page.go("/")  # Redirect to home on error
                raise ViewError(
                    error_msg,
                    route=current_route,
                    view_name=getattr(view_class, "__name__", "UnknownView"),
                    cause=e,
                )

        except ViewError:
            # Re-raise view errors to maintain error context
            raise
        except Exception as e:
            error_msg = f"Unexpected error handling route {current_route}"
            logger.error(f"{error_msg}: {e}")
            self.page.go("/")  # Redirect to home on error
            raise NavigationError(error_msg, route=current_route, cause=e)

    def _handle_view_pop(self, view: Any) -> None:
        """Handle view stack pop operations.

        Remove top view and update navigation state.

        Args:
            view (Any): View being removed from stack.

        Raises:
            NavigationError: If view stack becomes invalid.
        """
        try:
            if self.page.views:  # Check if list is not empty
                self.page.views.pop()
                if self.page.views:
                    top_view = self.page.views[-1]
                    route = getattr(top_view, "route", "/")
                    self.page.go(str(route))
        except Exception as e:
            error_msg = f"Error handling view pop: {e}"
            logger.error(error_msg)
            raise NavigationError(error_msg, cause=e)


def main(page: ft.Page) -> None:
    """Initialize and launch TJD Toolkit application.

    Set up application instance, configure window event handlers,
    and start the main application loop.

    Args:
        page (ft.Page): Root Flet page for UI construction.

    Raises:
        ThemeError: If theme setup fails.
        WindowError: If window configuration fails.
        NavigationError: If routing setup fails.

    Example:
        >>> ft.app(target=main)
        >>> # Application launches with configured window
    """
    try:
        TJDToolkitApp(page)

        def handle_window_event(e: ft.WindowEvent) -> None:
            """Process window events and persist configuration.

            Args:
                e (ft.WindowEvent): Window event containing type and data.

            Raises:
                WindowError: If saving window settings fails.
            """
            try:
                if e.type == "resize":
                    config.set("window.width", page.window.width)
                    config.set("window.height", page.window.height)
                    config.save()
                elif e.type == "close":
                    config.save()
            except ConfigurationError as err:
                error_msg = f"Failed to save window settings: {err}"
                logger.error(error_msg)
                raise WindowError(error_msg, property_name="window_event", cause=err)
            except Exception as err:
                error_msg = f"Unexpected error handling window event: {err}"
                logger.error(error_msg)
                raise WindowError(error_msg, property_name="window_event", cause=err)

        page.window.on_event = handle_window_event

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ft.app(target=main)
