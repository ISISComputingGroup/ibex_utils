from galil_ini_parser import Galil

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


def zero_homeval_zero_offsets(old_homeval):
    new_offset = old_homeval
    new_hlim = old_hlim - old_homeval
    new_llim = old_llim - old_homeval

    new_settings = {
        OFFSET: new_offset,
        HLIM: new_hlim,
        LLIM: new_llim,
        USER_OFFSET: None
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

        if (abs(old_offset) > lowerthresh) or (abs(old_user_offset) > lowerthresh):
            print("Galil {} Axis {}".format(galil.crate_index, axis.axis_index))
            print(old_offset, old_user_offset)

        if (abs(old_homeval) > lowerthresh) and (abs(old_offset) < lowerthresh) and (abs(old_user_offset) < lowerthresh):
            # Nonzero homeval, zero offsets
            #print("SECI Home Position: {}".format(old_homeval))
            new_offset = old_homeval
            new_hlim = old_hlim - old_homeval
            new_llim = old_llim - old_homeval

            # Write new values
            axis.set_value(OFFSET, "{:8.6f}".format(new_offset))
            #print("Offset: {} -> {}".format(old_offset, new_offset))

            # Only write new limits if they aren't infinite
            if abs(old_hlim) != float('inf'):
                axis.set_value(HLIM, "{:8.6f}".format(new_hlim))
                #print("HLIM: {} -> {}".format(old_hlim, new_hlim))
            if abs(old_llim) != float('inf'):
                axis.set_value(LLIM, "{:8.6f}".format(new_llim))
                #print("LLIM: {} -> {}".format(old_llim, new_llim))

            # Write new values
            axis.set_value(OFFSET, "{:8.6f}".format(new_offset))
            #print("Offset: {} -> {}".format(old_offset, new_offset))

            # Only write new limits if they aren't infinite
            if abs(old_hlim) != float('inf'):
                axis.set_value(HLIM, "{:8.6f}".format(new_hlim))
                #print("HLIM: {} -> {}".format(old_hlim, new_hlim))
            if abs(old_llim) != float('inf'):
                axis.set_value(LLIM, "{:8.6f}".format(new_llim))
               # print("LLIM: {} -> {}".format(old_llim, new_llim))

        elif (abs(old_homeval) > lowerthresh) and (abs(old_offset + old_user_offset) > lowerthresh):
            # Nonzero homeval, nonzero offsets
            #print("SECI Home Position: {}".format(old_homeval))
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

            # Write new values
            axis.set_value(OFFSET, "{:8.6f}".format(new_offset))
            #print("Offset: {} -> {}".format(old_offset, new_offset))

            axis.set_value(USER_OFFSET, "{:8.6f}".format(new_user_offset))

            # Only write new limits if they aren't infinite
            if abs(old_hlim) != float('inf'):
                axis.set_value(HLIM, "{:8.6f}".format(new_hlim))
                #print("HLIM: {} -> {}".format(old_hlim, new_hlim))
            if abs(old_llim) != float('inf'):
                axis.set_value(LLIM, "{:8.6f}".format(new_llim))
               # print("LLIM: {} -> {}".format(old_llim, new_llim))

        elif (abs(old_homeval) > lowerthresh) and (abs(old_offset + old_user_offset) > lowerthresh) and axis_negated:
            print("Warning! This axis has a negated direction, check its output is sane")
            # Nonzero homeval, nonzero offsets
            #print("SECI Home Position: {}".format(old_homeval))
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

            # Write new values
            axis.set_value(OFFSET, "{:8.6f}".format(new_offset))
            #print("Offset: {} -> {}".format(old_offset, new_offset))

            axis.set_value(USER_OFFSET, "{:8.6f}".format(new_user_offset))

            # Only write new limits if they aren't infinite
            if abs(old_hlim) != float('inf'):
                axis.set_value(HLIM, "{:8.6f}".format(new_hlim))
                #print("HLIM: {} -> {}".format(old_hlim, new_hlim))
            if abs(old_llim) != float('inf'):
                axis.set_value(LLIM, "{:8.6f}".format(new_llim))
               # print("LLIM: {} -> {}".format(old_llim, new_llim))

# NEED TO MAKE SURE THESE TWO IF STATEMENTS GIVE THE SAME ANSWER WHEN OFFSETS = 0
# If they do, can delete the first one

# Maybe test this against the galil in the office too?

for galil in galil_crates.values():
    reference_galil = reference_galils[galil.crate_index]
    for axis in galil.axes.values():
        #print("Galil {} Axis {}".format(galil.crate_index, axis.axis_index))
        reference_axis = reference_galil.axes[axis.axis_index]
        for setting in axis.settings.keys():
            # Loop though all the settings, see where the differences are
            reference = reference_axis.get_value(setting, str)
            script = axis.get_value(setting, str)
            if reference != script:
                pass
                #print("{} new: {} ref: {}".format(setting, script, reference))

with open(output_file, 'w') as f:
    for galil in galil_crates.values():
        f.write(galil.get_save_string())
        f.write("\n")
