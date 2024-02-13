import logging
import re
import subprocess
import win32api

from ibex_install_utils.software import Software
from ibex_install_utils.version_check import VERSION_REGEX, get_major_minor_patch


class Git(Software):
    def get_name(self) -> str:
        return "Git"
    
    def get_installed_version(self) -> str:
        version_output = subprocess.check_output("git --version").decode()
        installed_version = re.search(VERSION_REGEX, version_output).group(1)
        return get_major_minor_patch(installed_version)
    
    def get_installer_pattern(self) -> str:
        return r"^Git-([0-9.]*)-[0-9]*-bit.exe"
    
    def get_installer_version(self, path: str) -> str:
        return get_file_version(path)


def get_file_version(path: str):
    """Reads the version of a file from file version info.

    Args:
        path: The path to the file.
    Returns:
        The string version (x.x.x.x) on successful read, None otherwise.
    """
    version = None
    try:
        info = win32api.GetFileVersionInfo(path, '\\')
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
    except:
        logging.exception(f"Can't get file version info of '{path}'")
    logging.info(f"Read version '{version}' from file info of '{path}'")
    return version