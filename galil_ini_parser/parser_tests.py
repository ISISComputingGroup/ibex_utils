import unittest

from galil_ini_parser import Galil, Axis
from galil_ini_parser import apply_home_shift, common_setting_names, extract_galil_settings_from_file

from mock import patch, call
from parameterized import parameterized
from typing import Dict

GALIL_CRATE_INDEX = "G1"
AXIS_INDEX = "A"

SETTING_STRING_WITHOUT_AXIS = "{setting} = {value}"
SETTING_STRING_WITH_AXIS = "Axis {axis_index} {setting} = {value}"


def POPULATE_AXIS(offset: float, user_offset: float, homeval: float, hlim: float, llim: float) -> Dict[str, float]:
    """
    Creates a dictionary with key/value pairs corresponding to axis parameters to be changed
    """
    axis = {
        common_setting_names["OFFSET"]: offset,
        common_setting_names["USER_OFFSET"]: user_offset,
        common_setting_names["HOMEVAL"]: homeval,
        common_setting_names["HLIM"]: hlim,
        common_setting_names["LLIM"]: llim,
    }

    return axis


TEST_AXIS_CASES = ([
    ("Nonzero homeval nonzero offset",
     POPULATE_AXIS(7.0, 3.0, 20.0, 50.0, 10.0),
     POPULATE_AXIS(20.0, 0.0, 20.0, 40.0, 0.0)),

    ("Zero homeval nonzero offsets",
     POPULATE_AXIS(10.0, 5.0, 0.0, 50.0, -10.0),
     POPULATE_AXIS(0.0, 0.0, 0.0, 65.0, 5.0)),

    ("Nonzero homeval zero offsets",
     POPULATE_AXIS(0.0, 0.0, 1045.0, 1045.0, -10.0),
     POPULATE_AXIS(1045.0, 0.0, 1045.0, 0.0, -1055.0)),

    ("Infinite limits",
     POPULATE_AXIS(7.0, 3.0, 20.0, float("inf"), -1.0*float("inf")),
     POPULATE_AXIS(20.0, 0.0, 20.0, None, None))

])

FLOAT_SETTING = {"Setting": 1.2}


class GalilTests(unittest.TestCase):
    """
    Tests for the galil crate class
    """

    def setUp(self):
        self.galil = Galil(GALIL_CRATE_INDEX)

    def test_GIVEN_new_galil_object_THEN_settings_dictionary_is_empty(self):
        self.assertEqual(len(self.galil.settings.keys()), 0)

    def test_GIVEN_new_galil_object_THEN_axis_list_is_empty(self):
        self.assertEqual(len(self.galil.axes.keys()), 0)

    def test_GIVEN_setting_line_with_no_axis_label_THEN_line_gets_added_to_crate_settings(self):
        new_setting = "Setting"
        setting_value = "value"
        self.galil.parse_line(SETTING_STRING_WITHOUT_AXIS.format(setting=new_setting, value=setting_value))

        self.assertEqual(self.galil.settings[new_setting], setting_value)

    def test_GIVEN_setting_line_with_axis_label_WHEN_that_axis_does_not_exist_THEN_axis_label_extracted_correctly(self):
        axis_index = "A"
        new_setting = "Setting"
        setting_value = "value"
        extracted_axis_letter = self.galil.get_axis_letter_from_line(SETTING_STRING_WITH_AXIS.format(axis_index=axis_index,
                                                                                                     setting=new_setting,
                                                                                                     value=setting_value))

        self.assertEqual(axis_index, extracted_axis_letter)

    def test_GIVEN_setting_line_with_axis_label_WHEN_that_axis_does_not_exist_THEN_new_axis_is_made(self):
        axis_index = "A"
        new_setting = "Setting"
        setting_value = "value"

        self.assertNotIn(axis_index, self.galil.axes.keys())

        self.galil.parse_line(SETTING_STRING_WITH_AXIS.format(axis_index=axis_index,
                                                                setting=new_setting, value=setting_value))

        self.assertIn(axis_index, self.galil.axes.keys())

    def test_GIVEN_setting_line_with_axis_label_WHEN_that_axis_does_exist_THEN_setting_gets_added_to_axis(self):
        axis_index = "A"
        new_setting = "Setting"
        setting_value = "value"
        self.galil.parse_line(SETTING_STRING_WITH_AXIS.format(axis_index=axis_index,
                                                                setting=new_setting, value=setting_value))

        self.assertEqual(self.galil.axes[axis_index].settings[new_setting], setting_value)

    def test_GIVEN_settings_on_crate_WHEN_save_string_requested_THEN_first_line_is_crate_identifier(self):
        galil_save_string = self.galil.get_save_strings()
        self.assertEqual(galil_save_string[0], "[{}]".format(GALIL_CRATE_INDEX))

    def test_GIVEN_settings_on_crate_and_axes_WHEN_save_string_requested_THEN_settings_from_crate_and_axes_are_present(self):
        axis_index = "A"
        axis_setting = "Offset"
        axis_setting_value = "12.3"

        crate_setting = "unit"
        crate_setting_value = "mm"

        axis = Axis(axis_index)
        axis.settings[axis_setting] = axis_setting_value

        self.galil.axes[axis_index] = axis
        self.galil.settings[crate_setting] = crate_setting_value

        save_string = self.galil.get_save_strings()

        self.assertIn(SETTING_STRING_WITHOUT_AXIS.format(setting=crate_setting, value=crate_setting_value), save_string)
        self.assertIn(SETTING_STRING_WITH_AXIS.format(axis_index=axis_index, setting=axis_setting, value=axis_setting_value),
                      save_string)


