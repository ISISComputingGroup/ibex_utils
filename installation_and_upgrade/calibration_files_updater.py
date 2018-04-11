"""
Script to update calibration files on instruments
"""

import sys
import git
import subprocess
import json
import logging
import os
import hashlib
from genie_python import genie as g
from genie_python.utilities import dehex_and_decompress

FNULL = open(os.devnull, 'w')

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
        return subprocess.call(['net', 'use', '{}:'.format(CalibrationsFolder.DRIVE_LETTER), '/del', '/y'],
                               stdout=FNULL, stderr=FNULL) == 0

    def connect_to_drive(self):
        """
        Returns: True if the connection is successful, else False
        """
        return subprocess.call(['net', 'use', '{}:'.format(CalibrationsFolder.DRIVE_LETTER), self.network_location,
                                '/user:{}'.format(self.username_with_domain), self.password],
                               stdout=FNULL, stderr=FNULL) == 0

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


def update_instrument(host, password, logger, dry_run=False):
    """
    Updates the calibration files on the named host.

    Args:
        host: The instrument host to update
        password: The password to access the remote network location
        logger: Handles log messages
        dry_run: Whether to do a read-only dry run

    Returns:
        Success: Whether the update completed successfully
    """
    logging.info("Updating {}".format(host))
    success = False
    with CalibrationsFolder(host, password) as repo:
        if repo is None:
            logger.warning("Unable to connect to host, {}".format(host))
        elif "master" not in repo.git.branch():
            logger.warning("The calibrations folder on {} does not point at the master branch".format(host))
        elif len(repo.git.diff()) > 0:
            logger.warning("The calibrations folder on {} has uncommitted changes".format(host))
        elif dry_run:
            logger.info("{} has passed all status checks, but not updated as this is a dry run".format(host))
            success = True
        else:
            try:
                logger.info("Performing git pull on {}".format(host))
                repo.git.pull()
                logger.info("Pull successful")
                success = True
            except git.GitCommandError as e:
                logger.error("Git pull on {} failed with error: {}".format(host, e))
    return success


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
    logger = logging.getLogger("main")

    # We shouldn't store the password in the repo, but we don't want to proceed with an incorrect password.
    # Store a hash and compare
    expected_hash = "51b0250c33fafc86dc69ab4335ca7c885a141c6d4ab1401962d35f3fa7384558"
    password = raw_input("Confirm gamekeeper password: ")
    while not hashlib.sha256(password).hexdigest() == expected_hash:
        password = raw_input("Password incorrect, please try again: ")

    # Loop over all instruments
    results = dict()

    # Is this a dry run?
    dry_run_raw = raw_input("Is this a dry run [Y/N]? ").upper()
    while dry_run_raw not in ["Y", "N"]:
        raw_input("Invalid response, try again. Is this a dry run [Y/N]? ").upper()
    dry_run = dry_run_raw == "Y"

    # Update the instruments
    for host in get_instrument_hosts():
        results[host] = update_instrument(host, password, logger, dry_run)

    # Report
    failed_instruments = (host for host in results.keys() if not results[host])
    successful_instruments = (host for host in results.keys() if results[host])
    if len(failed_instruments) > 0:
        logger.warning("The following instruments could not be updated. Please do them by hand: " +
                       ", ".join(failed_instruments))
    if len(successful_instruments) > 0:
        logger.warning("The following instruments were updated successfully: " + ", ".join(successful_instruments))

    sys.exit(0)