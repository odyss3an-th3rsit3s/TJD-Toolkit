"""Manage configuration storage and retrieval for TJD-Toolkit.

This module provides a hierarchical configuration system that supports:
- JSON-based persistent storage
- Dot notation access to nested values
- Type safety and validation
- Default value management

Example:
    >>> from internal.core.config import config
    >>> config.set('app.theme', 'dark')
    >>> theme = config.get('app.theme')
    >>> print(theme)
    'dark'

Attributes:
    __all__ (List[str]): Public interface exports.
    logger (logging.Logger): Module-level logger instance.
    T (TypeVar): Generic type variable for type hints.
    config (Config): Global configuration instance.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, TypeVar, Union

from .exceptions import ConfigurationError, FileOperationError, JSONParsingError, ValidationError
from .platform import get_app_data_dir

__all__ = ["Config", "config"]

logger = logging.getLogger(__name__)

T = TypeVar("T")  # For generic type hints


class Config:
    """Manage hierarchical configuration with JSON persistence.

    Provides an interface for storing and retrieving configuration values using
    dot notation paths. Supports automatic JSON persistence, validation, and
    default value management.

    Attributes:
        config_dir (Path): Directory for configuration storage.
        config_file (Path): JSON file path for configuration data.
        _config (Dict[str, Any]): Internal configuration storage.

    Example:
        >>> config = Config()
        >>> config.set('database.host', 'localhost')
        >>> host = config.get('database.host')
        >>> assert host == 'localhost'
    """

    config_dir: Path
    config_file: Path
    _config: Dict[str, Any]

    def __init__(self) -> None:
        """Initialize configuration manager with default settings."""
        self.config_dir: Path = get_app_data_dir()
        self.config_file: Path = self.config_dir / "config.json"
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from the JSON file.

        Read configuration from disk and merge with defaults. Creates new
        file with defaults if none exists.

        Raises:
            ConfigurationError: If file cannot be read or parsed.
            FileOperationError: If file system operations fail.
            JSONParsingError: If JSON content is invalid.
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    try:
                        self._config = json.load(f)
                    except json.JSONDecodeError as e:
                        logging.error(f"Invalid JSON in config file: {e}")
                        raise JSONParsingError(
                            f"Invalid JSON syntax in configuration file: {e}", cause=e
                        )
                self._merge_defaults()
            else:
                self._config = self._get_defaults()
                self.save()
        except (OSError, IOError) as e:
            logging.error(f"Could not load config file: {e}")
            self._config = self._get_defaults()
            raise FileOperationError(
                "load", f"Cannot read configuration file: {e}", str(self.config_file), cause=e
            )
        except Exception as e:
            if not isinstance(e, (ConfigurationError, FileOperationError, JSONParsingError)):
                logging.error(f"Unexpected error loading config: {e}")
                raise ConfigurationError(f"Failed to load configuration: {e}", cause=e)
            raise

    def save(self) -> None:
        """Persist configuration to the JSON file.

        Create configuration directory if needed and write current state
        to disk in JSON format.

        Raises:
            FileOperationError: If file cannot be written.
            JSONParsingError: If configuration cannot be serialized.
        """
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                try:
                    json.dump(self._config, f, indent=2)
                except (TypeError, ValueError) as e:
                    logging.error(f"Cannot serialize config to JSON: {e}")
                    raise JSONParsingError(f"Cannot serialize configuration to JSON: {e}", cause=e)
        except (OSError, IOError) as e:
            logging.error(f"Could not save config file: {e}")
            raise FileOperationError(
                "save", f"Cannot write configuration file: {e}", str(self.config_file), cause=e
            )

    def get(self, key: str, default: T = None) -> Union[T, Any]:
        """Retrieve a configuration value using dot notation.

        Access nested configuration values using dot-separated key paths.
        Returns default value if key doesn't exist.

        Args:
            key (str): Dot-separated path to configuration value.
            default (T, optional): Value to return if key not found.
                Defaults to None.

        Returns:
            Union[T, Any]: Configuration value or default if not found.

        Raises:
            ValidationError: If key format is invalid.

        Example:
            >>> value = config.get('app.window.width', 800)
            >>> assert isinstance(value, int)
        """
        try:
            if not isinstance(key, str):
                raise ValidationError(
                    "Configuration key must be a string", field="key", value=str(type(key).__name__)
                )

            if not key:
                raise ValidationError(
                    "Configuration key cannot be empty", field="key", value="<empty>"
                )

            current = self._config
            for part in key.split("."):
                if not isinstance(current, dict):
                    return default
                current = current.get(part, default)
                if current is None:
                    return default

            return current

        except Exception as e:
            if not isinstance(e, ValidationError):
                raise ValidationError(
                    f"Error accessing configuration key '{key}': {e}",
                    field="key",
                    value=key,
                    cause=e,
                )
            raise

    def set(self, key: str, value: Any) -> None:
        """Store a configuration value using dot notation.

        Store value at the specified path, creating intermediate dictionaries
        as needed.

        Args:
            key (str): Dot-separated path to store value at.
            value (Any): Value to store (must be JSON-serializable).

        Raises:
            ValidationError: If key is invalid or value cannot be stored.
            JSONParsingError: If value cannot be serialized.
            FileOperationError: If changes cannot be saved.
        """
        try:
            if not isinstance(key, str):
                raise ValidationError(
                    "Configuration key must be a string", field="key", value=str(type(key).__name__)
                )

            if not key:
                raise ValidationError(
                    "Configuration key cannot be empty", field="key", value="<empty>"
                )

            parts = key.split(".")
            current = self._config

            # Navigate to the correct nested level
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    raise ValidationError(
                        f"Cannot set key '{key}': path element '{part}' is not a dictionary",
                        field="key",
                        value=key,
                    )
                current = current[part]

            # Set the value
            current[parts[-1]] = value
            self.save()

        except Exception as e:
            if not isinstance(e, (ValidationError, FileOperationError, JSONParsingError)):
                raise ValidationError(
                    f"Error setting configuration key '{key}': {e}", field="key", value=key, cause=e
                )
            raise

    def has(self, key: str) -> bool:
        """Check if a configuration key exists.

        Args:
            key (str): Configuration key to check.

        Returns:
            bool: True if key exists, False otherwise.
        """
        if "." not in key:
            return key in self._config

        keys = key.split(".")
        current = self._config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return False
        return True

    def delete(self, key: str) -> bool:
        """Remove a configuration key and its value.

        Args:
            key (str): Configuration key to remove.

        Returns:
            bool: True if key was deleted, False if key did not exist.
        """
        if "." not in key:
            if key in self._config:
                del self._config[key]
                return True
            return False

        keys = key.split(".")
        current = self._config

        # Navigate to parent
        for k in keys[:-1]:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return False

        # Delete final key
        if isinstance(current, dict) and keys[-1] in current:
            del current[keys[-1]]
            return True
        return False

    def get_section(self, section: str) -> Dict[str, Any]:
        """Retrieve an entire configuration section.

        Args:
            section (str): Section key (e.g., 'tools.browserrefresher').

        Returns:
            Dict[str, Any]: Dictionary containing section configuration.
        """
        return self.get(section, {})

    def update_section(self, section: str, values: Dict[str, Any]) -> None:
        """Update multiple values in a configuration section.

        Args:
            section (str): Section key to update.
            values (Dict[str, Any]): New values to set in section.

        Raises:
            ValidationError: If section path is invalid.
            JSONParsingError: If values cannot be serialized.
            FileOperationError: If changes cannot be saved.
        """
        current_section = self.get_section(section)
        current_section.update(values)
        self.set(section, current_section)

    def reset_to_defaults(self) -> None:
        """Reset entire configuration to default values.

        Raises:
            FileOperationError: If defaults cannot be saved.
            JSONParsingError: If defaults cannot be serialized.
        """
        self._config = self._get_defaults()
        self.save()

    def _merge_defaults(self) -> None:
        """Merge default values into current configuration.

        Internal method to ensure all default keys exist in config.
        """
        defaults = self._get_defaults()
        self._config = self._merge_dicts(defaults, self._config)

    def _merge_dicts(self, default: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        """Perform deep merge of configuration dictionaries.

        Recursively combine two dictionaries following these rules:
        - Nested dictionaries are merged
        - Scalar values from current override default
        - Dictionary values are always merged, not replaced

        Args:
            default (Dict[str, Any]): Base configuration dictionary.
            current (Dict[str, Any]): Override configuration dictionary.

        Returns:
            Dict[str, Any]: New dictionary with merged configuration.

        Note:
            - Nested dictionaries are merged recursively
            - Scalar values from current override default
            - Dictionary values are always merged, not replaced
        """
        result = default.copy()
        for key, value in current.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result

    def _get_defaults(self) -> Dict[str, Any]:
        """Return default configuration structure.

        Returns:
            Dict[str, Any]: Default configuration dictionary.

        Note:
            This defines the base configuration with default values for
            all supported settings.
        """
        return {
            "theme": "system",
            "window": {"width": 1186, "height": 733},
            "auto_check_updates": True,
            "tools": {"feature_eins": True},
            "ui": {
                "show_tooltips": True,
                "confirm_destructive_actions": True,
                "auto_refresh_browser_list": True,
            },
            "logging": {"level": "INFO", "file_logging": False, "max_log_size": "10MB"},
        }


# Global config instance
config = Config()