class AxisTests(unittest.TestCase):
    """
    Tests for the galil axis class
    """

    def setUp(self):
        self.axis = Axis("A")

    def test_GIVEN_settings_line_WHEN_line_contains_axis_prefix_THEN_axis_prefix_removed_from_line(self):
        axis_index = "A"
        new_setting = "Setting"
        setting_value = "value"
        parsed_settings_line = self.axis.scrub_axis_prefix(SETTING_STRING_WITH_AXIS.format(axis_index=axis_index,
                                                           setting=new_setting, value=setting_value))

        self.assertEqual(parsed_settings_line, SETTING_STRING_WITHOUT_AXIS.format(setting=new_setting, value=setting_value))

    def test_GIVEN_settings_line_THEN_setting_correctly_added_to_axis(self):
        axis_index = "A"
        new_setting = "Setting"
        setting_value = "value"

        self.axis.add_setting_from_ini_line(SETTING_STRING_WITH_AXIS.format(axis_index=axis_index,
                                            setting=new_setting, value=setting_value))

        self.assertEqual(self.axis.settings[new_setting], setting_value)

    @parameterized.expand([
        ("pos_float", 12.3, float),
        ("neg_float", -12.3, float),
        ("pos_inf", float("inf"), float),
        ("neg_inf", -float("inf"), float),
        ("pos_int", 123, int),
        ("neg_int", -123, int),
        ("string", "string_value", str)
    ])
    def test_GIVEN_set_value_exists_WHEN_value_retrieved_THEN_correct_value_returned(self, _, setting_value, caster):
        new_setting = "Setting"

        self.axis.settings[new_setting] = setting_value

        self.assertEqual(self.axis.get_value(new_setting, caster), setting_value)

    def test_GIVEN_set_value_does_not_exist_WHEN_value_retieved_THEN_None_is_returned(self):
        setting_does_not_exist = "Setting"

        self.assertNotIn(setting_does_not_exist, self.axis.settings.keys())

        self.assertIsNone(self.axis.get_value(setting_does_not_exist, str))

    def test_GIVEN_new_setting_is_set_WHEN_make_new_not_true_THEN_no_setting_is_added(self):
        setting_to_add = "Setting"
        sample_value = "value"

        self.assertNotIn(setting_to_add, self.axis.settings.keys())

        self.axis.set_value(setting_to_add, sample_value, make_new=False)

        self.assertNotIn(setting_to_add, self.axis.settings.keys())

    def test_GIVEN_new_setting_is_set_WHEN_make_new_is_true_THEN_new_setting_is_added(self):
        setting_to_add = "Setting"
        sample_value = "value"

        self.assertNotIn(setting_to_add, self.axis.settings.keys())

        self.axis.set_value(setting_to_add, sample_value, make_new=True)

        self.assertIn(setting_to_add, self.axis.settings.keys())


class IniParserTests(unittest.TestCase):
    """
    Tests for the code which changes SECI offsets to IBEX offsets
    """

    @parameterized.expand(TEST_AXIS_CASES)
    def test_GIVEN_test_case_axis_WHEN_new_limits_calculated_THEN_correct_values_returned(self, _, axis, corrected_axis):
        new_axis_values = apply_home_shift(axis[common_setting_names["HOMEVAL"]],
                                           axis[common_setting_names["OFFSET"]],
                                           axis[common_setting_names["USER_OFFSET"]],
                                           axis[common_setting_names["HLIM"]],
                                           axis[common_setting_names["LLIM"]])

        for key in new_axis_values.keys():
            self.assertEqual(corrected_axis[key], new_axis_values[key])

    def test_GIVEN_sample_ini_file_WHEN_parsed_THEN_new_galil_objects_created(self):
        galil_1_name = "G0"
        galil_2_name = "G1"

        split_ini_file = [
            "[{}]".format(galil_1_name),
            "setting = value",
            "Axis A setting = value",
            "[{}]".format(galil_2_name),
            "setting = value",
            "Axis B setting = value",
        ]

        with patch("galil_ini_parser.Galil") as mock_galil:
            extract_galil_settings_from_file(split_ini_file)
            mock_galil.assert_any_call(galil_1_name)
            mock_galil.assert_any_call(galil_2_name)
