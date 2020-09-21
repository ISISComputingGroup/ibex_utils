import unittest

from galil_ini_parser import Galil, Axis
from parameterized import parameterized
from sans2d_galils import zero_homeval_zero_offsets, nonzero_homeval_nonzero_offsets, setting_names

GALIL_CRATE_INDEX = 1
AXIS_INDEX = "A"

SETTING_STRING_WITHOUT_AXIS = "{setting} = {value}"
SETTING_STRING_WITH_AXIS = "Axis {axis_index} {setting} = {value}"

# This change in coordinates from SECI to IBEX was verified by hand
original_sans2d_axis = {
    setting_names["OFFSET"]: 0.0,
    setting_names["USER_OFFSET"]: 0.0,
    setting_names["HOMEVAL"]: 1045.0,
    setting_names["HLIM"]: 1045.0,
    setting_names["LLIM"]: -10.0,
}

corrected_sans2d_axis = {
    setting_names["OFFSET"]: 1045.0,
    setting_names["USER_OFFSET"]: 0.0,
    setting_names["HOMEVAL"]: 1045.0,
    setting_names["HLIM"]: 0.0,
    setting_names["LLIM"]: -1055.0
}

# These are dummy data sets corrected by hand
nonzero_homeval_nonzero_offset_axis = {
    setting_names["OFFSET"]: 10.0,
    setting_names["USER_OFFSET"]: 5.0,
    setting_names["HOMEVAL"]: 1045.0,
    setting_names["HLIM"]: 1450.0,
    setting_names["LLIM"]: -10.0,

    setting_names["OFFSET"]: 7.0,
    setting_names["USER_OFFSET"]: 3.0,
    setting_names["HOMEVAL"]: 20.0,
    setting_names["HLIM"]: 50.0,
    setting_names["LLIM"]: 10.0,
}

corrected_nonzero_homeval_nonzero_offset_axis = {
    setting_names["OFFSET"]: 1045.0,
    setting_names["USER_OFFSET"]: 0.0,
    setting_names["HOMEVAL"]: 1045.0,
    setting_names["HLIM"]: 420.0,
    setting_names["LLIM"]: -1040.0,

    setting_names["OFFSET"]: 20.0,
    setting_names["USER_OFFSET"]: 0.0,
    setting_names["HOMEVAL"]: 20.0,
    setting_names["HLIM"]: 40.0,
    setting_names["LLIM"]: 0.0,
}

nonzero_homeval_zero_offset_axis = {
    setting_names["OFFSET"]: 0.0,
    setting_names["USER_OFFSET"]: 0.0,
    setting_names["HOMEVAL"]: 20.0,
    setting_names["HLIM"]: 50.0,
    setting_names["LLIM"]: 10.0,
}

corrected_nonzero_homeval_zero_offset_axis = {
    setting_names["OFFSET"]: 20.0,
    setting_names["USER_OFFSET"]: 0.0,
    setting_names["HOMEVAL"]: 20.0,
    setting_names["HLIM"]: 30.0,
    setting_names["LLIM"]: -10.0,
}

infinite_limits_axis = nonzero_homeval_nonzero_offset_axis
infinite_limits_axis["LLIM"] = -1.0 * float("inf")
infinite_limits_axis["HLIM"] = 1.0 * float("inf")

