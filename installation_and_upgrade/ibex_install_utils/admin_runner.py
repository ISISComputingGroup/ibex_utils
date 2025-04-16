import contextlib
import os
import tempfile
from time import sleep
from typing import Any, Generator


class AdminRunner:
    @staticmethod
    def run_command(command: str, parameters: str, expected_return_val: int | None = 0) -> None:
        input(
            f"Manually run command: '{command} {parameters}' as administrator. "
            f"Press enter to confirm command listed above ran successfully in an admin prompt. "
            f"It should exit with status code {expected_return_val}"
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
