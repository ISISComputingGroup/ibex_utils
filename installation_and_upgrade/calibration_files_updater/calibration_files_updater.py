"""
Script to update calibration files on instruments
"""

import sys
import git
import subprocess
from genie_python import genie as g
from genie_python.utilities import dehex_and_decompress
import json

USERNAME = "gamekeeper"


class CalibrationsFolder(object):

    DRIVE_LETTER = "q"

    @staticmethod
    def disconnect_from_drive():
        return subprocess.call(['net', 'use', '{}:'.format(CalibrationsFolder.DRIVE_LETTER), '/del', '/y'])

    def connect_to_drive(self):
        username = self.username
        password = PASSWORD
        folder = self.network_location
        command = r'net use {drive}: {folder} /user:{user} {password}'.format(
            drive=CalibrationsFolder.DRIVE_LETTER, folder=self.network_location,
            user=self.username, password=PASSWORD)
        print("Connecting to {}, user: {}, password: {}, command: {}".format(folder, username, password, command))
        return subprocess.call(['net', 'use', '{}:'.format(CalibrationsFolder.DRIVE_LETTER), folder,
                         '/user:{}'.format(username), PASSWORD])

    def __init__(self, instrument_host):
        self.username = "{}\\{}".format(instrument_host, USERNAME)
        self.network_location = r'\\{}\c$\Instrument\Settings\config\common'.format(instrument_host)

    def __enter__(self):
        self.disconnect_from_drive()
        if self.connect_to_drive()==0:
            return self.network_location
        else:
            return None

    def __exit__(self, *args):
        self.disconnect_from_drive()


def get_instruments():
    return [inst['hostName'] for inst in json.loads(dehex_and_decompress(g.get_pv("CS:INSTLIST")))]


def update_all_instruments(dry_run):
    for host in get_instruments():
        with CalibrationsFolder(host) as f:
                if f is None:
                    print("Unable to connect")
                else:
                    repo = git.Repo(f)
                    if "master" not in repo.git.branch() or len(repo.git.diff()) > 0:
                        print("Calibrations folder not clean...")
                        print("master" not in repo.git.branch(), repo.git.branch())
                        print(len(repo.git.diff()), repo.git.diff())
                    else:
                        if dry_run:
                            print("This is where I would update {}".format(host))
                        else:
                            try:
                                repo.git.pull()
                            except git.GitCommandError as e:
                                print("Error doing pull...")


if __name__ == "__main__":
    PASSWORD = raw_input("Enter gamekeeper password: ")
    update_all_instruments(True)
    sys.exit(0)
