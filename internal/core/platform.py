"""Provide platform-specific system utilities for TJD-Toolkit operations.

This module implements:
- Operating system detection
- Privilege management
- Path resolution
- Administrative command execution

Example:
    >>> from internal.core.platform import get_platform, is_admin
    >>> platform = get_platform()
    >>> print(f"Running on {platform.value} with admin: {is_admin()}")

Attributes:
    __all__ (List[str]): Public interface exports.
    logger (logging.Logger): Module-level logger instance.
"""

from __future__ import annotations

import ctypes
import logging
import os
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import List

from .exceptions import PlatformError

__all__ = ["Platform", "get_platform", "is_admin", "get_app_data_dir", "run_as_admin"]

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Define supported operating system identifiers.

    Enumerate platform types for consistent OS identification and feature
    management across the application.

    Attributes:
        WINDOWS (str): Windows operating system identifier.
        MACOS (str): macOS operating system identifier.
        LINUX (str): Linux operating system identifier.

    Example:
        >>> platform = Platform.WINDOWS
        >>> assert platform.value == "windows"
    """

    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


def get_platform() -> Platform:
    """Determine current operating system platform.

    Returns:
        Platform: Enum value for current operating system.

    Example:
        >>> platform = get_platform()
        >>> assert isinstance(platform, Platform)
    """
    if sys.platform == "win32":
        return Platform.WINDOWS
    elif sys.platform == "darwin":  # macOS
        return Platform.MACOS
    else:  # Linux and other Unix-like
        return Platform.LINUX


def is_admin() -> bool:
    """Check for elevated process privileges.

    Determine if current process has administrative access rights on the
    current platform.

    Returns:
        bool: True if process has admin privileges.

    Raises:
        PlatformError: If privilege check fails.

    Example:
        >>> is_elevated = is_admin()
        >>> assert isinstance(is_elevated, bool)

    Note:
        Windows checks UAC elevation, Unix checks for root (uid 0).
    """
    try:
        if sys.platform == "win32":
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        else:  # Unix-like systems (Linux, macOS)
            if hasattr(os, "geteuid"):  # Unix systems have this
                return os.geteuid() == 0
            return False
    except Exception as e:
        msg = "Error checking admin privileges"
        logger.error(f"{msg}: {e}")
        raise PlatformError(
            msg, platform=get_platform().value, operation="check_privileges", cause=e
        )


def get_app_data_dir() -> Path:
    """Resolve platform-specific application data directory.

    Determine and return the appropriate directory for storing application
    data based on the current operating system's conventions.

    Returns:
        Path: Directory path for application data storage.

    Raises:
        PlatformError: If directory cannot be accessed or created.

    Example:
        >>> data_dir = get_app_data_dir()
        >>> config_file = data_dir / "config.json"

    Note:
        Windows: %LOCALAPPDATA%/TJD-Toolkit
        macOS: ~/Library/Application Support/TJD-Toolkit
        Linux: ~/.config/tjd-toolkit
    """
    platform = get_platform()
    try:
        home = Path.home()
        if platform == Platform.WINDOWS:
            path = home / "AppData" / "Local" / "TJD-Toolkit"
        elif platform == Platform.MACOS:
            path = home / "Library" / "Application Support" / "TJD-Toolkit"
        else:
            path = home / ".config" / "tjd-toolkit"

        # Ensure the directory exists and is accessible
        path.mkdir(parents=True, exist_ok=True)
        return path
    except PermissionError as e:
        msg = f"Permission denied accessing app data directory: {e}"
        logger.error(msg)
        raise PlatformError(msg, platform=platform.value, operation="access_app_data", cause=e)
    except OSError as e:
        msg = f"Failed to resolve or create app data directory: {e}"
        logger.error(msg)
        raise PlatformError(msg, platform=platform.value, operation="access_app_data", cause=e)


def run_as_admin(command: List[str]) -> bool:
    """Execute command with elevated privileges.

    Run specified command using platform-appropriate privilege elevation
    mechanism.

    Args:
        command (List[str]): Command and arguments to execute. First item
            must be executable path.

    Returns:
        bool: True if command succeeds.

    Raises:
        PlatformError: If elevation fails or command errors.

    Example:
        >>> cmd = ["echo", "test"]
        >>> success = run_as_admin(cmd)
        >>> assert isinstance(success, bool)

    Note:
        Windows uses 'runas', Unix-like systems use 'sudo'.
    """
    platform = get_platform()
    try:
        if platform == Platform.WINDOWS:
            subprocess.run(
                ["runas", "/user:Administrator"] + command,
                check=True,
                capture_output=True,
                text=True,
            )
        else:
            subprocess.run(["sudo"] + command, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        msg = f"Failed to run command as admin: {e}"
        logger.error(msg)
        raise PlatformError(msg, platform=platform.value, operation="privilege_elevation", cause=e)
    except FileNotFoundError as e:
        msg = f"Required elevation tool not found: {e}"
        logger.error(msg)
        raise PlatformError(msg, platform=platform.value, operation="privilege_elevation", cause=e)
