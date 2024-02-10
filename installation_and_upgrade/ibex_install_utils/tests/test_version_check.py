import pytest
from ibex_install_utils.version_check import *

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

    # def test_get_file_version(self):
    #     example_file = "\\\\isis.cclrc.ac.uk\shares\ISIS_Experiment_Controls_Public\\third_party_installers\latest_versions\Git-2.38.1-64-bit.exe"
    #     self.assertEqual(get_file_version(example_file), "2.38.1.1")

    # def test_get_msi_property(self):
    #     example_file = "\\\\isis.cclrc.ac.uk\shares\ISIS_Experiment_Controls_Public\\third_party_installers\latest_versions\OpenJDK17U-jdk_x64_windows_hotspot_17.0.4.1_1.msi"
    #     version = get_msi_property(example_file, MSI_PRODUCT_VERSION_PROPERTY)
    #     self.assertEqual(version, "17.0.4.101")
