from enum import Enum
from galil_ini_parser import Galil, Axis

from typing import Optional, Dict

# File which contains current galil.ini
input_file = ""
# Destination for the parsed config file
output_file = ""
# I used this to check all the values against the galil ini file made by Tom and David
reference_file = ""

from filenames import input_file, output_file, reference_file

HOMEVAL = "Home Position"
USER_OFFSET = "User Offset"
OFFSET = "Offset"
LLIM = "Soft Min"
HLIM = "Soft Max"
NEGATED = "Negate Motor Direction"
ENCODER_RES = "Encoder Steps Per Unit"
MOTOR_RES = "Motor Steps Per Unit"


setting_names = {
    "HOMEVAL": "Home Position",
    "USER_OFFSET": "User Offset",
    "OFFSET": "Offset",
    "LLIM": "Soft Min",
    "HLIM": "Soft Max",
    "NEGATED": "Negate Motor Direction",
    "ENCODER_RES": "Encoder Steps Per Unit",
    "MOTOR_RES": "Motor Steps Per Unit"
}


def get_motor_resolution(axis: Axis):
    """
    Calculates the smallest detectable movement for this axis.
    Movements smaller than this value are equivalent to zero movement.
    """
    motor_res = axis.get_value(MOTOR_RES, float)
    encoder_res = axis.get_value(ENCODER_RES, float)
    return 1.0/min(motor_res, encoder_res)


def float_to_setting_string(value: Optional[float]) -> Optional[str]:
    """
    If the input value is not none, return the float as a galil ini string
    """
    if value is not None:
        return "{:8.6f}".format(value)


def zero_homeval_zero_offsets(old_homeval: float, old_hlim: float, old_llim: float) -> Dict[str, str]:
    """
    Applies the old homeval as a new offset, and shifts the limits accordingly

    Args:
        old_homeval: The current Home Postion in the settings file
        old_hlim: The current soft max limit in the settings file
        old_llim: The current soft min limit in the settings file
    Returns:
        new_settings: Dictionary containing the string representation of the updated values.
    """
    new_offset = old_homeval

    # Only change limits if they aren't infinite
    if abs(old_hlim) != float('inf'):
        new_hlim = old_hlim - old_homeval
    else:
        new_hlim = None

    if abs(old_llim) != float('inf'):
        new_llim = old_llim - old_homeval
    else:
        new_llim = None

    new_settings = {
        OFFSET: new_offset,
        HLIM: new_hlim,
        LLIM: new_llim,
    }

    return new_settings


def nonzero_homeval_nonzero_offsets(old_homeval: float,
                                    old_offset: float,
                                    old_user_offset: float,
                                    old_hlim: float,
                                    old_llim: float) -> Dict[str, str]:
    """
    Combines both the user and axis offsets into one (the new axis offset).
    Shifts the axis limits by this amount

    Args:
        old_homeval: The current Home Postion in the settings file
        old_hlim: The current soft max limit in the settings file
        old_llim: The current soft min limit in the settings file
        old_user_offset: The current user offset in the settings file
        old_offset: The current axis offset in the settings file
    Returns:
        new_settings: Dictionary containing the string representation of the updated values.
    """

    # Nonzero homeval, nonzero offsets
    combined_offset = old_offset + old_user_offset
    new_offset = old_homeval
    new_user_offset = 0.0
    difference_in_offsets = combined_offset - old_homeval
    # the homeval in motor coords needs to be zero
    # => (homeval - any offsets ) == 0
    # => combined offsets == homeval
    # Only thing which changes is that the limits don't have the offsets applied,
    # so need to remember how much we've changed offsets by and change the limits accordingly
    new_hlim = old_hlim + difference_in_offsets
    new_llim = old_llim + difference_in_offsets

    # Only write new limits if they aren't infinite
    if abs(old_hlim) != float('inf'):
        new_hlim = old_hlim + difference_in_offsets
    else:
        new_hlim = None

    if abs(old_llim) != float('inf'):
        new_llim = old_llim + difference_in_offsets
    else:
        new_llim = None

    new_settings = {
        OFFSET: new_offset,
        HLIM: new_hlim,
        LLIM: new_llim,
        USER_OFFSET: new_user_offset
    }
    return new_settings


galil_crates = {}

with open(input_file, 'r') as f:
    for line in f:
        # New galil crate if line starts [Gx]
        if line.startswith("[G"):
            crate_index = int(line[2])
            galil_crates[crate_index] = Galil(crate_index)
        elif "=" in line:
            galil_crates[crate_index].add_ini_line(line)
        else:
            # Not a setting or new galil crate, skip this line
            pass

reference_galils = {}
with open(reference_file, 'r') as f:
    for line in f:
        # New galil crate if line starts [Gx]
        if line.startswith("[G"):
            crate_index = int(line[2])
            reference_galils[crate_index] = Galil(crate_index)
        elif "=" in line:
            reference_galils[crate_index].add_ini_line(line)
        else:
            # Not a setting or new galil crate, skip this line
            pass

for galil in galil_crates.values():
    for axis in galil.axes.values():
        lowerthresh = 0.5 * get_motor_resolution(axis)
        #print("Galil {} Axis {}".format(galil.crate_index, axis.axis_index))

        axis_negated = axis.get_value(NEGATED, bool)

        old_offset = axis.get_value(OFFSET, float)
        old_user_offset = axis.get_value(USER_OFFSET, float)
        old_homeval = axis.get_value(HOMEVAL, float)

        old_hlim = axis.get_value(HLIM, float)
        old_llim = axis.get_value(LLIM, float)

        if (abs(old_homeval) > lowerthresh) and (abs(old_offset) < lowerthresh) and (abs(old_user_offset) < lowerthresh):
            new_settings = zero_homeval_zero_offsets(old_homeval, old_hlim, old_llim)
            # new_settings = nonzero_homeval_nonzero_offsets(old_homeval, old_offset, old_user_offset, old_hlim, old_llim)
            for setting, value in new_settings.items():
                if value is not None:
                    axis.set_value(setting, float_to_setting_string(value))

        elif (abs(old_homeval) > lowerthresh) and (abs(old_offset + old_user_offset) > lowerthresh):
            new_settings = nonzero_homeval_nonzero_offsets(old_homeval, old_offset, old_user_offset, old_hlim, old_llim)
            for setting, value in new_settings.items():
                if value is not None:
                    axis.set_value(setting, float_to_setting_string(value))

        elif (abs(old_homeval) > lowerthresh) and (abs(old_offset + old_user_offset) > lowerthresh) and axis_negated:
            print("Warning! This axis has a negated direction, check its output is sane")
            new_settings = nonzero_homeval_nonzero_offsets(old_homeval, old_offset, old_user_offset, old_hlim, old_llim)
            for setting, value in new_settings.items():
                if value is not None:
                    axis.set_value(setting, float_to_setting_string(value))

# NEED TO MAKE SURE THESE TWO IF STATEMENTS GIVE THE SAME ANSWER WHEN OFFSETS = 0
# If they do, can delete the first one

# Maybe test this against the galil in the office too?

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
                #pass
                print("{} new: {} ref: {}".format(setting, script, reference))

with open(output_file, 'w') as f:
    for galil in galil_crates.values():
        f.write(galil.get_save_string())
        f.write("\n")
