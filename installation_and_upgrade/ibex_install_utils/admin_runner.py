import contextlib
import getpass
import os
import socket
import subprocess
import tempfile
from time import sleep
from typing import Any, Generator

from ibex_install_utils.logger import temporarily_disable_logging

# Plink is an SSH binary bundled with putty.
# Use Plink as it allows passwords on the command-line, as opposed to
# windows-bundled SSH which does not.
PLINK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plink.exe")
SSH_HOST = "localhost"


def ssh_available() -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((SSH_HOST, 22))
    sock.close()
    return result == 0


class AdminRunner:
    _ssh_user = None
    _ssh_password = None
    _ssh_authenticated = False

    @classmethod
    def _auth_ssh(cls) -> None:
        if not cls._ssh_authenticated:
            while True:
                with temporarily_disable_logging():
                    cls._ssh_user = input("Enter admin username (without domain): ")
                    cls._ssh_password = getpass.getpass("Enter admin password: ")

                assert cls._ssh_user is not None
                assert cls._ssh_password is not None

                test_output = subprocess.run(
                    [
                        PLINK,
                        "-ssh",
                        "-pw",
                        cls._ssh_password,
                        f"{cls._ssh_user}@{SSH_HOST}",
                        "net session",  # Will only work if got admin rights
                    ],
                    shell=True,
                )
                if test_output.returncode == 0:
                    cls._ssh_authenticated = True
                    break
                print("SSH credentials were incorrect. Try again.")

    @classmethod
    def _run_command_ssh(cls, command: str, parameters: str) -> int:
        cls._auth_ssh()

        assert cls._ssh_user is not None
        assert cls._ssh_password is not None

        out = subprocess.run(
            [
                PLINK,
                "-ssh",
                "-batch",
                "-pw",
                cls._ssh_password,
                f"{cls._ssh_user}@{SSH_HOST}",
                f"{command} {parameters}",
            ],
            shell=True,
        )
        return out.returncode

    @classmethod
    def run_command(
        cls, command: str, parameters: str, expected_return_val: int | None = 0
    ) -> None:
        if ssh_available():
            return_value = cls._run_command_ssh(command, parameters)
            if return_value != expected_return_val:
                raise ValueError(
                    f"Command failed; expected return "
                    f"value {expected_return_val}, got {return_value}"
                )
        else:
            input(
                f"Manually run in an admin terminal:\n\n{command} {parameters}\n\n"
                f"Press enter when done. "
                f"Return value should be {expected_return_val}."
            )


class AdminCommandBuilder:
    """
    Builder for running multiple commands sequentially as admin.
    """

    def __init__(self) -> None:
        self._commands: list[tuple[str, str, int | None]] = []

    def add_command(
        self, command: str, parameters: str, expected_return_val: int | None = 0
    ) -> None:
        self._commands.append((command, parameters, expected_return_val))

    def run_all(self) -> str:
        bat_file = ""

        log_file = tempfile.NamedTemporaryFile(mode="w+t", suffix=".log", delete=False)
        log_file.close()

        for cmd, parameters, expected_return_val in self._commands:
            bat_file += f"echo ### COMMAND: {cmd} {parameters} >> {log_file.name} 2>&1\r\n"
            bat_file += f"{cmd} {parameters} >> {log_file.name} 2>&1\r\n"

            if expected_return_val is not None:
                bat_file += f"if %errorlevel% neq {expected_return_val} exit /B 1\r\n"

        bat_file += "exit /B 0\r\n"

        comspec = os.getenv("COMSPEC", "cmd.exe")
        with temp_bat_file(bat_file) as f:
            print(
                f"Executing bat script as admin. Saved as {f}. Check for an admin prompt. "
                f"Log at {log_file.name}."
            )
            sleep(1)  # Wait for file handle to be closed etc
            try:
                AdminRunner.run_command(f"{comspec}", f"/c {f}", expected_return_val=0)
            except IOError as e:
                print(f"Error while executing bat script: {e}.")
                with open(log_file.name, "r") as logfile:
                    for line in logfile.readlines():
                        print("bat script output: {}".format(line.rstrip()))
                raise
            sleep(1)  # Wait for commands to fully die etc

        return log_file.name


@contextlib.contextmanager
def temp_bat_file(contents: str) -> Generator[str, None, Any]:
    f = tempfile.NamedTemporaryFile(mode="w+t", suffix=".bat", delete=False)
    try:
        f.write(contents)
        f.close()
        yield f.name
    finally:
        os.remove(f.name)
