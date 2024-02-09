import unittest
from ibex_install_utils.version_check import *

class TestVersionCheck(unittest.TestCase):

    def test_get_major_minor_patch(self):
        # good version patterns
        self.assertEqual(get_major_minor_patch("17"), "17.0.0")
        self.assertEqual(get_major_minor_patch("17.0"), "17.0.0")
        self.assertEqual(get_major_minor_patch("17.23"), "17.23.0")
        self.assertEqual(get_major_minor_patch("17.0.7.3"), "17.0.7")
        self.assertEqual(get_major_minor_patch("17.0.0.3"), "17.0.0")

        # wrong version patterns
        with self.assertRaises(AttributeError):
            get_major_minor_patch("17.0.0.3.4")

        with self.assertRaises(AttributeError):
            get_major_minor_patch("17.")
        
        with self.assertRaises(AttributeError):
            get_major_minor_patch("java 17.2.4")

    def test_get_file_version(self):
        example_file = "\\\\isis.cclrc.ac.uk\shares\ISIS_Experiment_Controls_Public\\third_party_installers\latest_versions\Git-2.38.1-64-bit.exe"
        self.assertEqual(get_file_version(example_file), "2.38.1.1")

    def test_get_msi_property(self):
        example_file = "\\\\isis.cclrc.ac.uk\shares\ISIS_Experiment_Controls_Public\\third_party_installers\latest_versions\OpenJDK17U-jdk_x64_windows_hotspot_17.0.4.1_1.msi"
        version = get_msi_property(example_file, MSI_PRODUCT_VERSION_PROPERTY)
        self.assertEqual(version, "17.0.4.101")
    
    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())

    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)

if __name__ == '__main__':
    unittest.main()