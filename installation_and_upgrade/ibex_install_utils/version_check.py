"""
Third party program version checker infrastructure.
"""
import subprocess
import re
from os import walk
from ibex_install_utils.tasks.common_paths import THIRD_PARTY_INSTALLERS_LATEST_DIR

JAVA_INSTALLER_VERSION_REGEX = r"^OpenJDK.*?([0-9.]*)_?[0-9]*.msi"
GIT_INSTALLER_VERSION_REGEX = r"^Git-([0-9.]*)-[0-9]*-bit.exe"
VERSION_REGEX = r"\s([0-9]+\.[0-9]+(\.[0-9]+)+)"

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
                version = latest_version_shares(get_version_pattern(program))

                print(f"{INDENT}Installed version details:\n{INDENT}{version_text}")

                try:
                    installed_version = get_version(version_text, VERSION_REGEX)
                    if installed_version == version:
                        print(f"{INDENT}Matches required version ({version}), skipping update task.")
                        return
                except:
                    print(f"{INDENT}Failed to extract version number from details.")
                    raise Exception()

                print(f"{INDENT}The installed version appears to be different to required ({version})")
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

def compare_versions(v1, v2):
    """
    Compare two version numbers of th format x.x.x
    Return: True if v2 represents a higher version compared to 1, False otherwise
    """
    v1_no_dots = v1.replace(".", "")
    v2_no_dots = v2.replace(".", "")
    diff = len(v1_no_dots) - len(v2_no_dots)
    if diff < 0:
        v1_no_dots += "0" * -diff
    elif diff > 0:
        v2_no_dots += "0" * diff

    return int(v1_no_dots) < int(v2_no_dots)

def get_version(filename, pattern):
    """
    Args:
        filename: The filename string.
        pattern: The regex pattern to retrieve version number as first group.
    Returns:
        The version number string found based on the pattern.
    Raises:
        Exception: If filename does not match regex pattern.
    """
    result = re.search(pattern, filename)
    if result:
        return result.group(1)
    else:
        raise Exception(f"Filename \"{filename}\" does not match regex \"{pattern}\".")

def latest_version_shares(version_pattern=JAVA_INSTALLER_VERSION_REGEX):
    """
    Retrieves the latest version from the shares folder conforming to the regex pattern.

    Args:
        version_pattern: the regex that matches the installers version number as its first group.
    Returns:
        The latest version matching the regex on the shares.
    Raises:
        Exception: Raises exception if no matches were found.
    """
    filenames = next(walk(THIRD_PARTY_INSTALLERS_LATEST_DIR), (None, None, []))[2]  # [] if no file
    latest = ""

    for filename in filenames:
        try:
            version = get_version(filename, version_pattern)
            if compare_versions(latest, version):
                latest = version
        except:
            continue
    if len(latest) > 0:
        return latest
    else:
        raise Exception("Can't find any version matching the pattern \"" + version_pattern + "\" on the shares")
