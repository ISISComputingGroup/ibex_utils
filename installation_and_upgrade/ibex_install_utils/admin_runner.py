import contextlib
import tempfile
from time import sleep
import os


class AdminRunner:
    @staticmethod
    def run_command(command, parameters, expected_return_val=0):
        try:
            from win32com.shell.shell import ShellExecuteEx
            from win32com.shell import shellcon
            import win32event
            import win32process
            import win32api
            import win32con
        except ImportError:
            raise OSError("Can only elevate privileges on windows")

        print(f"Running command: '{command} {parameters}' as administrator")

        process_info = ShellExecuteEx(
            nShow=win32con.SW_HIDE,
            fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
            lpVerb="runas",
            lpFile=command,
            lpParameters=parameters
        )

        win32event.WaitForSingleObject(process_info['hProcess'], 600000)
        ret = win32process.GetExitCodeProcess(process_info['hProcess'])
        win32api.CloseHandle(process_info['hProcess'])

        if ret != expected_return_val:
            raise IOError(f"Process returned {ret} (expected {expected_return_val})")


class AdminCommandBuilder:
    """
    Builder for running multiple commands sequentially as admin.
    """
    def __init__(self):
        self._commands = []

    def add_command(self, command, parameters, expected_return_val=0):
        self._commands.append((command, parameters, expected_return_val))

    def run_all(self):
        bat_file = ""

        log_file = tempfile.NamedTemporaryFile(mode="w+t", suffix=".log", delete=False)
        log_file.close()

        for cmd, parameters, expected_return_val in self._commands:

            bat_file += f"echo running command: {cmd} {parameters} >> {log_file.name} 2>&1\r\n"
            bat_file += f"{cmd} {parameters} >> {log_file.name} 2>&1\r\n"

            if expected_return_val is not None:
                bat_file += f"if %errorlevel% neq {expected_return_val} exit /B 1\r\n"

        bat_file += "exit /B 0\r\n"

        with temp_bat_file(bat_file) as f:
            print(f"Executing bat script as admin. Saved as {f}. Check for an admin prompt. Contents:\r\n{bat_file}")
            sleep(1)  # Wait for file handle to be closed etc
            try:
                AdminRunner.run_command("cmd", f"/c {f}", expected_return_val=0)
            except IOError as e:
                print(f"Error while executing bat script: {e}.")
                with open(log_file.name) as f:
                    for line in f.readlines():
                        print("bat script output: {}".format(line.rstrip()))
                raise
            sleep(1)  # Wait for commands to fully die etc


@contextlib.contextmanager
def temp_bat_file(contents):
    try:
        f = tempfile.NamedTemporaryFile(mode="w+t", suffix=".bat", delete=False)
        f.write(contents)
        f.close()
        yield f.name
    finally:
        os.remove(f.name)
