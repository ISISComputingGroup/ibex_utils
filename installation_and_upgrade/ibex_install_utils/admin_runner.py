import os
from time import sleep


class AdminRunner(object):
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

        print("Running command: '{} {}' as administrator".format(command, parameters))

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
            raise IOError("Process returned {} (expected {})".format(ret, expected_return_val))


class AdminCommandBuilder(object):
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
            bat_file += "{} {}\r\n".format(cmd, parameters)
            if expected_return_val is not None:
                bat_file += "if %errorlevel% neq {} exit / B 1\r\n".format(expected_return_val)

        bat_file += "exit /B 0\r\n"

        filename = os.path.join("C:\\", "Instrument", "temp.bat")
        with open(filename, "w") as f:
            f.write(bat_file)

        sleep(1)  # Wait for file handle to be closed etc
        AdminRunner.run_command("cmd", "/c {}".format(filename))
        sleep(1)  # Wait for commands to fully die etc
        os.remove(filename)