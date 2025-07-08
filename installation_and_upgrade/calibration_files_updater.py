"""
Script to update calibration files on instruments
"""

import getpass
import json
import logging
import os
import subprocess

import git
from six.moves import input
from ibex_install_utils.file_utils import FileUtils
from epics import caget

FNULL = open(os.devnull, "w")


class CalibrationsFolder:
    """
    Context manager for accessing calibration folders on remote instruments.
    """

    DRIVE_LETTER = "q"

    @staticmethod
    def disconnect_from_drive():
        """
        Returns: True if disconnect is successful, else False.
        """
        return (
            subprocess.call(
                ["net", "use", f"{CalibrationsFolder.DRIVE_LETTER}:", "/del", "/y"],
                stdout=FNULL,
                stderr=FNULL,
            )
            == 0
        )

    def connect_to_drive(self):
        """
        Returns: True if the connection is successful, else False
        """
        return (
            subprocess.call(
                [
                    "net",
                    "use",
                    f"{CalibrationsFolder.DRIVE_LETTER}:",
                    self.network_location,
                    f"/user:{self.username_with_domain}",
                    self.password,
                ],
                stdout=FNULL,
                stderr=FNULL,
            )
            == 0
        )

    def __init__(self, instrument_host, username, password):
        self.username_with_domain = f"{instrument_host}\\{username}"
        self.network_location = r"\\{}\c$\Instrument\Settings\config\common".format(instrument_host)
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
    return (inst["hostName"] for inst in json.loads(FileUtils.dehex_and_decompress(caget("CS:INSTLIST").tobytes().decode().rstrip('\x00'))))


def update_instrument(host, username, password, logger, dry_run=False):
    """
    Updates the calibration files on the named host.

    Args:
        host: The instrument host to update
        username: The username to access the remote network location
        password: The password to access the remote network location
        logger: Handles log messages
        dry_run: Whether to do a read-only dry run

    Returns:
        Success: Whether the update completed successfully
    """
    logging.info(f"Updating {host}")
    success = False
    with CalibrationsFolder(host, username, password) as repo:
        if repo is None:
            logger.warning(f"Unable to connect to host, {host}")
        elif "master" not in repo.git.branch():
            logger.warning(f"The calibrations folder on {host} does not point at the master branch")
        elif len(repo.git.diff()) > 0:
            logger.warning(f"The calibrations folder on {host} has uncommitted changes")
        elif dry_run:
            logger.info(
                f"{host} has passed all status checks, but not updated as this is a dry run"
            )
            success = True
        else:
            try:
                logger.info(f"Performing git pull on {host}")
                repo.git.pull()
                logger.info("Pull successful")
                success = True
            except git.GitCommandError as e:
                logger.error(f"Git pull on {host} failed with error: {e}")
    return success


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", level=logging.INFO)
    logger = logging.getLogger("main")

    # Get user credentials, don't store in the repo
    username = input("Enter username (no domain): ")
    password = getpass.getpass("Enter gamekeeper password: ")

    # Is this a dry run?
    dry_run_raw = input("Is this a dry run [Y/N]? ").upper()
    while dry_run_raw not in ["Y", "N"]:
        dry_run_raw = input("Invalid response, try again. Is this a dry run [Y/N]? ").upper()
    dry_run = dry_run_raw == "Y"

    # Update the instruments
    results = dict()
    for host in get_instrument_hosts():
        results[host] = update_instrument(host, username, password, logger, dry_run)

    # Report
    failed_instruments = [host for host in results.keys() if not results[host]]
    successful_instruments = [host for host in results.keys() if results[host]]
    if len(successful_instruments) > 0:
        logger.warning(
            "The following instruments were updated successfully: "
            + ", ".join(successful_instruments)
        )
    if len(failed_instruments) > 0:
        logger.warning(
            "The following instruments could not be updated. Please do them by hand: "
            + ", ".join(failed_instruments)
        )
