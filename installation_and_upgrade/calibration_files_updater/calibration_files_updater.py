"""
Script to update calibration files on instruments
"""

import sys
import git
import subprocess
import json
import logging
from genie_python import genie as g
from genie_python.utilities import dehex_and_decompress


class CalibrationsFolder(object):
    """
    Context manager for accessing calibration folders on remote instruments.
    """

    DRIVE_LETTER = "q"
    USERNAME = "gamekeeper"

    @staticmethod
    def disconnect_from_drive():
        """
        Returns: True if disconnect is successful, else False.
        """
        return subprocess.call(['net', 'use', '{}:'.format(CalibrationsFolder.DRIVE_LETTER), '/del', '/y']) == 0

    def connect_to_drive(self):
        """
        Returns: True if the connection is successful, else False
        """
        return subprocess.call(['net', 'use', '{}:'.format(CalibrationsFolder.DRIVE_LETTER), self.network_location,
                                '/user:{}'.format(self.username_with_domain), self.password]) == 0

    def __init__(self, instrument_host, password):
        self.username_with_domain = "{}\\{}".format(instrument_host, CalibrationsFolder.USERNAME)
        self.network_location = r'\\{}\c$\Instrument\Settings\config\common'.format(instrument_host)
        self.password = password

    def __enter__(self):
        """
        Returns: A git repository for the remote calibration folder if connection is successful, else None.
        """
        self.disconnect_from_drive()
        return git.Repo(self.network_location) if self.connect_to_drive() else None

    def __exit__(self, *args):
        self.disconnect_from_drive()


def get_instrument_hosts():
    """
    Returns: A collection of instrument host names
    """
    return (inst['hostName'] for inst in json.loads(dehex_and_decompress(g.get_pv("CS:INSTLIST"))))


def update_instrument(hosts, password, dry_run=False):
    """
    Updates the calibration files on the named host.

    Args:
        host: The instrument host to update
        password: The password to access the remote network location
        dry_run: Whether to do a read-only dry run

    Returns:
        Success: Whether the update completed successfully
    """
    success = False
    with CalibrationsFolder(host, password) as repo:
        if repo is None:
            pass
        elif "master" not in repo.git.branch():
            pass
        elif len(repo.git.diff()) > 0:
            pass
        elif dry_run:
            pass
            success = True
        else:
            try:
                repo.git.pull()
                success = True
            except git.GitCommandError as e:
               pass
    return success


if __name__ == "__main__":
    # Ask for this every time. We shouldn't store it in a public repo
    password = raw_input("Enter gamekeeper password: ")

    # Loop over all instruments
    failed_instruments = []
    for host in get_instrument_hosts():
        success = update_instrument(host, password, True)
        if not success:
            failed_instruments.append(host)

    # Report failures
    if len(failed_instruments) > 0:
        pass

    sys.exit(0)
