import argparse
import pathlib
from galil_ini_parser import Galil, Axis, apply_home_shift, common_setting_names, extract_galil_settings_from_file

from typing import Optional

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input_file", help="Input file location", action="store", required=True)
parser.add_argument("-o", "--output_file", help="Output file location", action="store", required=True)
parser.add_argument("--reference_file", help="Location of a file to compare output of this script to", action="store")
args = parser.parse_args()

input_file = pathlib.Path(args.input_file)
output_file = pathlib.Path(args.output_file)
reference_file = pathlib.Path(args.reference_file)

if input_file == output_file:
    raise RuntimeError("Output file cannot overwrite input file")

#from filenames import input_file, output_file, reference_file


def get_motor_resolution(axis: Axis) -> float:
    """
    Calculates the smallest detectable movement for this axis.
    Movements smaller than this value are equivalent to zero movement.
    """
    motor_res = axis.get_value(common_setting_names["MOTOR_RES"], float)
    encoder_res = axis.get_value(common_setting_names["ENCODER_RES"], float)
    return 1.0/min(motor_res, encoder_res)


def float_to_setting_string(value: Optional[float]) -> Optional[str]:
    """
    If the input value is not none, return the float as a galil ini string
    """
    if value is not None:
        return "{:8.6f}".format(value)


galil_crates = extract_galil_settings_from_file(input_file)
reference_galils = extract_galil_settings_from_file(reference_file)

for galil in galil_crates.values():
    for axis in galil.axes.values():
        lowerthresh = 0.5 * get_motor_resolution(axis)
        #print("Galil {} Axis {}".format(galil.crate_index, axis.axis_index))

        axis_negated = axis.get_value(common_setting_names["NEGATED"], bool)

        old_offset = axis.get_value(common_setting_names["OFFSET"], float)
        old_user_offset = axis.get_value(common_setting_names["USER_OFFSET"], float)
        old_homeval = axis.get_value(common_setting_names["HOMEVAL"], float)

        old_hlim = axis.get_value(common_setting_names["HLIM"], float)
        old_llim = axis.get_value(common_setting_names["LLIM"], float)

        if axis_negated:
            print("Warning! This axis has a negated direction, check its output is sane")

        new_settings = apply_home_shift(old_homeval, old_offset, old_user_offset, old_hlim, old_llim)
        for setting, value in new_settings.items():
            if value is not None:
                axis.set_value(setting, float_to_setting_string(value))

for galil in galil_crates.values():
    reference_galil = reference_galils[galil.crate_index]
    for axis in galil.axes.values():
        print("Galil {} Axis {}".format(galil.crate_index, axis.axis_index))
        reference_axis = reference_galil.axes[axis.axis_index]
        for setting in axis.settings.keys():
            # Loop though all the settings, see where the differences are
            reference = reference_axis.get_value(setting, str)
            script = axis.get_value(setting, str)
            if reference != script:
                print("{} new: {} ref: {}".format(setting, script, reference))

with open(output_file, 'w') as f:
    for galil in galil_crates.values():
        f.write(galil.get_save_string())
        f.write("\n")
