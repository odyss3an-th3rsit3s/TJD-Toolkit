"""Test suite for the platform module in the TJD-Toolkit.

This module provides comprehensive test coverage for platform detection,
administrative privilege checking, app data directory resolution,
and administrative command execution across Windows, macOS, and Linux.

The test suite uses extensive mocking to isolate units under test
and avoid requiring actual system privileges during testing.

Example:
    Run the test suite with pytest:
        $ pytest test_exceptions.py -v
"""

import subprocess
from enum import Enum
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from internal.core.exceptions import PlatformError
from internal.core.platform import (
    Platform,
    get_platform,
    is_admin,
    get_app_data_dir,
    run_as_admin,
)


class TestPlatform:
    """Test the Platform enum functionality.

    Verify that the Platform enum contains the correct values
    and behaves as expected for platform identification.

    Example:
        >>> test = TestPlatform()
        >>> test.test_platform_enum_values()
    """

    def test_platform_enum_values(self):
        """Test that Platform enum has correct string values.

        Verify that each platform enum member maps to the expected
        string value used for platform identification.

        Raises:
            AssertionError: If enum values don't match expected strings.
        """
        assert Platform.WINDOWS.value == "windows"
        assert Platform.MACOS.value == "macos"
        assert Platform.LINUX.value == "linux"

    def test_platform_enum_is_enum(self):
        """Test that Platform is a proper Enum with correct length.

        Verify that Platform inherits from Enum and contains exactly
        three platform definitions.

        Raises:
            AssertionError: If Platform is not an Enum or wrong length.
        """
        assert issubclass(Platform, Enum)
        assert len(Platform) == 3


class TestGetPlatform:
    """Test the get_platform function for all supported platforms.

    Verify platform detection works correctly across Windows, macOS,
    and Unix-like systems by mocking sys.platform values.

    Example:
        >>> test = TestGetPlatform()
        >>> test.test_get_platform_windows()
    """

    @patch("sys.platform", "win32")
    def test_get_platform_windows(self):
        """Test get_platform detects Windows correctly.

        Mock sys.platform as 'win32' and verify the function
        returns Platform.WINDOWS.

        Raises:
            AssertionError: If Platform.WINDOWS is not returned.
        """
        result = get_platform()
        assert result == Platform.WINDOWS

    @patch("sys.platform", "darwin")
    def test_get_platform_macos(self):
        """Test get_platform detects macOS correctly.

        Mock sys.platform as 'darwin' and verify the function
        returns Platform.MACOS.

        Raises:
            AssertionError: If Platform.MACOS is not returned.
        """
        result = get_platform()
        assert result == Platform.MACOS

    @pytest.mark.parametrize("platform_name", ["linux", "linux2", "freebsd", "openbsd"])
    @patch("sys.platform")
    def test_get_platform_linux_and_unix(self, mock_sys_platform, platform_name):
        """Test get_platform detects Unix-like systems as Linux.

        Test various Unix-like platform strings to ensure they
        all map to Platform.LINUX.

        Args:
            mock_sys_platform: Mocked sys.platform attribute.
            platform_name (str): Platform string to test.

        Raises:
            AssertionError: If Platform.LINUX is not returned.
        """
        with patch("sys.platform", platform_name):
            result = get_platform()
            assert result == Platform.LINUX


