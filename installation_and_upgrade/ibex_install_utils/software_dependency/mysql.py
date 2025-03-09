import os
import re
import subprocess

from ibex_install_utils.file_utils import file_in_zip, get_version
from ibex_install_utils.software_dependency import SoftwareDependency
from ibex_install_utils.tasks.common_paths import APPS_BASE_DIR, INST_SHARE_AREA
from ibex_install_utils.version_check import VERSION_REGEX, get_major_minor_patch

MYSQL8_INSTALL_DIR = os.path.join(APPS_BASE_DIR, "MySQL")


class MySQL(SoftwareDependency):
    def get_name(self) -> str:
        return "MySQL"

    def get_installed_version(self) -> str:
        mysql_exe = os.path.join(MYSQL8_INSTALL_DIR, "bin", "mysql.exe")
        version_output = subprocess.check_output(f"{mysql_exe} --version").decode()
        installed_version = re.search(VERSION_REGEX, version_output).group(1)
        return get_major_minor_patch(installed_version)

    def get_file_pattern(self) -> str:
        return r"^mysql-.*-winx64\.zip"

    def get_version_of(self, path: str) -> str:
        filename, _ = os.path.splitext(os.path.basename(path))

        exe_within_zip = f"{filename}/bin/mysql.exe"
        with file_in_zip(path, exe_within_zip) as mysql_exe:
            return get_version(mysql_exe.name)

    def get_search_dir(self) -> str:
        return os.path.join(INST_SHARE_AREA, "kits$", "CompGroup", "ICP", "MySQL")
