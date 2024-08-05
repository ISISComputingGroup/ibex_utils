import re
import subprocess

from ibex_install_utils.file_utils import get_msi_property
from ibex_install_utils.software_dependency import SoftwareDependency
from ibex_install_utils.version_check import VERSION_REGEX, get_major_minor_patch


class Java(SoftwareDependency):
    def get_name(self) -> str:
        return "Java"

    def get_installed_version(self) -> str:
        version_output = subprocess.check_output("java --version").decode()
        installed_version = re.search(VERSION_REGEX, version_output).group(1)
        return get_major_minor_patch(installed_version)

    def get_file_pattern(self) -> str:
        return r"^OpenJDK.*?([0-9.]*)_?[0-9]*.msi"

    def get_version_of(self, path: str) -> str:
        return get_msi_property(path, "ProductVersion")