class TestIsAdmin:
    """Test the is_admin function for privilege checking.

    Verify administrative privilege detection works correctly
    on both Windows and Unix-like systems, including error
    handling scenarios.

    Example:
        >>> test = TestIsAdmin()
        >>> test.test_is_admin_windows_true()
    """

    @patch("sys.platform", "win32")
    @patch("ctypes.windll.shell32.IsUserAnAdmin")
    def test_is_admin_windows_true(self, mock_is_user_admin):
        """Test is_admin returns True for Windows administrator.

        Mock Windows admin check to return 1 (admin) and verify
        the function returns True.

        Args:
            mock_is_user_admin: Mocked Windows admin check function.

        Raises:
            AssertionError: If True is not returned.
        """
        mock_is_user_admin.return_value = 1
        result = is_admin()
        assert result is True

    @patch("sys.platform", "win32")
    @patch("ctypes.windll.shell32.IsUserAnAdmin")
    def test_is_admin_windows_false(self, mock_is_user_admin):
        """Test is_admin returns False for Windows non-administrator.

        Mock Windows admin check to return 0 (not admin) and verify
        the function returns False.

        Args:
            mock_is_user_admin: Mocked Windows admin check function.

        Raises:
            AssertionError: If False is not returned.
        """
        mock_is_user_admin.return_value = 0
        result = is_admin()
        assert result is False

    @patch("sys.platform", "linux")
    @patch("os.geteuid", create=True)
    def test_is_admin_unix_root(self, mock_geteuid):
        """Test is_admin returns True for Unix root user.

        Mock os.geteuid to return 0 (root UID) and verify
        the function returns True.

        Args:
            mock_geteuid: Mocked os.geteuid function.

        Raises:
            AssertionError: If True is not returned.
        """
        mock_geteuid.return_value = 0
        result = is_admin()
        assert result is True

    @patch("sys.platform", "linux")
    @patch("os.geteuid", create=True)
    def test_is_admin_unix_non_root(self, mock_geteuid):
        """Test is_admin returns False for Unix non-root user.

        Mock os.geteuid to return non-zero UID and verify
        the function returns False.

        Args:
            mock_geteuid: Mocked os.geteuid function.

        Raises:
            AssertionError: If False is not returned.
        """
        mock_geteuid.return_value = 1000
        result = is_admin()
        assert result is False

    @patch("sys.platform", "linux")
    def test_is_admin_unix_no_geteuid(self):
        """Test is_admin handles missing geteuid gracefully.

        Mock os.geteuid to raise AttributeError and verify
        the function returns False safely.

        Raises:
            AssertionError: If False is not returned.
        """
        with patch("os.geteuid", side_effect=AttributeError, create=True):
            result = is_admin()
            assert result is False

    @patch("sys.platform", "win32")
    @patch("ctypes.windll.shell32.IsUserAnAdmin")
    def test_is_admin_windows_exception(self, mock_is_user_admin):
        """Test is_admin raises PlatformError on Windows failure.

        Mock Windows admin check to raise exception and verify
        PlatformError is raised with correct attributes.

        Args:
            mock_is_user_admin: Mocked Windows admin check function.

        Raises:
            AssertionError: If PlatformError is not raised correctly.
        """
        mock_is_user_admin.side_effect = Exception("Access denied")

        with pytest.raises(PlatformError) as exc_info:
            is_admin()

        assert "Error checking admin privileges" in str(exc_info.value)
        assert exc_info.value.platform == "windows"
        assert exc_info.value.operation == "check_privileges"

    @patch("sys.platform", "linux")
    @patch("os.geteuid", create=True)
    def test_is_admin_unix_exception(self, mock_geteuid):
        """Test is_admin raises PlatformError on Unix failure.

        Mock os.geteuid to raise OSError and verify PlatformError
        is raised with correct attributes.

        Args:
            mock_geteuid: Mocked os.geteuid function.

        Raises:
            AssertionError: If PlatformError is not raised correctly.
        """
        mock_geteuid.side_effect = OSError("System error")

        with pytest.raises(PlatformError) as exc_info:
            is_admin()

        assert "Error checking admin privileges" in str(exc_info.value)
        assert exc_info.value.platform == "linux"


