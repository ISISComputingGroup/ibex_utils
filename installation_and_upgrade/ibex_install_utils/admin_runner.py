import os

import sys
from six.moves import input


class AdminRunner(object):
    def __init__(self):
        self._admin_username = input("Admin user account: ")

        while not self._password_correct():
            print("Incorrect username/password provided to AdminRunner. Try again:")
            self._admin_username = input("Admin user account: ")

    def _password_correct(self):
        """
        Spawn a command purely to ensure the username/password are valid.

        /savecred should mean we only need to input password once...?
        """
        return os.system('runas /noprofile /user:{} /savecred "cmd /c echo OK"'.format(self._admin_username)) == 0

    def run_bat(self, bat_line):
        """
        Runs a single line of a batch file as an administrator.

        Args:
            bat_line: (str) The line to run in the cmd interpreter as admin
        Returns:
            Exit code of the process
        """
        return os.system('runas /noprofile /user:{} /savecred "cmd /c {}"'.format(self._admin_username, bat_line))

    def run_py_command(self, py_line):
        """
        Runs a single line of python as an administrator.

        Args:
            py_line: (str) The line of python to run as admin
        Returns:
            Exit code of the process
        """
        return self.run_bat('{} -c \\"{}\\"'.format(sys.executable, py_line))
