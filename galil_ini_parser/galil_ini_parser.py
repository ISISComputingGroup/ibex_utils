import re

GALIL_CRATE_NUMBER_REGEX = r"(?<=\[G)\d+(?=\])]"
AXIS_NUMBER_REGEX = r"(?<=Axis )\S+"
AXIS_SETTING_REGEX = r"(?<=Axis {axis_letter} ).*"


class Galil:
    def __init__(self, crate_index: int, crate_ini_text: str):
        self.crate_index = crate_index
        self.ini_text = crate_ini_text
        self.settings = {}
        self.axis_letters = self.get_axis_letters()
        self.axes = OrderedDict()

        self.add_settings()

        for axis_label in self.axis_letters:
            self.axes[axis_label] = Axis(self.get_axis_settings(axis_label))

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
            axis_letters: Set containing the unique axis letters defined for this crate
        """
        axis_letters = set(re.findall(AXIS_NUMBER_REGEX, "\n".join(self.ini_text)))

        return set(axis_letters)

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


class Axis:
    def __init__(self, axis_settings):
        self.settings = {}

        for setting in axis_settings:
            split_setting = setting.split("=")
            key = split_setting[0]
            # This captures settings which contain an equals sign in them
            value = split_setting[1:]
            self.settings[key] = value


filename = "C:\\Users\\plf31717\\Downloads\\sans2d_vis\\Sans2d Galil\\Galil.ini"


with open(filename, 'r') as f:
    ini_file = f.read().split("\n")


galil_crates = {}

crate_index = None
crate_settings = []
for line in ini_file:
    #print(line)
    # New galil crate if line starts [G
    if line.startswith("[G"):
        print('asdf')
        if crate_index is not None:
            galil_crates[crate_index] = Galil(crate_index, crate_settings)

        crate_index = int(line[2])

        #crate_index = int(re.search(GALIL_CRATE_NUMBER_REGEX, line).group(0))
        crate_settings = []
    else:
        crate_settings.append(line)

for galil in galil_crates:
    print(galil.n)
    for axis in galil.axes:
        print(axis.settings["Home Offset"])
        print(axis.settings["Offset"])
    for axis in galil.axis_letters:


print(galil_crates)