class TestGetAppDataDir:
    """Test the get_app_data_dir function for all platforms.

    Verify app data directory resolution works correctly
    across Windows, macOS, and Linux with proper error handling.

    Example:
        >>> test = TestGetAppDataDir()
        >>> test.test_get_app_data_dir_windows()
    """

    @patch("internal.core.platform.get_platform")
    @patch("pathlib.Path.home")
    def test_get_app_data_dir_windows(self, mock_home, mock_get_platform):
        """Test get_app_data_dir returns correct Windows path.

        Mock platform detection and home directory to verify
        Windows-specific app data path is constructed correctly.

        Args:
            mock_home: Mocked Path.home method.
            mock_get_platform: Mocked get_platform function.

        Raises:
            AssertionError: If Windows path is not constructed correctly.
        """
        mock_home.return_value = Path("/Users/test")
        mock_get_platform.return_value = Platform.WINDOWS

        with patch.object(Path, "mkdir") as mock_mkdir:
            result = get_app_data_dir()
            expected = Path("/Users/test/AppData/Local/TJD-Toolkit")
            assert result == expected
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("internal.core.platform.get_platform")
    @patch("pathlib.Path.home")
    def test_get_app_data_dir_macos(self, mock_home, mock_get_platform):
        """Test get_app_data_dir returns correct macOS path.

        Mock platform detection and home directory to verify
        macOS-specific app data path is constructed correctly.

        Args:
            mock_home: Mocked Path.home method.
            mock_get_platform: Mocked get_platform function.

        Raises:
            AssertionError: If macOS path is not constructed correctly.
        """
        mock_home.return_value = Path("/Users/test")
        mock_get_platform.return_value = Platform.MACOS

        with patch.object(Path, "mkdir") as mock_mkdir:
            result = get_app_data_dir()
            expected = Path("/Users/test/Library/Application Support/TJD-Toolkit")
            assert result == expected
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("internal.core.platform.get_platform")
    @patch("pathlib.Path.home")
    def test_get_app_data_dir_linux(self, mock_home, mock_get_platform):
        """Test get_app_data_dir returns correct Linux path.

        Mock platform detection and home directory to verify
        Linux-specific app data path is constructed correctly.

        Args:
            mock_home: Mocked Path.home method.
            mock_get_platform: Mocked get_platform function.

        Raises:
            AssertionError: If Linux path is not constructed correctly.
        """
        mock_home.return_value = Path("/home/test")
        mock_get_platform.return_value = Platform.LINUX

        with patch.object(Path, "mkdir") as mock_mkdir:
            result = get_app_data_dir()
            expected = Path("/home/test/.config/tjd-toolkit")
            assert result == expected
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("internal.core.platform.get_platform")
    @patch("pathlib.Path.home")
    def test_get_app_data_dir_permission_error(self, mock_home, mock_get_platform):
        """Test get_app_data_dir handles permission denied errors.

        Mock directory creation to raise PermissionError and verify
        PlatformError is raised with correct attributes.

        Args:
            mock_home: Mocked Path.home method.
            mock_get_platform: Mocked get_platform function.

        Raises:
            AssertionError: If PlatformError is not raised correctly.
        """
        mock_home.return_value = Path("/Users/test")
        mock_get_platform.return_value = Platform.WINDOWS

        with patch.object(Path, "mkdir", side_effect=PermissionError("Access denied")):
            with pytest.raises(PlatformError) as exc_info:
                get_app_data_dir()

            assert "Permission denied accessing app data directory" in str(exc_info.value)
            assert exc_info.value.platform == "windows"
            assert exc_info.value.operation == "access_app_data"

    @patch("internal.core.platform.get_platform")
    @patch("pathlib.Path.home")
    def test_get_app_data_dir_os_error(self, mock_home, mock_get_platform):
        """Test get_app_data_dir handles general OS errors.

        Mock directory creation to raise OSError and verify
        PlatformError is raised with correct attributes.

        Args:
            mock_home: Mocked Path.home method.
            mock_get_platform: Mocked get_platform function.

        Raises:
            AssertionError: If PlatformError is not raised correctly.
        """
        mock_home.return_value = Path("/Users/test")
        mock_get_platform.return_value = Platform.LINUX

        with patch.object(Path, "mkdir", side_effect=OSError("Disk full")):
            with pytest.raises(PlatformError) as exc_info:
                get_app_data_dir()

            assert "Failed to resolve or create app data directory" in str(exc_info.value)
            assert exc_info.value.platform == "linux"
            assert exc_info.value.operation == "access_app_data"


