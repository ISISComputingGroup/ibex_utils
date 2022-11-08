from _typeshed import StrOrBytesPath
import os
import subprocess


FNULL = open(os.devnull, 'w')


def call_process(args: list[str], cwd : StrOrBytesPath=None, capture_output=True, log_args=True) -> int:
    """
        Call a process.
        The 'subprocess' module uses the underlying file descriptor for output,
        bypassing 'sys.stdout/sys.stderr'.
        By using 'print' for output generated from the process,
        the 'ibex_install_utils.logger' Logger can be used to capture that output to a file.

        Args:
            args: arguments to call
            cwd: working directory to call the process in
            capture_output: whether to capture output from the process
            log_args: whether to show the full command being executed or just the process
        """
    if log_args:
        print(f"Calling: {' '.join(args)}")
    else:
        print(f"Calling: {args[0]} (arguments hidden)")

    if capture_output:
        process = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for stdout_line in iter(process.stdout.readline, ""):
            print(f"    {stdout_line}", end="")
        process.stdout.close()
        return process.wait()
    else:
        return subprocess.call(args=args, cwd=cwd, stdout=FNULL, stderr=FNULL)
