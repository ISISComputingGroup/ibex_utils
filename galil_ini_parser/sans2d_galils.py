from galil_ini_parser import Galil, Axis

from typing import Optional, Dict

# File which contains current galil.ini
input_file = ""
# Destination for the parsed config file
output_file = ""
# I used this to check all the values against the galil ini file made by Tom and David
reference_file = ""

HOMEVAL = "Home Position"
USER_OFFSET = "User Offset"
OFFSET = "Offset"
LLIM = "Soft Min"
HLIM = "Soft Max"
NEGATED = "Negate Motor Direction"
ENCODER_RES = "Encoder Steps Per Unit"
MOTOR_RES = "Motor Steps Per Unit"


def get_motor_resolution(axis: Axis):
    """
    Calculates the smallest detectable movement for this axis
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

# This threshold should be a fraction of the min(encoder or motor res)
lowerthresh = 1e-5


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
        OFFSET: float_to_setting_string(new_offset),
        HLIM: float_to_setting_string(new_hlim),
        LLIM: float_to_setting_string(new_llim),
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
#        axis.set_value(HLIM, "{:8.6f}".format(new_hlim))
    else:
        new_hlim = None

    if abs(old_llim) != float('inf'):
        new_llim = old_llim + difference_in_offsets
#        axis.set_value(LLIM, "{:8.6f}".format(new_llim))
    else:
        new_llim = None

    new_settings = {
        OFFSET: float_to_setting_string(new_offset),
        HLIM: float_to_setting_string(new_hlim),
        LLIM: float_to_setting_string(new_llim),
        USER_OFFSET: float_to_setting_string(new_user_offset)
    }
    return new_settings


for galil in galil_crates.values():
    for axis in galil.axes.values():
        #print("Galil {} Axis {}".format(galil.crate_index, axis.axis_index))

        axis_negated = axis.get_value(NEGATED, bool)

        old_offset = axis.get_value(OFFSET, float)
        old_user_offset = axis.get_value(USER_OFFSET, float)
        old_homeval = axis.get_value(HOMEVAL, float)

        old_hlim = axis.get_value(HLIM, float)
        old_llim = axis.get_value(LLIM, float)

        if (abs(old_homeval) > lowerthresh) and (abs(old_offset) < lowerthresh) and (abs(old_user_offset) < lowerthresh):
            new_settings = zero_homeval_zero_offsets(old_homeval, old_hlim, old_llim)
            for setting, value in new_settings.items():
                axis.set_value(setting, value)
            # new_settings = zero_homeval_zero_offsets(old_homeval, old_hlim, old_llim)
            
            # # Nonzero homeval, zero offsets
            # #print("SECI Home Position: {}".format(old_homeval))
            # new_offset = old_homeval
            # new_hlim = old_hlim - old_homeval
            # new_llim = old_llim - old_homeval

            # # Write new values
            # axis.set_value(OFFSET, "{:8.6f}".format(new_offset))
            # #print("Offset: {} -> {}".format(old_offset, new_offset))

            # # Only write new limits if they aren't infinite
            # if abs(old_hlim) != float('inf'):
            #     axis.set_value(HLIM, "{:8.6f}".format(new_hlim))
            #     #print("HLIM: {} -> {}".format(old_hlim, new_hlim))
            # if abs(old_llim) != float('inf'):
            #     axis.set_value(LLIM, "{:8.6f}".format(new_llim))
            #     #print("LLIM: {} -> {}".format(old_llim, new_llim))

            # # Write new values
            # axis.set_value(OFFSET, "{:8.6f}".format(new_offset))
            # #print("Offset: {} -> {}".format(old_offset, new_offset))

            # # Only write new limits if they aren't infinite
            # if abs(old_hlim) != float('inf'):
            #     axis.set_value(HLIM, "{:8.6f}".format(new_hlim))
            #     #print("HLIM: {} -> {}".format(old_hlim, new_hlim))
            # if abs(old_llim) != float('inf'):
            #     axis.set_value(LLIM, "{:8.6f}".format(new_llim))
            #    # print("LLIM: {} -> {}".format(old_llim, new_llim))

        elif (abs(old_homeval) > lowerthresh) and (abs(old_offset + old_user_offset) > lowerthresh):
            new_settings = nonzero_homeval_nonzero_offsets(old_homeval, old_offset, old_user_offset, old_hlim, old_llim)
            for setting, value in new_settings.items():
                axis.set_value(setting, value)
            # # Nonzero homeval, nonzero offsets
            # #print("SECI Home Position: {}".format(old_homeval))
            # combined_offset = old_offset + old_user_offset
            # new_offset = old_homeval
            # new_user_offset = 0.0
            # difference_in_offsets = combined_offset - old_homeval
            # # the homeval in motor coords needs to be zero
            # # => (homeval - any offsets ) == 0
            # # => combined offsets == homeval
            # # Only thing which changes is that the limits don't have the offsets applied,
            # # so need to remember how much we've changed offsets by and change the limits accordingly
            # new_hlim = old_hlim + difference_in_offsets
            # new_llim = old_llim + difference_in_offsets

            # # Write new values
            # axis.set_value(OFFSET, "{:8.6f}".format(new_offset))
            # #print("Offset: {} -> {}".format(old_offset, new_offset))

            # axis.set_value(USER_OFFSET, "{:8.6f}".format(new_user_offset))

            # # Only write new limits if they aren't infinite
            # if abs(old_hlim) != float('inf'):
            #     axis.set_value(HLIM, "{:8.6f}".format(new_hlim))
            #     #print("HLIM: {} -> {}".format(old_hlim, new_hlim))
            # if abs(old_llim) != float('inf'):
            #     axis.set_value(LLIM, "{:8.6f}".format(new_llim))
            #    # print("LLIM: {} -> {}".format(old_llim, new_llim))

        elif (abs(old_homeval) > lowerthresh) and (abs(old_offset + old_user_offset) > lowerthresh) and axis_negated:
            print("Warning! This axis has a negated direction, check its output is sane")
            new_settings = nonzero_homeval_nonzero_offsets(old_homeval, old_offset, old_user_offset, old_hlim, old_llim)
            for setting, value in new_settings.items():
                axis.set_value(setting, value)
            # # Nonzero homeval, nonzero offsets
            # #print("SECI Home Position: {}".format(old_homeval))
            # combined_offset = old_offset + old_user_offset
            # new_offset = old_homeval
            # new_user_offset = 0.0
            # difference_in_offsets = combined_offset - old_homeval
            # # the homeval in motor coords needs to be zero
            # # => (homeval - any offsets ) == 0
            # # => combined offsets == homeval
            # # Only thing which changes is that the limits don't have the offsets applied,
            # # so need to remember how much we've changed offsets by and change the limits accordingly
            # new_hlim = old_hlim + difference_in_offsets
            # new_llim = old_llim + difference_in_offsets

            # # Write new values
            # axis.set_value(OFFSET, "{:8.6f}".format(new_offset))
            # #print("Offset: {} -> {}".format(old_offset, new_offset))

            # axis.set_value(USER_OFFSET, "{:8.6f}".format(new_user_offset))

            # # Only write new limits if they aren't infinite
            # if abs(old_hlim) != float('inf'):
            #     axis.set_value(HLIM, "{:8.6f}".format(new_hlim))
            #     #print("HLIM: {} -> {}".format(old_hlim, new_hlim))
            # if abs(old_llim) != float('inf'):
            #     axis.set_value(LLIM, "{:8.6f}".format(new_llim))
            #    # print("LLIM: {} -> {}".format(old_llim, new_llim))

# NEED TO MAKE SURE THESE TWO IF STATEMENTS GIVE THE SAME ANSWER WHEN OFFSETS = 0
# If they do, can delete the first one

# Maybe test this against the galil in the office too?

for galil in galil_crates.values():
    reference_galil = reference_galils[galil.crate_index]
    for axis in galil.axes.values():
        print(get_motor_resolution(axis))
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