class TestRunAsAdmin:
    """Test the run_as_admin function for privilege elevation.

    Verify administrative command execution works correctly
    across platforms with proper error handling for various
    failure scenarios.

    Example:
        >>> test = TestRunAsAdmin()
        >>> test.test_run_as_admin_windows_success()
    """

    @patch("internal.core.platform.get_platform")
    @patch("subprocess.run")
    def test_run_as_admin_windows_success(self, mock_run, mock_get_platform):
        """Test run_as_admin executes successfully on Windows.

        Mock platform detection and subprocess execution to verify
        Windows runas command is constructed and executed correctly.

        Args:
            mock_run: Mocked subprocess.run function.
            mock_get_platform: Mocked get_platform function.

        Raises:
            AssertionError: If command execution fails or returns False.
        """
        mock_get_platform.return_value = Platform.WINDOWS
        mock_run.return_value = Mock()

        command = ["echo", "test"]
        result = run_as_admin(command)

        assert result is True
        mock_run.assert_called_once_with(
            ["runas", "/user:Administrator", "echo", "test"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("internal.core.platform.get_platform")
    @patch("subprocess.run")
    def test_run_as_admin_unix_success(self, mock_run, mock_get_platform):
        """Test run_as_admin executes successfully on Unix systems.

        Mock platform detection and subprocess execution to verify
        sudo command is constructed and executed correctly.

        Args:
            mock_run: Mocked subprocess.run function.
            mock_get_platform: Mocked get_platform function.

        Raises:
            AssertionError: If command execution fails or returns False.
        """
        mock_get_platform.return_value = Platform.LINUX
        mock_run.return_value = Mock()

        command = ["echo", "test"]
        result = run_as_admin(command)

        assert result is True
        mock_run.assert_called_once_with(
            ["sudo", "echo", "test"], check=True, capture_output=True, text=True
        )

    @patch("internal.core.platform.get_platform")
    @patch("subprocess.run")
    def test_run_as_admin_called_process_error(self, mock_run, mock_get_platform):
        """Test run_as_admin handles subprocess execution failure.

        Mock subprocess.run to raise CalledProcessError and verify
        PlatformError is raised with correct attributes.

        Args:
            mock_run: Mocked subprocess.run function.
            mock_get_platform: Mocked get_platform function.

        Raises:
            AssertionError: If PlatformError is not raised correctly.
        """
        mock_get_platform.return_value = Platform.LINUX
        mock_run.side_effect = subprocess.CalledProcessError(1, "sudo")

        command = ["echo", "test"]

        with pytest.raises(PlatformError) as exc_info:
            run_as_admin(command)

        assert "Failed to run command as admin" in str(exc_info.value)
        assert exc_info.value.platform == "linux"
        assert exc_info.value.operation == "privilege_elevation"

    @patch("internal.core.platform.get_platform")
    @patch("subprocess.run")
    def test_run_as_admin_file_not_found_error(self, mock_run, mock_get_platform):
        """Test run_as_admin handles missing elevation tools.

        Mock subprocess.run to raise FileNotFoundError and verify
        PlatformError is raised with correct attributes.

        Args:
            mock_run: Mocked subprocess.run function.
            mock_get_platform: Mocked get_platform function.

        Raises:
            AssertionError: If PlatformError is not raised correctly.
        """
        mock_get_platform.return_value = Platform.WINDOWS
        mock_run.side_effect = FileNotFoundError("runas not found")

        command = ["echo", "test"]

        with pytest.raises(PlatformError) as exc_info:
            run_as_admin(command)

        assert "Required elevation tool not found" in str(exc_info.value)
        assert exc_info.value.platform == "windows"
        assert exc_info.value.operation == "privilege_elevation"

    @pytest.mark.parametrize(
        "platform_type,expected_prefix",
        [
            (Platform.WINDOWS, ["runas", "/user:Administrator"]),
            (Platform.MACOS, ["sudo"]),
            (Platform.LINUX, ["sudo"]),
        ],
    )
    @patch("subprocess.run")
    def test_run_as_admin_platform_specific_commands(
        self, mock_run, platform_type, expected_prefix
    ):
        """Test run_as_admin uses correct elevation tools per platform.

        Verify that each platform uses its appropriate elevation
        command prefix (runas for Windows, sudo for Unix-like).

        Args:
            mock_run: Mocked subprocess.run function.
            platform_type (Platform): Platform enum value to test.
            expected_prefix (list): Expected command prefix for platform.

        Raises:
            AssertionError: If wrong elevation command is used.
        """
        with patch("internal.core.platform.get_platform", return_value=platform_type):
            command = ["test", "command"]
            run_as_admin(command)

            expected_call = expected_prefix + command
            mock_run.assert_called_once_with(
                expected_call, check=True, capture_output=True, text=True
            )


class TestIntegration:
    """Integration tests for the platform module.

    Test module-level functionality and ensure components
    work together correctly without mocking internal calls.

    Example:
        >>> test = TestIntegration()
        >>> test.test_module_imports()
    """

    def test_module_imports(self):
        """Test that all expected functions and classes are importable.

        Verify that the platform module exports all required
        components and they are callable/usable.

        Raises:
            ImportError: If any expected component cannot be imported.
            AssertionError: If imported components are not callable.
        """
        from internal.core.platform import (
            Platform,
            get_platform,
            is_admin,
            get_app_data_dir,
            run_as_admin,
        )

        assert Platform is not None
        assert callable(get_platform)
        assert callable(is_admin)
        assert callable(get_app_data_dir)
        assert callable(run_as_admin)

    def test_platform_detection_consistency(self):
        """Test that platform detection is consistent across calls.

        Verify that multiple calls to get_platform return the same
        result and that the result is a valid Platform enum.

        Raises:
            AssertionError: If platform detection is inconsistent.
        """
        platform1 = get_platform()
        platform2 = get_platform()
        assert platform1 == platform2
        assert isinstance(platform1, Platform)


@pytest.fixture
def mock_windows_environment():
    """Provide a mocked Windows environment for testing.

    Create a context where sys.platform is set to 'win32'
    to simulate testing on Windows.

    Yields:
        None: Context manager for Windows environment.

    Example:
        >>> def test_windows_feature(mock_windows_environment):
        ...     # Test runs in mocked Windows environment
        ...     pass
    """
    with patch("sys.platform", "win32"):
        yield


@pytest.fixture
def mock_linux_environment():
    """Provide a mocked Linux environment for testing.

    Create a context where sys.platform is set to 'linux'
    to simulate testing on Linux.

    Yields:
        None: Context manager for Linux environment.

    Example:
        >>> def test_linux_feature(mock_linux_environment):
        ...     # Test runs in mocked Linux environment
        ...     pass
    """
    with patch("sys.platform", "linux"):
        yield


@pytest.fixture
def mock_macos_environment():
    """Provide a mocked macOS environment for testing.

    Create a context where sys.platform is set to 'darwin'
    to simulate testing on macOS.

    Yields:
        None: Context manager for macOS environment.

    Example:
        >>> def test_macos_feature(mock_macos_environment):
        ...     # Test runs in mocked macOS environment
        ...     pass
    """
    with patch("sys.platform", "darwin"):
        yield


class TestEdgeCases:
    """Test edge cases and boundary conditions.

    Verify that the platform module handles unusual or
    edge case scenarios gracefully and correctly.

    Example:
        >>> test = TestEdgeCases()
        >>> test.test_empty_command_run_as_admin()
    """

    def test_empty_command_run_as_admin(self):
        """Test run_as_admin handles empty command lists.

        Verify that passing an empty command list to run_as_admin
        results in only the elevation prefix being executed.

        Raises:
            AssertionError: If empty command is not handled correctly.
        """
        with patch("internal.core.platform.get_platform", return_value=Platform.LINUX):
            with patch("subprocess.run") as mock_run:
                run_as_admin([])
                mock_run.assert_called_once_with(
                    ["sudo"], check=True, capture_output=True, text=True
                )

    @patch("pathlib.Path.home")
    def test_get_app_data_dir_with_complex_home_path(self, mock_home):
        """Test get_app_data_dir handles complex home directory paths.

        Verify that home directories with spaces and special
        characters are handled correctly in path construction.

        Args:
            mock_home: Mocked Path.home method.

        Raises:
            AssertionError: If complex paths are not handled correctly.
        """
        complex_path = Path("/Users/test user/with spaces/home")
        mock_home.return_value = complex_path

        with patch("internal.core.platform.get_platform", return_value=Platform.MACOS):
            with patch.object(Path, "mkdir"):
                result = get_app_data_dir()
                expected = complex_path / "Library" / "Application Support" / "TJD-Toolkit"
                assert result == expected
