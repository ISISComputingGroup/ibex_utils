import re

from collections import OrderedDict
from typing import Optional, Any, Dict, List

AXIS_NUMBER_REGEX = r"(?<=Axis )\S+"

common_setting_names = {
    "HOMEVAL": "Home Position",
    "USER_OFFSET": "User Offset",
    "OFFSET": "Offset",
    "LLIM": "Soft Min",
    "HLIM": "Soft Max",
    "NEGATED": "Negate Motor Direction",
    "ENCODER_RES": "Encoder Steps Per Unit",
    "MOTOR_RES": "Motor Steps Per Unit"
}


def apply_home_shift(old_homeval: float,
                     old_offset: float,
                     old_user_offset: float,
                     old_hlim: float,
                     old_llim: float) -> Dict[str, Optional[str]]:
    """
    Combines both the user and axis offsets into one (the new axis offset).
    Shifts the axis limits by the difference between the old and new home position

    Args:
        old_homeval: The current Home Postion in the settings file
        old_hlim: The current soft max limit in the settings file.
        old_llim: The current soft min limit in the settings file.
        old_user_offset: The current user offset in the settings file
        old_offset: The current axis offset in the settings file
    Returns:
        new_settings: Dictionary containing the string representation of the updated values.
    """

    old_combined_offset = old_offset + old_user_offset

    # Set offset = homeval, so home position written to device is (homeval - offset) = 0
    new_offset = old_homeval
    new_user_offset = 0.0

    # Distance to shift the limits by to maintain distance from limits to home position
    difference_in_schemes = old_combined_offset - new_offset

    # Infinite limits do not get changed (set to None so can be ignored)
    if abs(old_hlim) != float('inf'):
        new_hlim = old_hlim + difference_in_schemes
    else:
        new_hlim = None

    if abs(old_llim) != float('inf'):
        new_llim = old_llim + difference_in_schemes
    else:
        new_llim = None

    new_settings = {
        common_setting_names["OFFSET"]: new_offset,
        common_setting_names["HLIM"]: new_hlim,
        common_setting_names["LLIM"]: new_llim,
        common_setting_names["USER_OFFSET"]: new_user_offset
    }
    return new_settings


class Galil:
    def __init__(self, crate_index: int):
        self.crate_index = crate_index
        self.settings = OrderedDict()
        self.axes = {}

    def parse_line(self, line) -> None:
        """
        Adds a line of the galil ini file to this class
        """
        axis_index = self.get_axis_letter_from_line(line)
        if axis_index is None:
            # Not referring to an axis so is a global setting for crate
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

    def get_save_strings(self) -> List[str]:
        """
        Returns a strings can containing all settings for all axes on this crate
        """
        settings = ["[{}]".format(self.crate_index)]
        for crate_setting, setting_value in self.settings.items():
            settings.append("{setting} = {value}".format(setting=crate_setting, value=setting_value))
        for axis_letter in self.axes.keys():
            axis = self.axes[axis_letter]
            for setting, value in axis.settings.items():
                settings.append("Axis {axis_letter} {setting} = {value}".format(axis_letter=axis_letter,
                                                                                setting=setting,
                                                                                value=value))
        return settings


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
            String containing "setting_name = value" pair
        """
        return ini_line[len(self.axis_line_prefix):].strip()

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

    def get_value(self, setting: str, caster: Any, default_value: Any = None) -> Optional[Any]:
        """
        Attempts to get the setting for this axis and cast it to type 'type'.

        Args:
            setting: The name of the setting to get
            caster: Function which casts string to expected type of setting
            default_value: The value to be returned if the setting was not found

        Returns:
            value: The setting, cast using supplied caster. Equals default_value if setting does not exist on this axis
        """

        try:
            value = caster(self.settings[setting])
        except KeyError:
            value = default_value

        return value

    def set_value(self, setting: str, value: str, make_new: bool = False) -> None:
        """
        Sets the setting with the specified value

        Args:
            setting: The setting to set
            value: A string representation of the value to set
            make_new: If True, create a new setting even if it does not currently exist
        """
        if setting in self.settings.keys() or make_new:
            self.settings[setting] = value


def extract_galil_settings_from_file(file: List[str]) -> Dict[str, Galil]:
    """
    Given a file contatining galil settings, extract the settings as Galil objects

    Args:
        file: List of lines from the settings files

    Returns:
        galil_crates: Dictionary containing the Galil settings held in file
    """
    galil_crates = {}
    for line in file:
        # New galil crate if line starts [Gx]
        if line.startswith("[G"):
            crate_index = line.strip().strip("[]")
            galil_crates[crate_index] = Galil(crate_index)
        elif "=" in line:
            galil_crates[crate_index].parse_line(line)
        else:
            print("Line did not contain valid setting or galil identifier information, ignoring: {}".format(line))

    return galil_crates