corrected_infinite_limits_axis = corrected_nonzero_homeval_nonzero_offset_axis
corrected_infinite_limits_axis["LLIM"] = -1.0 * float("inf")
corrected_infinite_limits_axis["HLIM"] = 1.0 * float("inf")


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
        self.galil.add_ini_line(SETTING_STRING_WITHOUT_AXIS.format(setting=new_setting, value=setting_value))

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

        self.galil.add_ini_line(SETTING_STRING_WITH_AXIS.format(axis_index=axis_index,
                                                                setting=new_setting, value=setting_value))

        self.assertIn(axis_index, self.galil.axes.keys())

    def test_GIVEN_setting_line_with_axis_label_WHEN_that_axis_does_exist_THEN_setting_gets_added_to_axis(self):
        axis_index = "A"
        new_setting = "Setting"
        setting_value = "value"
        self.galil.add_ini_line(SETTING_STRING_WITH_AXIS.format(axis_index=axis_index,
                                                                setting=new_setting, value=setting_value))

        self.assertEqual(self.galil.axes[axis_index].settings[new_setting], setting_value)

    def test_GIVEN_settings_on_crate_WHEN_save_string_requested_THEN_first_line_is_crate_identifier(self):
        galil_save_string = self.galil.get_save_string().split("\n")
        self.assertEqual(galil_save_string[0], "[G{}]".format(GALIL_CRATE_INDEX))

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

        save_string = self.galil.get_save_string().split("\n")

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

    def test_GIVEN_nonzero_homeval_and_nonzero_offsets_WHEN_new_limits_calculated_THEN_correct_values_returned(self):
        new_axis_values = nonzero_homeval_nonzero_offsets(infinite_limits_axis[setting_names["HOMEVAL"]],
                                                          infinite_limits_axis[setting_names["OFFSET"]],
                                                          infinite_limits_axis[setting_names["USER_OFFSET"]],
                                                          infinite_limits_axis[setting_names["HLIM"]],
                                                          infinite_limits_axis[setting_names["LLIM"]])
        for key in new_axis_values.keys():
            self.assertEqual(corrected_infinite_limits_axis[key], new_axis_values[key])

    def test_GIVEN_zero_homeval_and_nonzero_offsets_WHEN_new_limits_calculated_THEN_correct_values_returned(self):
        new_axis_values = zero_homeval_zero_offsets(original_sans2d_axis[setting_names["HOMEVAL"]],
                                                    original_sans2d_axis[setting_names["HLIM"]],
                                                    original_sans2d_axis[setting_names["LLIM"]])
        for key in new_axis_values.keys():
            self.assertEqual(corrected_sans2d_axis[key], new_axis_values[key])

    def test_GIVEN_nonzero_homeval_and_zero_offsets_WHEN_new_limits_calculated_THEN_correct_values_returned(self):
        new_axis_values = nonzero_homeval_nonzero_offsets(nonzero_homeval_zero_offset_axis[setting_names["HOMEVAL"]],
                                                          nonzero_homeval_zero_offset_axis[setting_names["OFFSET"]],
                                                          nonzero_homeval_zero_offset_axis[setting_names["USER_OFFSET"]],
                                                          nonzero_homeval_zero_offset_axis[setting_names["HLIM"]],
                                                          nonzero_homeval_zero_offset_axis[setting_names["LLIM"]])
        for key in new_axis_values.keys():
            self.assertEqual(corrected_nonzero_homeval_zero_offset_axis[key], new_axis_values[key])

    def test_GIVEN_both_calculation_WHEN_new_limits_calculated_THEN_they_are_equivalent(self):
        new_axis_values = nonzero_homeval_nonzero_offsets(original_sans2d_axis[setting_names["HOMEVAL"]],
                                                          0.0,
                                                          0.0,
                                                          original_sans2d_axis[setting_names["HLIM"]],
                                                          original_sans2d_axis[setting_names["LLIM"]])
        for key in new_axis_values.keys():
            self.assertEqual(corrected_sans2d_axis[key], new_axis_values[key])

    def test_GIVEN_nonzero_homeval_and_infinite_limits_WHEN_new_limits_calculated_THEN_limits_are_unchanged(self):
        new_axis_values = nonzero_homeval_nonzero_offsets(nonzero_homeval_nonzero_offset_axis[setting_names["HOMEVAL"]],
                                                          nonzero_homeval_nonzero_offset_axis[setting_names["OFFSET"]],
                                                          nonzero_homeval_nonzero_offset_axis[setting_names["USER_OFFSET"]],
                                                          nonzero_homeval_nonzero_offset_axis[setting_names["HLIM"]],
                                                          nonzero_homeval_nonzero_offset_axis[setting_names["LLIM"]])
        for key in new_axis_values.keys():
            self.assertEqual(corrected_nonzero_homeval_nonzero_offset_axis[key], new_axis_values[key])
