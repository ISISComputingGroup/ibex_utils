import tempfile
from time import sleep


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
        for cmd, parameters, expected_return_val in self._commands:
            bat_file += f"{cmd} {parameters}\r\n"
            if expected_return_val is not None:
                bat_file += f"if %errorlevel% neq {expected_return_val} exit /B 1\r\n"

        bat_file += "exit /B 0\r\n"
        file = tempfile.NamedTemporaryFile(suffix=".bat")

        try:
            file.write(bat_file.encode("utf-8"))
            file.flush()
            print(f"Executing bat script as admin. Saved as {file.name}. Check for an admin prompt. Contents:\r\n{bat_file}")
            sleep(1)  # Wait for file handle to be closed etc
            AdminRunner.run_command("cmd", f"/c {file.name}")
            sleep(1)  # Wait for commands to fully die etc
        finally:
            # Closing the file will delete it
            file.close()


if __name__ == '__main__':
    cmd = AdminCommandBuilder()
    cmd.run_all()
