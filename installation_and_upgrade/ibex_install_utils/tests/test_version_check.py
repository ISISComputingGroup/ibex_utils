import pytest
import os
from unittest.mock import patch
from ibex_install_utils.version_check import *

def get_version_from_name(name):
    """
    Return version number read out from the filename
    """
    basename = os.path.basename(name)
    version = re.search(r"([0-9]+\.[0-9]+(\.[0-9]+)+)", basename).group(1)
    return get_major_minor_patch(version)

class TestVersionCheck:

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

    @patch("ibex_install_utils.version_check.get_msi_property", return_value="17.0.4.0")
    @patch("ibex_install_utils.version_check.get_file_version", return_value="2.0.3.0")
    def test_get_version_from_metadata(self, mock_get_file_version, mock_get_msi_property):
        assert get_version_from_metadata("something.msi") == "17.0.4.0"
        assert get_version_from_metadata("something.exe") == "2.0.3.0"
        
        with pytest.raises(Exception):
            get_version_from_metadata("something.txt") 

    @patch("ibex_install_utils.version_check.get_msi_property", return_value="17.0.4")
    @patch("ibex_install_utils.version_check.get_file_version", return_value="2.0.3.0")
    def test_get_latest_version(self, mock_get_file_version, mock_get_msi_property):
        assert get_latest_version(["./java.msi", "./git.exe"]) == ("./java.msi", "17.0.4")

        with pytest.raises(Exception):
            get_latest_version(["./java.msi", "./git.exe", "./something.txt"])

    @patch("ibex_install_utils.version_check.get_version_from_metadata", side_effect=get_version_from_name)
    @patch("ibex_install_utils.version_check.get_installed_version")
    @patch("ibex_install_utils.version_check.get_filenames_in_dir")
    def test_version_check(self, mock_get_filenames_in_dir, mock_get_installed_version, mock_get_version_from_metadata):
        mock_get_filenames_in_dir.return_value = ["OpenJDK_17.0.1_1.msi",
                                                  "OpenJDK_17.0.4_1.msi",
                                                  "OpenJDK_16.0.4.6_1.msi"]
        mock_get_installed_version.return_value = "17.0.4"

        @version_check("java")
        def should_run(_, should_run):
            # As a result of the version check decorator this should not run
            # if the simulated verions match
            assert should_run == True

        should_run(self, False)

        mock_get_installed_version.return_value = "17.0.0.3"

        should_run(self, True)  #TODO fix because we will never know if it ran or not

        mock_get_filenames_in_dir.return_value = ["Git-2.3.0-1.exe",
                                                  "Git-2.3.2-1-bit.exe",
                                                  "Git-1.2.3-1-bit.exe"]
        mock_get_installed_version.return_value = "2.3.2.1" # fourth segment is disregarded in comparison

        @version_check("git")
        def should_run_git(_, should_run):
            # As a result of the version check decorator this should not run
            # if the simulated verions match
            assert should_run == True
        
        should_run_git(self, False)
