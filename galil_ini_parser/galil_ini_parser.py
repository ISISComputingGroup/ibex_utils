import re

from collections import OrderedDict
from typing import Optional, Any

AXIS_NUMBER_REGEX = r"(?<=Axis )\S+"


class Galil:
    def __init__(self, crate_index: int):
        self.crate_index = crate_index
        self.settings = OrderedDict()
        self.axes = {}

    def add_ini_line(self, line) -> None:
        """
        Adds a line of the galil ini file to this class
        """
        axis_index = self.get_axis_letter_from_line(line)
        if axis_index is None:
            setting, value = line.split("=")
            setting = setting.strip()
            value = value.strip()
            self.settings[setting] = value
        elif axis_index in self.axes.keys():
            axis = self.axes[axis_index]
            axis.add_setting_from_ini_line(line)
        else:
            new_axis = Axis(axis_index)
            new_axis.add_setting_from_ini_line(line)

            self.axes[axis_index] = new_axis

    def get_axis_letter_from_line(self, ini_line: str) -> str:
        """
        Extracts the letter of the axis referred to in a line of the ini file
        """
        matches = re.search(AXIS_NUMBER_REGEX, ini_line)
        if matches is not None:
            return matches.group(0)
        else:
            return None

    def get_save_string(self) -> str:
        """
        Returns a string which can be written to file containing the settings for all axes on this crate
        """
        settings = []
        settings.append("[G{}]".format(self.crate_index))
        for crate_setting, setting_value in self.settings.items():
            settings.append("{setting} = {value}".format(setting=crate_setting, value=setting_value))
        for axis_letter in self.axes.keys():
            axis = self.axes[axis_letter]
            for setting, value in axis.settings.items():
                settings.append("Axis {axis_letter} {setting} = {value}".format(axis_letter=axis_letter,
                                                                                setting=setting,
                                                                                value=value))
        return "\n".join(settings)


class Axis:
    def __init__(self, axis_index: str):
        self.settings = {}
        self.axis_index = axis_index
        self.axis_line_prefix = "Axis {}".format(axis_index)

    def scrub_axis_prefix(self, ini_line: str) -> str:
        """
        Removes the axis identifier from a line in the ini file. Returns a string which defines its setting

        Args:
            ini_line: Line from the ini file

        Returns:
            setting: String containing "setting_name = value" pair 
        """
        # Scrub the Axis prefix from the line
        setting = ini_line[len(self.axis_line_prefix):].strip()
        return setting

    def add_setting_from_ini_line(self, ini_line: str):
        """
        Imports a new setting from a line in the galil ini file
        """
        setting = self.scrub_axis_prefix(ini_line)
        split_line = setting.split("=")
        key = split_line[0].strip()
        # This captures settings which contain an equals sign in them
        value = "=".join(split_line[1:]).strip()
        self.set_value(key, value, make_new=True)

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
