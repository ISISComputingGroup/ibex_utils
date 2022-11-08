import os
import subprocess


FNULL = open(os.devnull, 'w')


def call_process(command: str, cwd : str=None) -> int:
    """
        Call a process.
        The 'subprocess' module uses the underlying file descriptor for output,
        bypassing 'sys.stdout/sys.stderr'.
        By using 'print' for output generated from the process,
        the 'ibex_install_utils.logger' Logger can be used to capture that output to a file.

        Args:
            command: command to call
            cwd: working directory to call the process in
        """
    print(f"Calling: {command}")

    process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for stdout_line in iter(process.stdout.readline, ""):
        print(f"    {stdout_line}", end="")
    process.stdout.close()
    return process.wait()
