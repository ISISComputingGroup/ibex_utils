import argparse
import pathlib

from distutils.util import strtobool

from galil_ini_parser import apply_home_shift, common_setting_names, extract_galil_settings_from_file

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input_file", help="Input file location", action="store", required=True)
parser.add_argument("-o", "--output_file", help="Output file location", action="store", required=True)
parser.add_argument("--reference_file", help="Location of a file to compare output of this script to", action="store")
args = parser.parse_args()

input_file = pathlib.Path(args.input_file)
output_file = pathlib.Path(args.output_file)

if input_file == output_file:
    raise RuntimeError("Output file cannot overwrite input file")

with open(input_file) as f:
    file_contents = f.readlines()

galil_crates = extract_galil_settings_from_file(file_contents)

output_contents = []

for galil in galil_crates.values():
    for axis in galil.axes.values():
        lowerthresh = 0.5 * axis.get_motor_resolution()

        axis_negated = axis.get_value(common_setting_names["NEGATED"], strtobool)

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
                print("Setting Galil {galil} Axis {axis} {setting} to {value}".format(
                    galil=galil.crate_index,
                    axis=axis.axis_index,
                    setting=setting,
                    value="{:8.6f}".format(value)
                ))
                axis.set_value(setting, "{:8.6f}".format(value))

    output_contents.extend(galil.get_save_strings())

with open(output_file, 'w') as f:
    f.write("\n".join(output_contents))
    f.write("\n")

if args.reference_file is not None:
    # Compare the new galil settings to a reference file (hand-migrated)
    reference_file = pathlib.Path(args.reference_file)
    with open(reference_file, 'r') as f:
        reference_contents = f.readlines()
    reference_galils = extract_galil_settings_from_file(reference_contents)

    galils_with_new_settings = extract_galil_settings_from_file(output_contents)
    for galil in galils_with_new_settings.values():
        reference_galil = reference_galils[galil.crate_index]
        for axis in galil.axes.values():
            print("Galil {} Axis {}".format(galil.crate_index, axis.axis_index))
            reference_axis = reference_galil.axes[axis.axis_index]
            for setting in axis.settings.keys():
                # Loop though all the settings, see where the differences are
                reference = reference_axis.get_value(setting, str)
                script = axis.get_value(setting, str)
                if reference != script:
                    print("{} New value: {} Reference value: {}".format(setting, script, reference))
