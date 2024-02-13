import logging
import msilib
import re
import subprocess

from ibex_install_utils.software import Software
from ibex_install_utils.version_check import VERSION_REGEX, get_major_minor_patch

class Java(Software):
    def get_name(self) -> str:
        return "Java"
    
    def get_installed_version(self) -> str:
        version_output = subprocess.check_output("java --version").decode()
        installed_version = re.search(VERSION_REGEX, version_output).group(1)
        return get_major_minor_patch(installed_version)

    def get_installer_pattern(self) -> str:
        return r"^OpenJDK.*?([0-9.]*)_?[0-9]*.msi"
    
    def get_installer_version(self, path: str) -> str:
        return get_msi_property(path, "ProductVersion")


def get_msi_property(path: str, property: str) -> str:
    """Reads a property from msi metadata database of a file.

    Args:
        path: The path to the file.
        property: The property to read.
    Returns:
        The string value of the property on successful read, None otherwise.
    """
    value = None
    try:
        db = msilib.OpenDatabase(path, msilib.MSIDBOPEN_READONLY)
        view = db.OpenView("SELECT Value FROM Property WHERE Property='" + property + "'")
        view.Execute(None)
        result = view.Fetch()
        value = result.GetString(1)
    except:
        logging.exception(f"Can't read property '{property}' from file '{path}'.")
    logging.info(f"Read value '{value}' for property '{property}' from file '{path}'.")
    return value