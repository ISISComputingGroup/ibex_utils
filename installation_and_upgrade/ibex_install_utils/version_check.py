"""
Third party program version checker infrastructure.
"""
import re
from ibex_install_utils.tasks.common_paths import THIRD_PARTY_INSTALLERS_LATEST_DIR
from ibex_install_utils.software import Software

VERSION_REGEX = r"\s([0-9]+\.[0-9]+(\.[0-9]+)+)"

JAVA_INSTALLER_PATTERN = r"^OpenJDK.*?([0-9.]*)_?[0-9]*.msi"
GIT_INSTALLER_PATTERN = r"^Git-([0-9.]*)-[0-9]*-bit.exe"
WIX_INSTALLER_PATTERN = r"^wix.*\.exe"

MSI_PRODUCT_VERSION_PROPERTY = "ProductVersion"

INDENT = "    "
    
def version_check(software: Software):
    """
        Decorator for tasks that check program version numbers.

        Identifies the current installed version of program by running the following code in the terminal.
        'program --version'
        If version returned matches required version skips the task otherwise execute it as any other task.
        Prints to user as it goes along.
        """
    
    def _version_check_decorator(func):
        def _wrapper(self_of_decorated_method, *args, **kwargs):
            print(f"Checking \'{software}\' version ...")
            try:
                installed_version = software.get_installed_version()
                print(f"Installed version: {installed_version}")
                _, latest_version = software.find_latest_installer()

                if get_major_minor_patch(installed_version) == get_major_minor_patch(latest_version):
                    print(f"{INDENT}Matches required version ({latest_version}), skipping update task.")
                    return

                print(f"{INDENT}The installed version appears to be different to required ({latest_version})")
                # func(self_of_decorated_method, *args, force=True, **kwargs)
                func(self_of_decorated_method, *args, **kwargs)
            except:
                print(f"{INDENT}Error occured while checking version, please continue manually.")
                func(self_of_decorated_method, *args, **kwargs)
        return _wrapper
    return _version_check_decorator


def get_major_minor_patch(version: str):
    version_pattern = r"^([0-9]+(\.[0-9]+){0,2})(\.[0-9]+)?$"
    extracted = re.match(version_pattern, version).group(1)
    segments = extracted.count(".") + 1
    if segments < 3:
        extracted += ".0" * (3 - segments)
    return extracted
