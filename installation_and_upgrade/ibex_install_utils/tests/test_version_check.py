import os
from unittest.mock import Mock

import pytest
from ibex_install_utils.software_dependency import is_higher
from ibex_install_utils.software_dependency.git import Git
from ibex_install_utils.version_check import *


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
        assert is_higher("17.0", "17.0.1") == True
        assert is_higher("17.0.6", "17.0.1") == False

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
        gitMock = Git()

        gitMock.get_installed_version = Mock(return_value="2.3.2")
        gitMock.get_version_of = Mock(side_effect=get_version_from_name)
        gitMock.find_available = Mock(return_value=MOCK_GIT_INSTALLERS)

        functionMock = Mock()

        @version_check(gitMock)
        def function(_):
            functionMock()

        function(self)
        functionMock.assert_not_called()

    def test_GIVEN_git_old_WHEN_version_checked_THEN_decorated_function_called(self):
        gitMock = Git()

        gitMock.get_installed_version = Mock(return_value="2.3.0")
        gitMock.get_version_of = Mock(side_effect=get_version_from_name)
        gitMock.find_available = Mock(return_value=MOCK_GIT_INSTALLERS)

        functionMock = Mock()

        @version_check(gitMock)
        def function(_):
            functionMock()

        function(self)
        functionMock.assert_called_once()
