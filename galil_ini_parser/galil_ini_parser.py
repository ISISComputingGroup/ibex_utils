import re

from collections import OrderedDict
from typing import Optional, Any, List

GALIL_CRATE_NUMBER_REGEX = r"(?<=\[G)\d+(?=\])]"
AXIS_NUMBER_REGEX = r"(?<=Axis )\S+"
AXIS_SETTING_REGEX = r"(?<=Axis {axis_letter} ).*"


class Galil:
    def __init__(self, crate_index: int):
        self.crate_index = crate_index
        self.ini_text = []
        self.settings = OrderedDict()
        self.axis_letters = None
        self.axes = {}

    def parse_ini_lines(self) -> None:
        """
        Parses the lines of the ini file referring to this galil crate.
        Only run when all settings for this crate have been added to its instance
        """
        self.add_crate_settings()
        self.axis_letters = self.get_axis_letters()
        for axis_label in self.axis_letters:
            self.axes[axis_label] = Axis(self.get_axis_settings(axis_label))

    def add_ini_line(self, line) -> None:
        """
        Adds a line of the galil ini file to this class
        """
        self.ini_text.append(line)

    def add_crate_settings(self) -> None:
        """
        Adds lines which do not refer to a specific axis to the galil crate settings
        """
        for line in self.ini_text:
            if not line.startswith("Axis"):
                # Line does not begin with Axis, so is a crate setting
                setting, value = line.split("=")
                self.settings[setting] = value

    def get_axis_letter_from_line(self, ini_line: str) -> str:
        """
        Extracts the letter of the axis referred to in a line of the ini file
        """
        matches = re.search(AXIS_NUMBER_REGEX, ini_line)
        if matches is not None:
            return matches.group(0)

    def get_axis_letters(self) -> List[str]:
        """
        Returns all the defined axis letters for this galil crate

        Returns:
            axis_letters: List containing the unique axis letters defined for this crate
        """
        axis_letters = []
        for line in self.ini_text:
            match = self.get_axis_letter_from_line(line)
            # match = re.search(AXIS_NUMBER_REGEX, line)
            if match is not None and match not in axis_letters:
                axis_letters.append(match)
        return axis_letters

    def get_axis_settings(self, axis_letter: str) -> str:
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
        return axis_settings

    def get_save_string(self) -> str:
        """
        Returns a string which can be written to file containing the settings for all axes on this crate
        """
        settings = []
        settings.append("[G{}]".format(self.crate_index))
        for crate_setting, setting_value in self.settings.items():
            settings.append("{setting} = {value}".format(setting=crate_setting, value=setting_value))
        for axis_letter in self.axis_letters:
            axis = self.axes[axis_letter]
            for setting, value in axis.settings.items():
                settings.append("Axis {axis_letter} {setting} = {value}".format(axis_letter=axis_letter,
                                                                              setting=setting,
                                                                              value=value))
        return "\n".join(settings)


class Axis:
    def __init__(self, axis_settings):
        self.settings = {}

        for setting in axis_settings:
            split_setting = setting.split("=")
            key = split_setting[0].strip()
            # This captures settings which contain an equals sign in them
            value = "=".join(split_setting[1:])
            self.settings[key] = value.strip()

    def get_value(self, setting: str, caster: Any) -> Optional[Any]:
        """
        Attempts to get the setting for this axis and cast it to type 'type'.

        Args:
            setting: The name of the setting to get
            type: Function which casts string to expected type of setting

        Returns:
            value: The setting, cast to 'type'. Is None if the setting does not exist for this axis
        """

        try:
            value = caster(self.settings[setting])
        except KeyError:
            value = None

        return value

    def set_value(self, setting: str, value: str, make_new=False) -> None:
        """
        Sets the setting with the specified value

        Args:
            setting: The setting to set
            value: A string representation of the value to set
            make_new: If True, create a new setting even if it does not currently exist
        """
        if setting in self.settings.keys():
            self.settings[setting] = value
        elif make_new:
            self.settings[setting] = value
