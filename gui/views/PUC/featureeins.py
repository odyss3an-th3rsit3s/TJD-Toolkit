"""Provide Quick Type Challenge game and Feature Eins view implementation.

This module implements a GUI view for the typing speed challenge game, including
game logic, animations, and UI management using the Flet framework.

Example:
    >>> page = ft.Page()
    >>> view = FeatureEinsView(page)
    >>> page.views.append(view)

Attributes:
    __all__ (List[str]): Public interface exports.
    logger (logging.Logger): Module-level logger instance.
"""

from __future__ import annotations

import logging
import random
import time
import threading
from enum import Enum
from typing import Callable, Optional, Sequence

import flet as ft

from gui.utils.font_utils import fontify
from internal.core.exceptions import ToolViewError

__all__ = ["FeatureEinsView"]

logger: logging.Logger = logging.getLogger(__name__)

# Animation constants
ANIMATION_STEPS = 60
ANIMATION_DURATION = 0.3
TITLE_SIZE_START = 40
TITLE_SIZE_TARGET = 25
SUBTITLE_SIZE_START = 25
SUBTITLE_SIZE_TARGET = 15

# Game constants
MAX_INCORRECT_TRIES = 5
WORD_DISPLAY_SIZE = 32
TYPING_FIELD_WIDTH = 350
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 50

# Timing constants
WORD_SETUP_DELAY = 0.6
AUTO_NEXT_DELAY = 1.5
FOCUS_DELAY = 0.1
SUMMARY_DELAY = 2.0

# UI constants
CONTAINER_PADDING = ft.Padding(20, 30, 20, 30)
HEADER_DIVIDER_MARGIN = ft.Margin(0, 5, 0, 15)

# Word list for the typing challenge
WORDS = [
    "python",
    "challenge",
    "construction",
    "random",
    "visitor",
    "type",
    "coming",
    "soon",
    "keyboard",
    "game",
    "future",
    "window",
    "panel",
    "refresh",
    "clean",
    "purge",
    "clear",
    "remove",
    "wipe",
    "trace",
    "record",
    "timeline",
    "entry",
    "log",
    "activity",
    "memory",
    "footprint",
    "cycle",
    "reload",
    "interface",
    "tab",
    "workspace",
    "session",
    "user",
    "input",
    "output",
    "list",
    "manage",
    "organize",
    "control",
    "monitor",
    "overview",
    "details",
    "summary",
    "reset",
    "update",
    "start",
    "stop",
    "pause",
    "resume",
    "launch",
    "terminate",
    "close",
    "open",
    "switch",
    "toggle",
    "access",
    "entrypoint",
    "navigation",
    "route",
    "address",
    "location",
    "field",
    "search",
    "filter",
    "sort",
    "arrange",
    "queue",
    "stack",
    "recent",
    "previous",
    "next",
    "forward",
    "back",
    "gecko",
    "undo",
    "redo",
    "action",
    "operation",
    "event",
    "process",
    "routine",
    "task",
    "job",
    "schedule",
    "plan",
    "execute",
    "run",
    "flow",
    "track",
    "scan",
    "analyze",
    "blink",
    "inspect",
    "review",
    "audit",
    "status",
    "state",
    "mode",
    "option",
    "setting",
    "preference",
    "tool",
    "utility",
    "assist",
    "guide",
    "help",
    "support",
    "info",
    "data",
    "recording",
    "logbook",
    "archive",
    "snapshot",
    "instance",
    "profile",
    "identity",
    "avatar",
    "guest",
    "member",
    "participant",
    "actor",
    "role",
    "permission",
    "homepage",
]


class GameState(Enum):
    """Enumeration for game states."""

    IDLE = "idle"
    STARTED = "started"
    ENDED = "ended"


