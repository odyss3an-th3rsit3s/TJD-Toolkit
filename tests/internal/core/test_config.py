"""Test suite for the config module in the TJD-Toolkit.

This module contains comprehensive test coverage for the
Config class functionality including configuration loading, saving,
getting, setting, and error handling scenarios.

The test suite covers:
- Configuration initialization and path setup
- Loading and saving configuration files
- Getting and setting configuration values with dot notation
- Configuration validation and error handling
- Integration testing and edge cases

Example:
    Run the test suite with pytest:
        $ pytest test_config.py -v
"""

import json
from unittest.mock import patch

import pytest

from internal.core.config import Config
from internal.core.exceptions import (
    ConfigurationError,
    FileOperationError,
    JSONParsingError,
    ValidationError,
)


class TestConfig:
    """Test suite for Config class functionality.

    This class contains all test methods for validating the Config class
    behavior including initialization, file operations, data access,
    and error handling scenarios.

    The test class uses pytest fixtures to provide consistent test
    environments and sample data for testing various configuration
    scenarios.

    Attributes:
        All test methods use pytest fixtures for setup and teardown.
    """

    @pytest.fixture
    def temp_config_dir(self, tmp_path):
        """Create a temporary directory for config testing.

        Args:
            tmp_path: Pytest temporary path fixture.

        Returns:
            Path: Temporary directory path for configuration testing.
        """
        return tmp_path / "test_config"

    @pytest.fixture
    def mock_config(self, temp_config_dir):
        """Create a Config instance with mocked app data directory.

        Args:
            temp_config_dir: Temporary directory fixture.

        Returns:
            Config: Configured Config instance for testing.
        """
        with patch("internal.core.config.get_app_data_dir", return_value=temp_config_dir):
            return Config()

    @pytest.fixture
    def sample_config_data(self):
        """Sample configuration data for testing.

        Returns:
            dict: Sample configuration dictionary with test data.
        """
        return {
            "theme": "dark",
            "window": {"width": 1200, "height": 800},
            "database": {"host": "localhost", "port": 5432},
            "features": {"enabled": True, "beta": False},
        }

    # Initialization Tests

    def test_init_creates_config_instance(self, mock_config):
        """Test that Config initializes properly.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        assert isinstance(mock_config, Config)
        assert hasattr(mock_config, "_config")
        assert isinstance(mock_config._config, dict)

    def test_init_sets_correct_paths(self, temp_config_dir):
        """Test that initialization sets correct file paths.

        Args:
            temp_config_dir: Temporary directory fixture.
        """
        with patch("internal.core.config.get_app_data_dir", return_value=temp_config_dir):
            config = Config()
            assert config.config_dir == temp_config_dir
            assert config.config_file == temp_config_dir / "config.json"

    # Load Method Tests

    def test_load_existing_valid_config(self, mock_config, sample_config_data):
        """Test loading valid existing configuration file.

        Args:
            mock_config: Mocked Config instance fixture.
            sample_config_data: Sample configuration data fixture.
        """
        mock_config.config_dir.mkdir(parents=True, exist_ok=True)
        with open(mock_config.config_file, "w") as f:
            json.dump(sample_config_data, f)

        mock_config.load()
        assert mock_config._config["theme"] == "dark"
        assert mock_config._config["window"]["width"] == 1200

    def test_load_nonexistent_config_creates_defaults(self, mock_config):
        """Test that loading creates default config when file doesn't exist.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config.load()
        defaults = mock_config._get_defaults()
        assert mock_config._config == defaults

    def test_load_invalid_json_raises_exception(self, mock_config):
        """Test that invalid JSON raises JSONParsingError.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config.config_dir.mkdir(parents=True, exist_ok=True)
        with open(mock_config.config_file, "w") as f:
            f.write("{ invalid json }")

        with pytest.raises(JSONParsingError):
            mock_config.load()

    def test_load_file_permission_error(self, mock_config):
        """Test file permission errors during load.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(FileOperationError):
                    mock_config.load()

    def test_load_unexpected_error_raises_configuration_error(self, mock_config):
        """Test that unexpected errors during load raise ConfigurationError.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        with patch("builtins.open", side_effect=RuntimeError("Unexpected error")):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(ConfigurationError):
                    mock_config.load()

    # Save Method Tests

    def test_save_creates_directory_and_file(self, mock_config, sample_config_data):
        """Test that save creates directory and writes file.

        Args:
            mock_config: Mocked Config instance fixture.
            sample_config_data: Sample configuration data fixture.
        """
        mock_config._config = sample_config_data
        mock_config.save()

        assert mock_config.config_dir.exists()
        assert mock_config.config_file.exists()

        with open(mock_config.config_file, "r") as f:
            saved_data = json.load(f)
        assert saved_data == sample_config_data

    def test_save_file_permission_error(self, mock_config):
        """Test file permission errors during save.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            with pytest.raises(FileOperationError):
                mock_config.save()

    def test_save_non_serializable_data_raises_exception(self, mock_config):
        """Test that non-JSON-serializable data raises JSONParsingError.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"function": lambda x: x}
        with pytest.raises(JSONParsingError):
            mock_config.save()

    # Get Method Tests

    def test_get_existing_simple_key(self, mock_config):
        """Test getting an existing simple key.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"theme": "dark"}
        assert mock_config.get("theme") == "dark"

    def test_get_existing_nested_key(self, mock_config):
        """Test getting an existing nested key with dot notation.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"window": {"width": 1200}}
        assert mock_config.get("window.width") == 1200

    def test_get_nonexistent_key_returns_default(self, mock_config):
        """Test that nonexistent key returns default value.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {}
        assert mock_config.get("nonexistent") is None
        assert mock_config.get("nonexistent", "default") == "default"

    def test_get_deeply_nested_key(self, mock_config):
        """Test getting deeply nested keys.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"a": {"b": {"c": {"d": "value"}}}}
        assert mock_config.get("a.b.c.d") == "value"

    def test_get_invalid_key_type_raises_validation_error(self, mock_config):
        """Test that invalid key type raises ValidationError.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        with pytest.raises(ValidationError):
            mock_config.get(123)

    def test_get_empty_key_raises_validation_error(self, mock_config):
        """Test that empty key raises ValidationError.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        with pytest.raises(ValidationError):
            mock_config.get("")

    def test_get_path_through_non_dict_returns_default(self, mock_config):
        """Test that accessing through non-dict values returns default.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"value": "string"}
        assert mock_config.get("value.nested", "default") == "default"

    # Set Method Tests

    def test_set_simple_key(self, mock_config):
        """Test setting a simple key-value pair.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config.set("theme", "light")
        assert mock_config._config["theme"] == "light"

    def test_set_nested_key_creates_structure(self, mock_config):
        """Test that setting nested key creates intermediate dictionaries.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config.set("window.width", 1400)
        assert mock_config._config["window"]["width"] == 1400

    def test_set_deeply_nested_key(self, mock_config):
        """Test setting deeply nested keys.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config.set("a.b.c.d", "deep_value")
        assert mock_config._config["a"]["b"]["c"]["d"] == "deep_value"

    def test_set_overwrites_existing_value(self, mock_config):
        """Test that setting overwrites existing values.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"theme": "dark"}
        mock_config.set("theme", "light")
        assert mock_config._config["theme"] == "light"

    def test_set_invalid_key_type_raises_validation_error(self, mock_config):
        """Test that invalid key type raises ValidationError.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        with pytest.raises(ValidationError):
            mock_config.set(123, "value")

    def test_set_empty_key_raises_validation_error(self, mock_config):
        """Test that empty key raises ValidationError.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        with pytest.raises(ValidationError):
            mock_config.set("", "value")

    def test_set_path_through_non_dict_raises_validation_error(self, mock_config):
        """Test that setting through non-dict path raises ValidationError.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"value": "string"}
        with pytest.raises(ValidationError):
            mock_config.set("value.nested", "new_value")

    # Has Method Tests

    def test_has_existing_simple_key(self, mock_config):
        """Test checking for existing simple key.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"theme": "dark"}
        assert mock_config.has("theme") is True

    def test_has_existing_nested_key(self, mock_config):
        """Test checking for existing nested key.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"window": {"width": 1200}}
        assert mock_config.has("window.width") is True

    def test_has_nonexistent_key(self, mock_config):
        """Test checking for nonexistent key.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {}
        assert mock_config.has("nonexistent") is False

    def test_has_partial_path_exists(self, mock_config):
        """Test checking when partial path exists but not full path.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"window": {"width": 1200}}
        assert mock_config.has("window.height") is False

    # Delete Method Tests

    def test_delete_existing_simple_key(self, mock_config):
        """Test deleting existing simple key.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"theme": "dark", "other": "value"}
        result = mock_config.delete("theme")
        assert result is True
        assert "theme" not in mock_config._config
        assert "other" in mock_config._config

    def test_delete_existing_nested_key(self, mock_config):
        """Test deleting existing nested key.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"window": {"width": 1200, "height": 800}}
        result = mock_config.delete("window.width")
        assert result is True
        assert "width" not in mock_config._config["window"]
        assert "height" in mock_config._config["window"]

    def test_delete_nonexistent_key(self, mock_config):
        """Test deleting nonexistent key returns False.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {}
        result = mock_config.delete("nonexistent")
        assert result is False

    def test_delete_partial_path_nonexistent(self, mock_config):
        """Test deleting when partial path doesn't exist.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"other": "value"}
        result = mock_config.delete("window.width")
        assert result is False

    # Section Methods Tests

    def test_get_section_existing(self, mock_config):
        """Test getting existing configuration section.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"window": {"width": 1200, "height": 800}}
        section = mock_config.get_section("window")
        assert section == {"width": 1200, "height": 800}

    def test_get_section_nonexistent(self, mock_config):
        """Test getting nonexistent section returns empty dict.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {}
        section = mock_config.get_section("window")
        assert section == {}

    def test_update_section_existing(self, mock_config):
        """Test updating existing section.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"window": {"width": 1200}}
        mock_config.update_section("window", {"height": 800, "maximized": True})

        expected = {"width": 1200, "height": 800, "maximized": True}
        assert mock_config._config["window"] == expected

    def test_update_section_new(self, mock_config):
        """Test updating new section creates it.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {}
        mock_config.update_section("database", {"host": "localhost", "port": 5432})

        assert mock_config._config["database"] == {"host": "localhost", "port": 5432}

    # Reset and Default Methods Tests

    def test_reset_to_defaults(self, mock_config):
        """Test resetting configuration to defaults.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"custom": "value"}
        mock_config.reset_to_defaults()

        defaults = mock_config._get_defaults()
        assert mock_config._config == defaults

    def test_get_defaults_structure(self, mock_config):
        """Test default configuration structure.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        defaults = mock_config._get_defaults()

        assert "theme" in defaults
        assert "window" in defaults
        assert "auto_check_updates" in defaults
        assert "tools" in defaults
        assert "ui" in defaults
        assert "logging" in defaults

        assert isinstance(defaults["window"], dict)
        assert "width" in defaults["window"]
        assert "height" in defaults["window"]

    # Internal Method Tests

    def test_merge_dicts_simple(self, mock_config):
        """Test simple dictionary merging.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        default = {"a": 1, "b": 2}
        current = {"b": 3, "c": 4}
        result = mock_config._merge_dicts(default, current)

        expected = {"a": 1, "b": 3, "c": 4}
        assert result == expected

    def test_merge_dicts_nested(self, mock_config):
        """Test nested dictionary merging.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        default = {"section": {"a": 1, "b": 2}}
        current = {"section": {"b": 3, "c": 4}}
        result = mock_config._merge_dicts(default, current)

        expected = {"section": {"a": 1, "b": 3, "c": 4}}
        assert result == expected

    def test_merge_dicts_scalar_override(self, mock_config):
        """Test that scalar values override nested dicts.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        default = {"section": {"nested": "value"}}
        current = {"section": "scalar"}
        result = mock_config._merge_dicts(default, current)

        expected = {"section": "scalar"}
        assert result == expected

    def test_merge_defaults_integration(self, mock_config):
        """Test merge defaults integration.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config._config = {"theme": "custom", "new_key": "value"}
        mock_config._merge_defaults()

        assert mock_config._config["theme"] == "custom"
        assert mock_config._config["new_key"] == "value"
        assert "window" in mock_config._config

    # Integration Tests

    def test_full_workflow_integration(self, mock_config):
        """Test complete workflow: set, save, load, get.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config.set("app.name", "TestApp")
        mock_config.set("app.version", "1.0.0")
        mock_config.set("database.host", "localhost")

        mock_config.save()

        new_config = Config.__new__(Config)
        new_config.config_dir = mock_config.config_dir
        new_config.config_file = mock_config.config_file
        new_config._config = {}
        new_config.load()

        assert new_config.get("app.name") == "TestApp"
        assert new_config.get("app.version") == "1.0.0"
        assert new_config.get("database.host") == "localhost"

    # Edge Cases and Error Handling

    def test_config_file_corrupted_during_operation(self, mock_config):
        """Test handling of file corruption during operations.

        Expects ConfigurationError wrapping the original JSONDecodeError
        when attempting to load corrupted configuration file.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        with patch("builtins.open", side_effect=json.JSONDecodeError("msg", "doc", 0)):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(ConfigurationError) as exc_info:
                    mock_config.load()
                assert isinstance(exc_info.value.cause, json.JSONDecodeError)
                assert "Failed to load configuration" in str(exc_info.value)

    def test_concurrent_access_simulation(self, mock_config):
        """Test behavior under simulated concurrent access.

        Args:
            mock_config: Mocked Config instance fixture.
        """
        mock_config.set("counter", 0)

        for i in range(10):
            current = mock_config.get("counter", 0)
            mock_config.set("counter", current + 1)

        assert mock_config.get("counter") == 10

    @pytest.mark.parametrize("invalid_key", [None, 123, [], {}, object()])
    def test_invalid_key_types(self, mock_config, invalid_key):
        """Test various invalid key types raise ValidationError.

        Args:
            mock_config: Mocked Config instance fixture.
            invalid_key: Invalid key type to test.
        """
        with pytest.raises(ValidationError):
            mock_config.get(invalid_key)

        with pytest.raises(ValidationError):
            mock_config.set(invalid_key, "value")

    @pytest.mark.parametrize(
        "test_value", ["string", 123, 123.45, True, False, None, [1, 2, 3], {"nested": "dict"}]
    )
    def test_various_value_types(self, mock_config, test_value):
        """Test setting and getting various value types.

        Args:
            mock_config: Mocked Config instance fixture.
            test_value: Value type to test.
        """
        mock_config.set("test_key", test_value)
        assert mock_config.get("test_key") == test_value
