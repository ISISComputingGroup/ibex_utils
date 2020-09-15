import re

from collections import OrderedDict

GALIL_CRATE_NUMBER_REGEX = r"(?<=\[G)\d+(?=\])]"
AXIS_NUMBER_REGEX = r"(?<=Axis )\S+"
AXIS_SETTING_REGEX = r"(?<=Axis {axis_letter} ).*"


class Galil:
    def __init__(self, crate_index: int, crate_ini_text: str):
        self.crate_index = crate_index
        self.ini_text = []#crate_ini_text
        self.settings = OrderedDict()
        self.axis_letters = None#self.get_axis_letters()
        self.axes = {}

        #self.add_settings()

        # for axis_label in self.axis_letters:
        #     self.axes[axis_label] = Axis(self.get_axis_settings(axis_label))

    def parse_ini_lines(self):
        self.add_settings()
        self.axis_letters = self.get_axis_letters()
        for axis_label in self.axis_letters:
            self.axes[axis_label] = Axis(self.get_axis_settings(axis_label))

    def add_ini_line(self, line):
        """
        Adds a line of the galil ini file to this class
        """
        self.ini_text.append(line)

    def add_setting(self, ini_line):
        print(line)
        if not line.startswith("Axis") and not line:
            # Line does not begin with Axis, so is a crate setting
            setting, value = line.split("=")
            self.settings[setting] = value

    def add_settings(self):
        """
        Adds lines which do not refer to a specific axis to the galil crate settings
        """
        for line in self.ini_text:
            if not line.startswith("Axis"):
                # Line does not begin with Axis, so is a crate setting
                setting, value = line.split("=")
                self.settings[setting] = value

    def get_axis_letter_from_line(self, ini_line: str):
        matches = re.search(AXIS_NUMBER_REGEX, ini_line)
        if matches is not None:
            return matches.group(0)

    def get_axis_letters(self):
        """
        Returns all the defined axis letters for this galil crate

        Returns:
            axis_letters: List containing the unique axis letters defined for this crate
        """
        axis_letters = []
        for line in self.ini_text:
            match = re.search(AXIS_NUMBER_REGEX, line)
            if match and match.group(0) not in axis_letters:
                axis_letters.append(match.group(0))
        return axis_letters

    def get_axis_settings(self, axis_letter: str):
        """
        Returns the lines which contain settings for a single axis

        Args:
            axis_letter: The identifying letter of the axis
        """
        axis_settings = []
        for line in self.ini_text:
            setting = re.search(AXIS_SETTING_REGEX.format(axis_letter=axis_letter), line)
            if setting is not None:
                axis_settings.append(setting.group(0))
            #if line.startswith("Axis {}".format(axis_letter)):
            #    axis_settings.append(line.strip("Axis {} ".format(axis_letter)))
        return axis_settings

    def get_save_string(self):
        """
        Returns a string which can be written to file containing the settings for all axes on this crate
        """
        settings = []
        for crate_setting, setting_value in self.settings.items():
            settings.append("{setting}={value}".format(setting=crate_setting, value=setting_value))
        for axis_letter in self.axis_letters:
            axis = self.axes[axis_letter]
            for setting, value in axis.settings.items():
                settings.append("Axis {axis_letter} {setting}={value}".format(axis_letter=axis_letter,
                                                                              setting=setting,
                                                                              value=value))
        return "\n".join(settings)


class Axis:
    def __init__(self, axis_settings):
        self.settings = OrderedDict()

        for setting in axis_settings:
            split_setting = setting.split("=")
            key = split_setting[0]
            # This captures settings which contain an equals sign in them
            value = ''.join(split_setting[1:])
            self.settings[key] = value




with open(filename, 'r') as f:
    ini_file = f.read().split("\n")


galil_crates = OrderedDict()

crate_index = None
crate_settings = []

for line in ini_file:
    #print(line)
    # New galil crate if line starts [Gx]
    if line.startswith("[G"):
        crate_index = int(line[2])
        galil_crates[crate_index] = Galil(crate_index, crate_settings)
    elif "=" in line:
        galil_crates[crate_index].add_ini_line(line)
    else:
        # Not a setting or new galil crate, skip this line
        pass

for galil in galil_crates.values():
    galil.parse_ini_lines()

# for galil in galil_crates.values():
#     print("Galil crate {}".format(galil.crate_index))
#     for axis_name in galil.axis_letters:
#         axis = galil.axes[axis_name]
#         print("Axis {} home offset {}".format(axis_name, axis.settings["Home Offset"]))
#         print("Axis {} offset {}".format(axis_name, axis.settings["Offset"]))
# #    for axis in galil.axis_letters:

for galil in galil_crates.values():
    print("[G{}]".format(galil.crate_index))
    print(galil.get_save_string())

for galil in galil_crates.values():
    print("[G{}]".format(galil.crate_index))

# print(galil_crates)