class AnimationManager:
    """Utility class for managing consistent animations."""

    @staticmethod
    def ease_out(progress: float) -> float:
        """Apply ease-out curve to progress value."""
        return 1 - (1 - progress) * (1 - progress)

    @staticmethod
    def ease_in_out(progress: float) -> float:
        """Apply ease-in-out curve to progress value."""
        if progress < 0.5:
            return 2 * progress * progress
        return 1 - 2 * (1 - progress) * (1 - progress)

    @staticmethod
    def animate_opacity(
        controls: Sequence[ft.Control],
        target_opacity: float,
        duration: float = ANIMATION_DURATION,
        steps: int = ANIMATION_STEPS,
        page: Optional[ft.Page] = None,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Animate opacity of controls with error handling."""

        def animate() -> None:
            try:
                step_duration = duration / steps

                for i in range(steps + 1):
                    if not page:
                        break

                    progress = i / steps
                    eased_progress = AnimationManager.ease_out(progress)
                    current_opacity = eased_progress * target_opacity

                    for control in controls:
                        if control:
                            control.opacity = current_opacity

                    if page:
                        page.update()

                    if i < steps:
                        time.sleep(step_duration)

                if callback:
                    callback()

            except Exception as e:
                logger.error(f"Animation error: {e}")
                raise ToolViewError(
                    "Failed to animate opacity", component="animation_manager", cause=e
                )

        threading.Thread(target=animate, daemon=True).start()


class QuickTypeChallenge:
    """Quick Type Challenge game component with optimized animations and error handling."""

    def __init__(self) -> None:
        """Initialize the QuickTypeChallenge game component."""
        # Game state
        self.word: str = ""
        self.start_time: float | None = None
        self.best_speed: float | None = None
        self.game_state: GameState = GameState.IDLE
        self.correct_answers: int = 0
        self.speeds: list[float] = []
        self.incorrect_tries: int = 0

        # UI state
        self.page: ft.Page | None = None
        self.is_animating: bool = False
        self.active_animations: list[threading.Thread] = []

        self._init_controls()

    def _init_controls(self) -> None:
        """Initialize all UI controls with consistent styling."""
        try:
            self._create_text_elements()
            self._create_game_controls()
            self._create_display_elements()

        except Exception as e:
            logger.error(f"Failed to initialize controls: {e}")
            raise ToolViewError(
                "Failed to initialize game controls", component="control_initialization", cause=e
            )

    def _create_text_elements(self) -> None:
        """Create title and subtitle text elements."""
        self.title_text = fontify(
            "Quick Type Challenge", size=TITLE_SIZE_START, bold=True, color=ft.Colors.BLUE_900
        )
        self.subtitle_text = fontify(
            "Type the given word as fast as you can!",
            size=SUBTITLE_SIZE_START,
            color=ft.Colors.GREY_700,
        )

        self.text_container = ft.Container(padding=ft.Padding(0, 0, 0, 0))

    def _create_game_controls(self) -> None:
        """Create game input and control elements."""
        self.entry = ft.TextField(
            label="Type the word and press Enter",
            autofocus=False,
            on_submit=self.on_submit,
            on_click=self._activate_game,
            on_focus=self._activate_game,
            width=TYPING_FIELD_WIDTH,
            visible=False,
            opacity=0.0,
        )

        self.start_button = ft.ElevatedButton(
            "🎮 Start Game",
            on_click=self.start_game,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE,
                padding=ft.Padding(20, 15, 20, 15),
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=15),
            ),
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
        )

    def _create_display_elements(self) -> None:
        """Create display elements for game feedback."""
        self.word_display = fontify(
            "",
            size=WORD_DISPLAY_SIZE,
            bold=True,
            color=ft.Colors.BLUE_700,
            visible=False,
            opacity=0.0,
        )

        self.status = fontify(
            "",
            size=16,
            visible=False,
            opacity=0.0,
        )

        self.best_speed_display = fontify("", size=14, italic=True, color=ft.Colors.GREEN)

        self.incorrect_tries_display = ft.Row([], alignment=ft.MainAxisAlignment.CENTER)

    def _update_page(self) -> None:
        """Safely update the page with error handling."""
        try:
            if self.page:
                self.page.update()
        except Exception as e:
            logger.error(f"Failed to update page: {e}")
            raise ToolViewError("Failed to update page display", component="page_update", cause=e)

    def _navigate_home(self) -> None:
        """Navigate to home page with error handling."""
        try:
            if self.page:
                self.page.go("/")
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            raise ToolViewError("Failed to navigate to home page", component="navigation", cause=e)

    def _animate_text_sizes(self) -> None:
        """Animate text size changes with improved error handling."""

        def animate() -> None:
            try:
                if self.is_animating:
                    return

                self.is_animating = True
                step_duration = ANIMATION_DURATION / ANIMATION_STEPS

                for i in range(ANIMATION_STEPS + 1):
                    if not self.page:
                        break

                    progress = i / ANIMATION_STEPS
                    eased_progress = AnimationManager.ease_in_out(progress)

                    # Calculate interpolated sizes
                    title_size = (
                        TITLE_SIZE_START + (TITLE_SIZE_TARGET - TITLE_SIZE_START) * eased_progress
                    )
                    subtitle_size = (
                        SUBTITLE_SIZE_START
                        + (SUBTITLE_SIZE_TARGET - SUBTITLE_SIZE_START) * eased_progress
                    )

                    # Update UI elements
                    self.title_text.size = round(title_size, 1)
                    self.subtitle_text.size = round(subtitle_size, 1)
                    self.text_container.padding = ft.Padding(0, 0, 0, 15 * eased_progress)

                    self._update_page()

                    if i < ANIMATION_STEPS:
                        time.sleep(step_duration)

                self.is_animating = False

            except Exception as e:
                self.is_animating = False
                logger.error(f"Text animation error: {e}")
                raise ToolViewError(
                    "Failed to animate text sizes", component="text_animation", cause=e
                )

        thread = threading.Thread(target=animate, daemon=True)
        self.active_animations.append(thread)
        thread.start()

    def _show_game_elements(self) -> None:
        """Show and animate game elements."""
        try:
            self.start_button.visible = False
            self.word_display.visible = True
            self.entry.visible = True
            self.status.visible = True

            self._update_incorrect_tries_display()
            self._update_page()

            # Animate fade-in
            AnimationManager.animate_opacity(
                [self.entry, self.word_display, self.status],
                target_opacity=1.0,
                page=self.page,
                callback=self._setup_first_word,
            )

        except Exception as e:
            logger.error(f"Failed to show game elements: {e}")
            raise ToolViewError(
                "Failed to display game elements", component="game_elements", cause=e
            )

    def _setup_first_word(self) -> None:
        """Setup the first word after animations complete."""

        def delayed_setup() -> None:
            try:
                time.sleep(WORD_SETUP_DELAY)
                if self.page:
                    self.word = random.choice(WORDS)
                    self.word_display.value = self.word
                    self._update_page()
            except Exception as e:
                logger.error(f"Failed to setup first word: {e}")
                raise ToolViewError(
                    "Failed to setup first word", component="first_word_setup", cause=e
                )

        threading.Thread(target=delayed_setup, daemon=True).start()

    def _update_incorrect_tries_display(self) -> None:
        """Update visual display of incorrect attempts."""
        try:
            self.incorrect_tries_display.controls.clear()

            if self.incorrect_tries == 0:
                return

            # Color progression from light to dark red
            colors = [
                ft.Colors.RED_100,
                ft.Colors.RED_300,
                ft.Colors.RED_500,
                ft.Colors.RED_700,
                ft.Colors.RED_900,
            ]

            for i in range(self.incorrect_tries):
                color = colors[min(i, len(colors) - 1)]
                cross = ft.Icon(ft.Icons.CANCEL, size=20, color=color)
                self.incorrect_tries_display.controls.append(cross)

        except Exception as e:
            logger.error(f"Failed to update incorrect tries display: {e}")
            raise ToolViewError(
                "Failed to update incorrect tries display", component="tries_display", cause=e
            )

    def _calculate_typing_speed(self) -> float:
        """Calculate typing speed in characters per second."""
        if self.start_time is None:
            return 0.0

        elapsed = time.time() - self.start_time
        char_count = len(self.word)
        return round(char_count / elapsed, 2) if elapsed > 0 else 0.0

    def _update_best_speed(self, speed: float) -> None:
        """Update best speed tracking and display."""
        try:
            if self.best_speed is None or speed > self.best_speed:
                self.best_speed = speed
                self.best_speed_display.value = f"🏅 Best: {self.best_speed} char/s"
            else:
                self.best_speed_display.value = f"🏆 Best: {self.best_speed} char/s"
        except Exception as e:
            logger.error(f"Failed to update best speed: {e}")
            raise ToolViewError("Failed to update best speed", component="best_speed", cause=e)

    def _focus_input_field(self) -> None:
        """Focus the input field with delay."""

        def focus_field() -> None:
            try:
                time.sleep(FOCUS_DELAY)
                if self.page and self.entry and not self.entry.disabled:
                    self.entry.focus()
            except Exception as e:
                logger.error(f"Failed to focus input field: {e}")
                raise ToolViewError("Failed to focus input field", component="focus_input", cause=e)

        threading.Thread(target=focus_field, daemon=True).start()

    def build(self) -> ft.Column:
        """Build and return the user interface layout."""
        try:
            return ft.Column(
                [
                    self.title_text,
                    self.subtitle_text,
                    self.text_container,
                    ft.Container(height=15),
                    self.start_button,
                    self.word_display,
                    self.entry,
                    ft.Container(height=5),
                    self.status,
                    self.best_speed_display,
                    ft.Container(height=10),
                    self.incorrect_tries_display,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            )
        except Exception as e:
            logger.error(f"Failed to build UI layout: {e}")
            raise ToolViewError("Failed to build game interface", component="ui_build", cause=e)

    def set_page(self, page: ft.Page) -> None:
        """Set the page reference for UI updates."""
        self.page = page

    def start_game(self, e: ft.ControlEvent | None = None) -> None:
        """Initialize and start the game."""
        try:
            # Reset game state
            self._reset_game_state()

            # Start animations and show elements
            self._animate_text_sizes()
            self._show_game_elements()

        except Exception as start_error:
            logger.error(f"Failed to start game: {start_error}")
            raise ToolViewError(
                "Failed to start typing game", component="game_start", cause=start_error
            )

    def _reset_game_state(self) -> None:
        """Reset all game state variables."""
        self.game_state = GameState.IDLE
        self.correct_answers = 0
        self.speeds = []
        self.incorrect_tries = 0
        self.start_time = None

    def _activate_game(self, e: ft.ControlEvent) -> None:
        """Activate game timing when user interacts with input field."""
        try:
            if self.game_state == GameState.IDLE and self.word:
                self.game_state = GameState.STARTED
                self.entry.label = "Type the word and press Enter"
                self.status.value = "Ready! Start typing..."
                self.status.color = ft.Colors.GREY_600
                self.start_time = float(time.time())
                self._update_page()
        except Exception as activate_error:
            logger.error(f"Failed to activate game: {activate_error}")
            raise ToolViewError(
                "Failed to activate game", component="activate_game", cause=activate_error
            )

    def _prepare_next_word(self) -> None:
        """Prepare the next word and reset input field."""
        try:
            self.word = random.choice(WORDS)
            self.word_display.value = self.word
            self.entry.value = ""
            self.entry.error_text = None
            self.status.value = "KEEP GOING! Continue typing..."
            self.status.color = ft.Colors.GREY_600
            self.entry.disabled = False
            self.start_time = float(time.time())

            self._update_page()
            self._focus_input_field()

        except Exception as prepare_error:
            logger.error(f"Failed to prepare next word: {prepare_error}")
            raise ToolViewError(
                "Failed to prepare next word", component="next_word", cause=prepare_error
            )

    def _auto_advance_word(self) -> None:
        """Automatically advance to next word after delay."""

        def delayed_advance() -> None:
            try:
                time.sleep(AUTO_NEXT_DELAY)
                if self.game_state == GameState.STARTED and self.page:
                    self._prepare_next_word()
            except Exception as advance_error:
                logger.error(f"Failed to auto-advance word: {advance_error}")
                raise ToolViewError(
                    "Failed to auto-advance to next word",
                    component="next_word",
                    cause=advance_error,
                )

        threading.Thread(target=delayed_advance, daemon=True).start()

    def _create_game_summary(self) -> ft.Column:
        """Create game over summary content."""
        try:
            avg_speed = round(sum(self.speeds) / len(self.speeds), 2) if self.speeds else 0

            # Color-code average speed
            speed_color = None
            if avg_speed > 3.5:
                speed_color = ft.Colors.GREEN_700
            elif avg_speed < 3:
                speed_color = ft.Colors.DEEP_ORANGE_700

            # Build statistics display
            avg_speed_row = ft.Row(
                [
                    fontify("📈 Average speed:    ", size=18),
                    fontify(
                        f"{avg_speed} char/s",
                        size=18,
                        color=speed_color,
                        tooltip="Average typing speed typically ranges from 3.0 to 3.5 char/s",
                    ),
                ]
            )

            return ft.Column(
                [
                    fontify("🎮 Game Over!", size=32, bold=True, color=ft.Colors.RED_700),
                    ft.Container(height=40),
                    fontify("📊 Final Statistics", size=20, bold=True, color=ft.Colors.BLUE_700),
                    ft.Container(height=25),
                    ft.Container(
                        ft.Column(
                            [
                                fontify(f"✅ Correct answers:   {self.correct_answers}", size=18),
                                avg_speed_row,
                                fontify(
                                    f"🏆 Best speed:             {self.best_speed or 0} char/s",
                                    size=18,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                        ),
                        alignment=ft.alignment.center,
                        width=300,
                    ),
                    ft.Container(height=80),
                    ft.ElevatedButton(
                        "Go Home",
                        icon=ft.Icons.HOME,
                        on_click=lambda _: self._navigate_home(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        except Exception as summary_error:
            logger.error(f"Failed to create game summary: {summary_error}")
            raise ToolViewError(
                "Failed to create game summary", component="summary_creation", cause=summary_error
            )

    def _display_game_summary(self) -> None:
        """Display the game over summary screen."""

        def show_summary() -> None:
            try:
                time.sleep(SUMMARY_DELAY)
                if not self.page:
                    return

                # Create Tool header
                tool_header = ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK, on_click=lambda _: self._navigate_home()
                        ),
                        fontify("[Feature Eins] Tool", size=25, bold=True),
                    ]
                )

                game_summary = self._create_game_summary()

                # Replace page content
                self.page.views.clear()
                self.page.views.append(
                    ft.View(
                        route="/featureeins",
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    [
                                        tool_header,
                                        ft.Container(
                                            content=ft.Divider(thickness=1, height=1),
                                            margin=HEADER_DIVIDER_MARGIN,
                                        ),
                                        ft.Container(
                                            content=game_summary,
                                            expand=True,
                                            alignment=ft.alignment.center,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=15,
                                ),
                                expand=True,
                                padding=CONTAINER_PADDING,
                                alignment=ft.alignment.center,
                            )
                        ],
                    )
                )
                self._update_page()

            except Exception as display_error:
                logger.error(f"Failed to display game summary: {display_error}")
                raise ToolViewError(
                    "Failed to display game over screen",
                    component="summary_display",
                    cause=display_error,
                )

        threading.Thread(target=show_summary, daemon=True).start()

    def on_submit(self, e: ft.ControlEvent) -> None:
        """Handle form submission when user presses Enter."""
        try:
            # Activate game if not started
            if self.game_state == GameState.IDLE:
                self._activate_game(e)
                return

            if self.start_time is None:
                return

            typed = str(self.entry.value or "").strip()

            if typed == self.word:
                self._handle_correct_answer()
            else:
                self._handle_incorrect_answer()

        except Exception as submit_error:
            logger.error(f"Error handling form submission: {submit_error}")
            raise ToolViewError(
                "Failed to process user input", component="form_submission", cause=submit_error
            )

    def _handle_correct_answer(self) -> None:
        """Process correct answer and update game state."""
        try:
            char_per_sec = self._calculate_typing_speed()

            self.status.value = f"✔️ Correct! Speed: {char_per_sec} char/s"
            self.status.color = ft.Colors.GREEN

            self._update_best_speed(char_per_sec)

            self.entry.disabled = True
            self.correct_answers += 1
            self.speeds.append(char_per_sec)

            self._update_page()
            self._auto_advance_word()

        except Exception as correct_error:
            logger.error(f"Error handling correct answer: {correct_error}")
            self.status.value = "Error calculating speed"
            self.status.color = ft.Colors.RED
            self._update_page()

    def _handle_incorrect_answer(self) -> None:
        """Process incorrect answer and update game state."""
        try:
            self.incorrect_tries += 1
            self._update_incorrect_tries_display()

            if self.incorrect_tries >= MAX_INCORRECT_TRIES:
                self._end_game()
            else:
                self._handle_retry()

        except Exception as incorrect_error:
            logger.error(f"Error handling incorrect answer: {incorrect_error}")
            raise ToolViewError(
                "Failed to handle wrong answer", component="incorrect_answer", cause=incorrect_error
            )

    def _end_game(self) -> None:
        """End the game and show summary."""
        self.game_state = GameState.ENDED
        self.entry.disabled = True
        self.status.value = "💀 Too many mistakes! Game ending..."
        self.status.color = ft.Colors.RED_700
        self.entry.error_text = None
        self._update_page()
        self._display_game_summary()

    def _handle_retry(self) -> None:
        """Handle retry after incorrect answer."""
        self.status.value = "❌ Oops..."
        self.status.color = ft.Colors.RED
        self.entry.error_text = "Incorrect! Try again."
        self.entry.value = ""
        self._update_page()
        self._focus_input_field()


class FeatureEinsView(ft.View):
    """Feature Eins View implementation for the typing game page."""

    def __init__(self, page: ft.Page) -> None:
        """Initialize the FeatureEinsView with error handling."""
        try:
            # Create and configure game instance
            self.game = QuickTypeChallenge()
            self.game.set_page(page)

            super().__init__(
                route="/featureeins",
                controls=[
                    ft.Container(
                        content=ft.Column(
                            [
                                self._create_tool_header(page),
                                ft.Container(
                                    content=ft.Divider(thickness=1, height=1),
                                    margin=HEADER_DIVIDER_MARGIN,
                                ),
                                fontify(
                                    "🚧  !=-->  Page Under Construction  <--=!  🚧",
                                    size=24,
                                    bold=True,
                                    color="#d2691e",
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            self.game.build(),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    expand=True,
                                    alignment=ft.alignment.center,
                                ),
                                ft.ElevatedButton(
                                    "Go Home",
                                    icon=ft.Icons.HOME,
                                    on_click=lambda _: page.go("/"),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                        ),
                        expand=True,
                        padding=CONTAINER_PADDING,
                        alignment=ft.alignment.center,
                    )
                ],
            )
        except ToolViewError:
            raise
        except Exception as init_error:
            logger.error(f"Failed to initialize FeatureEinsView: {init_error}")
            raise ToolViewError(
                "Failed to initialize Feature Eins view",
                component="view_initialization",
                cause=init_error,
            )

    def _create_tool_header(self, page: ft.Page) -> ft.Row:
        """Create the reusable Tool header with error handling."""
        try:
            return ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/")),
                    fontify("[Feature Eins] Tool", size=25, bold=True),
                ]
            )
        except Exception as header_error:  # Changed from 'error' to be more specific
            logger.error(f"Failed to create tool header: {header_error}")
            raise ToolViewError(
                "Failed to create tool header", component="header_creation", cause=header_error
            )
