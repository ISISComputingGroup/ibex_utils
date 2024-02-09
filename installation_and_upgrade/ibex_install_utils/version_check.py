"""
Third party program version checker infrastructure.
"""
import subprocess
import re
import msilib
import os
import win32api
import logging
from ibex_install_utils.tasks.common_paths import THIRD_PARTY_INSTALLERS_LATEST_DIR
from typing import List

JAVA_INSTALLER_VERSION_REGEX = r"^OpenJDK.*?([0-9.]*)_?[0-9]*.msi"
GIT_INSTALLER_VERSION_REGEX = r"^Git-([0-9.]*)-[0-9]*-bit.exe"
VERSION_REGEX = r"\s([0-9]+\.[0-9]+(\.[0-9]+)+)"

JAVA_INSTALLER_PATTERN = r"^OpenJDK.*?([0-9.]*)_?[0-9]*.msi"
GIT_INSTALLER_PATTERN = r"^Git-([0-9.]*)-[0-9]*-bit.exe"
WIX_INSTALLER_PATTERN = r"^wix.*\.exe"

MSI_PRODUCT_VERSION_PROPERTY = "ProductVersion"

INDENT = "    "

def version_check(program, version):
    """
        Decorator for tasks that check program version numbers.

        Identifies the current installed version of program by running the following code in the terminal.
        'program --version'
        If version returned matches required version skips the task otherwise execute it as any other task.
        Prints to user as it goes along.
        """
    
    def _version_check_decorator(func):
        def _wrapper(self_of_decorated_method, *args, **kwargs):
            print(f"Checking \'{program}\' version ...")

            try:
                version_output = subprocess.check_output(f"{program} --version").decode()
                version_text = version_output.strip().replace("\n", f"\n{INDENT}")

                installed_version = re.search(VERSION_REGEX, version_text).group(1)
                print(f"Installed version: {installed_version}")
                _, latest_version = get_latest_version_in_dir(file_pattern=get_version_pattern(program))

                print(f"{INDENT}Installed version details:\n{INDENT}{version_text}")

                # try:
                # installed_version = get_version(version_text, VERSION_REGEX)
                if get_major_minor_patch(installed_version) == get_major_minor_patch(latest_version):
                    print(f"{INDENT}Matches required version ({latest_version}), skipping update task.")
                    return
                # except:
                #     print(f"{INDENT}Failed to extract version number from details.")
                #     raise Exception()

                print(f"{INDENT}The installed version appears to be different to required ({latest_version})")
                # func(self_of_decorated_method, *args, force=True, **kwargs)
                func(self_of_decorated_method, *args, **kwargs)
            except:
                print(f"{INDENT}Error occured while checking version, please continue manually.")
                func(self_of_decorated_method, *args, **kwargs)
        return _wrapper
    return _version_check_decorator

def get_version_pattern(program):
    if program == "java":
        return JAVA_INSTALLER_VERSION_REGEX
    elif program == "git":
        return GIT_INSTALLER_VERSION_REGEX
    raise Exception(f"No version pattern regex for program \"{program}\".")

def get_major_minor_patch(version: str):
    version_pattern = r"^([0-9]+(\.[0-9]+){0,2})(\.[0-9]+)?$"
    extracted = re.match(version_pattern, version).group(1)
    segments = extracted.count(".") + 1
    if segments < 3:
        extracted += ".0" * (3 - segments)
    return extracted


def get_latest_version_in_dir(path=THIRD_PARTY_INSTALLERS_LATEST_DIR, file_pattern=JAVA_INSTALLER_PATTERN):
    """
    Retrieves the latest version from the shares folder conforming to the regex pattern.

    Args:
        version_pattern: the regex that matches the installers version number as its first group.
    Returns:
        The latest version matching the regex on the shares.
    Raises:
        Exception: Raises exception if no matches were found.
    """
    logging.basicConfig(level=logging.DEBUG)

    # Get filenames in directory
    filenames = next(os.walk(path), (None, None, []))[2]  # [] if no file
    # Filter for relevant files matching regex
    filenames = [f for f in filenames if re.search(file_pattern, f)]
    file_paths = [os.path.join(path, f) for f in filenames]
    return get_latest_version(file_paths)

def get_latest_version(paths: List[str]):
    latest = max(paths, key=get_version_from_metadata)  # Comparing version strings works
    version = get_version_from_metadata(latest)
    return (latest, version)

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

def get_msi_property(path: str, property: str):
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

def get_version_from_metadata(path):
    """
    Reads the product version from file metadata.
    Currently supports .msi and .exe

    Args:
        path: The path to the file.
    """
    version = None
    if path.endswith(".msi"):
        version = get_msi_property(path, MSI_PRODUCT_VERSION_PROPERTY)
    elif path.endswith(".exe"):
        version = get_file_version(path)
    
    if version is None:
        raise Exception(f"Can't get version of {path}")
    return version
