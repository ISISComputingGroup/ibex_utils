import os
import re
from abc import ABC, abstractmethod

from ibex_install_utils.tasks.common_paths import THIRD_PARTY_INSTALLERS_LATEST_DIR


class SoftwareDependency(ABC):
    """
    Represents a software dependency installed on the system.
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        Return user friendly name of the software.
        """
        ...

    @abstractmethod
    def get_installed_version(self) -> str:
        """
        Return the installed version of the software.
        """
        ...

    @abstractmethod
    def get_file_pattern(self) -> str:
        """
        Return the regex to match the files describing different versions of this software.
        """
        ...

    @abstractmethod
    def get_version_of(self, path: str) -> str:
        """
        Return the version of the software dependency described by the path.

        Args:
            path: The path to the dir/file.
        """
        ...

    def get_search_dir(self) -> str:
        """
        Return the path to the directory containing the available versions of the software.
        """
        return THIRD_PARTY_INSTALLERS_LATEST_DIR

    def find_available(self) -> list[str]:
        """
        Return a list of paths pointing to the available versions of this software on the system.
        """
        # Get filenames in directory
        filenames = next(os.walk(self.get_search_dir()), (None, None, []))[2]  # [] if no file
        # Filter for relevant files matching regex
        filenames = [f for f in filenames if re.search(self.get_file_pattern(), f)]
        file_paths = [os.path.join(self.get_search_dir(), f) for f in filenames]

        return file_paths

    def find_latest(self) -> tuple[str, str]:
        """
        Return a tuple of (dependency_file, version)
        where the dependency_file points to the location describing the latest version of the software
        and the version is the version of this dependency.
        """
        installer_paths = self.find_available()
        # Compare versions
        latest_installer = installer_paths[0]
        latest_version = self.get_version_of(latest_installer)
        for installer in installer_paths:
            v = self.get_version_of(installer)
            # TODO do some logging

            if is_higher(latest_version, v):
                latest_installer = installer
                latest_version = v
        # The following did not always work, because it only takes major minor patch into consideration.
        # latest = max(installer_paths, key=lambda path : int(get_major_minor_patch(self.get_installer_version(path)).replace(".", "")))
        return (latest_installer, latest_version)


def is_higher(v1, v2):
    """
    Returns True if v2 represents a higher version than v1.
    """
    segments1 = v1.split(".")
    segments2 = v2.split(".")
    maxSegments = max(len(segments1), len(segments2))

    for i in range(maxSegments):
        s1, s2 = 0, 0
        try:
            s1 = int(segments1[i])
        except:
            s1 = 0

        try:
            s2 = int(segments2[i])
        except:
            s2 = 0

        if s1 < s2:
            return True
        elif s1 > s2:
            return False
    return False
