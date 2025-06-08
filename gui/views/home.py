"""Provide main navigation interface for TJD Toolkit GUI.

This module implements the home view that serves as the main entry point
for accessing various tools and features of the TJD Toolkit application.
It provides a grid-based interface for tool selection and navigation.

Example:
    >>> page = ft.Page()
    >>> view = HomeView(page)
    >>> page.views.append(view)
    >>> view.setup_ui()

Attributes:
    __all__ (List[str]): Public interface exports.
    logger (logging.Logger): Module-level logging instance.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import flet as ft

from gui.utils.font_utils import fontify
from internal.core.exceptions import HomeViewError

__all__ = ["HomeView"]

logger: logging.Logger = logging.getLogger(__name__)


class HomeView(ft.View):
    """Present main navigation interface for TJD Toolkit.

    Provides a grid-based interface for accessing various tools and features,
    including loading states and navigation controls.

    Attributes:
        COMING_SOON_TOOLS (List[str]): Names of tools under development.
        page (ft.Page): Parent page instance for this view.
        route (str): URL route for this view.
        title (str): Display title for this view.
        _loading_text (ft.Text): Text widget for loading messages.
        _loading_overlay (ft.Stack): Container for loading indicator.

    Example:
        >>> page = ft.Page()
        >>> view = HomeView(page)
        >>> view.setup_ui()
        >>> assert view.route == "/"

    Raises:
        HomeViewError: When view initialization or critical operations fail.
    """

    AVAILABLE_TOOLS: Dict[str, Dict[str, Any]] = {
        "Feature Eins": {
            "description": "Wouldn't you like to know...",
            "icon": ft.Icons.HOURGLASS_EMPTY,
            "color": ft.Colors.ORANGE,
        },
    }

    COMING_SOON_TOOLS: List[str] = [
        "Feature Zwei",
        # "Feature Drei"
        # "Feature Vier",
        # "Feature Fünf"
    ]

    def __init__(self, page: ft.Page | None) -> None:
        """Initialize home view with required components.

        Args:
            page (ft.Page | None): Parent page instance for view integration.
                                   None values are validated and rejected with HomeViewError.

        Raises:
            HomeViewError: When initialization fails due to invalid parameters
                or component creation errors.
        """
        if not isinstance(page, ft.Page):
            raise HomeViewError(
                "Cannot initialize HomeView with None page reference",
                route="/",
                view_name="HomeView",
                component="page_validation",
            )

        super().__init__()
        self.page: ft.Page = page
        self.route: str = "/"
        self.title: str = "TJD Toolkit - Homepage"

        # Store loading text reference
        self._loading_text: ft.Text = ft.Text("", size=16, color=ft.Colors.WHITE)

        # Add loading overlay components
        self._loading_overlay: ft.Stack = self._create_loading_overlay()
        self.setup_ui()

    def _create_loading_overlay(self) -> ft.Stack:
        """Create loading indicator overlay component.

        Constructs a semi-transparent overlay with progress indicator and
        loading message display.

        Returns:
            ft.Stack: Configured loading overlay container.

        Raises:
            HomeViewError: When loading overlay creation fails.
        """
        try:
            return ft.Stack(
                controls=[
                    ft.Container(
                        bgcolor=ft.Colors.BLACK54,
                        border_radius=10,
                        width=375,
                        height=230,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.ProgressRing(
                                    width=50, height=50, color=ft.Colors.LIGHT_BLUE_ACCENT_400
                                ),
                                self._loading_text,
                            ],
                            spacing=20,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        width=375,
                        height=230,
                    ),
                ],
                width=375,
                height=230,
                alignment=ft.alignment.center,
                visible=False,
            )
        except Exception as e:
            logger.error(f"Failed to create loading overlay: {e}")
            raise HomeViewError(
                "Failed to create loading overlay",
                route=self.route,
                view_name="HomeView",
                component="loading_overlay",
                cause=e,
            )

    def setup_ui(self) -> None:
        """Configure and arrange user interface components.

        Creates and arranges the header, tools grid, and loading overlay
        into the main view layout.

        Raises:
            HomeViewError: When UI component creation or layout arrangement fails.
        """
        try:
            header = self._create_header()
            tools_grid = self._create_tools_grid()
            self.controls = [
                ft.Stack(
                    controls=[
                        ft.Container(
                            content=ft.Column([header, tools_grid]), padding=20, expand=True
                        ),
                        self._loading_overlay,
                    ],
                    expand=True,
                    alignment=ft.alignment.center,
                )
            ]
        except HomeViewError:
            raise
        except Exception as e:
            logger.error(f"Failed to setup UI components: {e}")
            raise HomeViewError(
                "Failed to setup UI components",
                route=self.route,
                view_name="HomeView",
                component="main_layout",
                cause=e,
            )

    def _show_loading(self, message: str) -> None:
        """Display loading overlay with specified message.

        Args:
            message (str): Status message to show during loading.

        Raises:
            HomeViewError: When loading overlay display fails.
        """
        try:
            self._loading_text.value = message
            self._loading_overlay.visible = True
            self.update()
        except Exception as e:
            logger.error(f"Failed to show loading overlay: {e}")
            raise HomeViewError(
                "Failed to display loading overlay",
                route=self.route,
                view_name="HomeView",
                component="loading_display",
                cause=e,
            )

    def _hide_loading(self) -> None:
        """Hide loading overlay and update view.

        Raises:
            HomeViewError: When loading overlay hiding fails.
        """
        try:
            self._loading_overlay.visible = False
            self.update()
        except Exception as e:
            logger.error(f"Failed to hide loading overlay: {e}")
            raise HomeViewError(
                "Failed to hide loading overlay",
                route=self.route,
                view_name="HomeView",
                component="loading_hide",
                cause=e,
            )

    def _navigate_to_tool(self, route: str, tool_name: str) -> None:
        """Navigate to specified tool with loading indication.

        Args:
            route (str): Target route path for navigation.
            tool_name (str): Name of tool to display in loading message.

        Raises:
            HomeViewError: When navigation fails or parameters are invalid.
        """
        # Strategic validation for critical parameters
        if not route or not tool_name:
            raise HomeViewError(
                "Navigation requires valid route and tool name",
                route=self.route,
                view_name="HomeView",
                component="navigation_validation",
            )

        try:
            self._show_loading(f"Loading {tool_name} ...")
            self.page.go(route)
        except HomeViewError:
            self._hide_loading()  # Ensure loading overlay is hidden on error
            raise
        except Exception as e:
            self._hide_loading()
            logger.error(f"Failed to navigate to tool '{tool_name}' at route '{route}': {e}")
            raise HomeViewError(
                f"Failed to navigate to {tool_name}",
                route=route,
                view_name="HomeView",
                component="navigation",
                cause=e,
            )

    def _create_header(self) -> ft.Container:
        """Create main header section of the view.

        Returns:
            ft.Container: Header container with title and subtitle.

        Raises:
            HomeViewError: When header creation or text styling fails.
        """
        try:
            return ft.Container(
                content=ft.Column(
                    [
                        fontify("TJD Toolkit", bold=True, size=32),
                        fontify(
                            "{ A collection of simple tools for your digital toolbelt }",
                            size=16,
                            italic=True,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.only(bottom=30),
            )
        except Exception as e:
            logger.error(f"Failed to create header: {e}")
            raise HomeViewError(
                "Failed to create header",
                route=self.route,
                view_name="HomeView",
                component="header",
                cause=e,
            )

    def _create_tools_grid(self) -> ft.GridView:
        """Create grid layout for tool selection.

        Generate a grid view containing cards for available tools and
        placeholder cards for upcoming features.

        Returns:
            ft.GridView: Grid container with tool cards.

        Raises:
            HomeViewError: When grid creation or card population fails.
        """
        try:
            tools_grid = ft.GridView(
                expand=1,
                runs_count=2,
                max_extent=300,
                child_aspect_ratio=1.5,
                spacing=10,
                run_spacing=10,
            )

            # Add available tools
            for tool_name, tool_config in self.AVAILABLE_TOOLS.items():
                try:
                    tools_grid.controls.append(
                        self._create_tool_card(
                            tool_name,
                            tool_config["description"],
                            tool_config["icon"],
                            tool_config["color"],
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to create card for {tool_name}: {e}")
                    raise HomeViewError(
                        f"Failed to create card for {tool_name}",
                        route=self.route,
                        view_name="HomeView",
                        component="available_tool_card",
                        cause=e,
                    )

            # Add coming soon tools
            for tool_name in self.COMING_SOON_TOOLS:
                try:
                    tools_grid.controls.append(self._create_coming_soon_card(tool_name))
                except Exception as e:
                    logger.warning(f"Failed to create card for {tool_name}: {e}")
                    raise HomeViewError(
                        f"Failed to create card for {tool_name}",
                        route=self.route,
                        view_name="HomeView",
                        component="coming_soon_tool_card",
                        cause=e,
                    )

            return tools_grid
        except HomeViewError:
            raise
        except Exception as e:
            logger.error(f"Failed to create tools grid: {e}")
            raise HomeViewError(
                "Failed to create tools grid",
                route=self.route,
                view_name="HomeView",
                component="tools_grid",
                cause=e,
            )

    def _handle_card_hover(
        self, e: Optional[ft.ControlEvent] = None, card: Optional[ft.Card] = None
    ) -> None:
        """Handle mouse hover events for tool cards.

        Args:
            e (Optional[ft.ControlEvent]): Hover event data. Defaults to None.
            card (Optional[ft.Card]): Card to update. Defaults to None.

        Note:
            This method gracefully handles errors without raising exceptions
            to prevent disrupting user interaction.
        """
        try:
            if e and card:
                card.elevation = 8 if e.data == "true" else 2
                card.update()
        except Exception as err:
            # Log but don't raise - hover effects must not break the app
            logger.debug(f"Card hover effect failed: {err}")

    def _create_coming_soon_card(self, tool_name: str) -> ft.Card:
        """Create placeholder card for upcoming tool.

        Args:
            tool_name (str): Name of the upcoming tool.

        Returns:
            ft.Card: Non-interactive card showing upcoming tool.

        Raises:
            HomeViewError: When card creation or component styling fails.
        """
        try:
            return ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.HOURGLASS_EMPTY, size=40, color=ft.Colors.GREY),
                            ft.Text(tool_name, weight=ft.FontWeight.BOLD),
                            ft.Text("Coming soon...", size=12, italic=True),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                )
            )
        except Exception as e:
            logger.error(f"Failed to create coming soon card for '{tool_name}': {e}")
            raise HomeViewError(
                f"Failed to create coming soon card for {tool_name}",
                route=self.route,
                view_name="HomeView",
                component="coming_soon_card",
                cause=e,
            )

    def _create_tool_card(
        self, tool_name: str, tool_description: str, icon: ft.Icons, color: ft.Colors
    ) -> ft.Card:
        """Create card component for specified tool.

        Args:
            tool_name (str): Name of the specified tool.
            tool_description (str): Description text displayed on the tool card.
            icon (ft.Icons): Icon to display on the card. Defaults to REFRESH.
            color (ft.Colors): Color of the icon. Defaults to BLUE.

        Returns:
            ft.Card: Interactive card for launching specified tool.

        Raises:
            HomeViewError: When card creation or component styling fails.
        """
        try:
            route_name = "/" + tool_name.replace(" ", "").lower()

            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(icon, size=40, color=color),
                            ft.Text(tool_name, weight=ft.FontWeight.BOLD),
                            ft.Text(tool_description, size=12),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                    on_click=lambda _: self._navigate_to_tool(route_name, tool_name),
                    animate_scale=300,  # Duration in milliseconds
                    animate_opacity=300,
                    on_hover=lambda e: self._handle_card_hover(e, card),
                ),
                elevation=2,
            )
            return card
        except Exception as e:
            logger.error(f"Failed to create coming soon card for '{tool_name}': {e}")
            raise HomeViewError(
                f"Failed to create coming soon card for {tool_name}",
                route=self.route,
                view_name="HomeView",
                component="available_card",
                cause=e,
            )
