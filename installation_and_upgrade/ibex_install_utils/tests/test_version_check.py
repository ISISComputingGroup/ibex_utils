import os
import re
from unittest.mock import Mock

import pytest
from ibex_install_utils.software_dependency import is_higher
from ibex_install_utils.software_dependency.git import Git
from ibex_install_utils.version_check import get_major_minor_patch, version_check


def get_version_from_name(name):
    """
    Return version number read out from the filename
    """
    basename = os.path.basename(name)
    version = re.search(r"([0-9]+\.[0-9]+(\.[0-9]+)+)", basename).group(1)
    return version


MOCK_GIT_INSTALLERS = [
    "Git-2.3.0-1.exe",
    "Git-2.3.2-1-bit.exe",  # latest
    "Git-1.2.3-1-bit.exe",
]


class TestVersionCheck:
    def test_is_higher(self):
        assert is_higher("17.0", "17.0.1")
        assert not is_higher("17.0.6", "17.0.1")

    def test_get_major_minor_patch(self):
        # good version patterns
        assert get_major_minor_patch("17") == "17.0.0"
        assert get_major_minor_patch("17.0") == "17.0.0"
        assert get_major_minor_patch("17.23") == "17.23.0"
        assert get_major_minor_patch("17.0.7.3") == "17.0.7"
        assert get_major_minor_patch("17.0.0.3") == "17.0.0"

        # wrong version patterns
        with pytest.raises(AttributeError):
            get_major_minor_patch("17.0.0.3.4")

        with pytest.raises(AttributeError):
            get_major_minor_patch("17.")

        with pytest.raises(AttributeError):
            get_major_minor_patch("java 17.2.4")

    def test_GIVEN_git_latest_WHEN_version_checked_THEN_decorated_function_not_called(self):
        git_mock = Git()

        git_mock.get_installed_version = Mock(return_value="2.3.2")
        git_mock.get_version_of = Mock(side_effect=get_version_from_name)
        git_mock.find_available = Mock(return_value=MOCK_GIT_INSTALLERS)

        func_mock = Mock()

        @version_check(git_mock)
        def function(_):
            func_mock()

        function(self)
        func_mock.assert_not_called()

    def test_GIVEN_git_old_WHEN_version_checked_THEN_decorated_function_called(self):
        git_mock = Git()

        git_mock.get_installed_version = Mock(return_value="2.3.0")
        git_mock.get_version_of = Mock(side_effect=get_version_from_name)
        git_mock.find_available = Mock(return_value=MOCK_GIT_INSTALLERS)

        func_mock = Mock()

        @version_check(git_mock)
        def function(_):
            func_mock()

        function(self)
        func_mock.assert_called_once()
