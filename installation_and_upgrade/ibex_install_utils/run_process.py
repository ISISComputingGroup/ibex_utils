"""
Running processes infrastructure.
"""

import os
import subprocess
from typing import IO, List, Optional, Union

from ibex_install_utils.exceptions import ErrorInRun


class RunProcess:
    """
    Create a process runner to run a process.
    """

    def __init__(
        self,
        working_dir: Optional[Union[str, bytes, os.PathLike[str], os.PathLike[bytes]]],
        executable_file: str,
        executable_directory: Optional[
            Union[str, bytes, os.PathLike[str], os.PathLike[bytes]]
        ] = None,
        press_any_key: bool = False,
        prog_args: Optional[List[str]] = None,
        capture_pipes: bool = True,
        std_in: Optional[Union[int, IO]] = None,
        log_command_args: bool = True,
        expected_return_codes: Optional[Union[int, List[int]]] = None,
        capture_last_output: bool = False,
        progress_metric: Optional[List[str]] = None,
        env: dict | None = None,
    ) -> None:
        """
        Create a process that needs running

        Args:
            working_dir: working directory of the process
            executable_file: file of the process to run, e.g. a bat file
            executable_directory: the directory in which the executable file lives,
             if None, default, use working dir
            press_any_key: if true then press a key to finish the run process
            prog_args(list[string]): arguments to pass to the program
            capture_pipes: whether to capture pipes and manage in python or let the
             process access the console
            std_in: std_in sets the stdin pipe to be this
            log_command_args (bool): Whether to show the full command line that is being executed.
            expected_return_codes (int, None, List[int]): The expected return code for this command.
             Set it to None to disable return-code checking.
            capture_last_output: Whether to record the last console output of a command
            while pipes are captured.
            progress_metric: A list that is either empty if progress is
            not being calculated, or contains the output to
                count, the 100% value, and optionally a label for printing progress
            env: Environment variable mapping to pass to subprocess.POpen.
            Passing None inherits the parent process' environment.
        """
        self._working_dir = working_dir
        self._bat_file = executable_file
        self._press_any_key = press_any_key
        self._prog_args = prog_args
        self._capture_pipes = capture_pipes
        self._stdin = std_in
        self._capture_last_output = capture_last_output
        self.captured_output = ""
        self._progress_metric = progress_metric if progress_metric is not None else []
        self._env = env
        if isinstance(expected_return_codes, int):
            expected_return_codes = [expected_return_codes]
        self._expected_return_codes = (
            expected_return_codes if expected_return_codes is not None else [0]
        )
        self.log_command_args = log_command_args
        if std_in is not None and self._capture_pipes:
            raise NotImplementedError("Capturing pipes and set standard in is not implemented.")
        if executable_directory is None:
            self._full_path_to_process_file = os.path.join(working_dir, executable_file)
        else:
            self._full_path_to_process_file = os.path.join(executable_directory, executable_file)

    def run(self) -> None:
        """
        Run the process

        Returns:
        Raises ErrorInRun: if there is a known problem with the run
        """
        try:
            command_line = [self._full_path_to_process_file]
            if self._prog_args is not None:
                command_line.extend(self._prog_args)

            if self.log_command_args:
                print("    Running {} ...".format(" ".join(command_line)))
            else:
                print(f"    Running {self._bat_file} ... (command arguments hidden)")

            if not self._capture_pipes:
                if self._stdin:
                    error_code = subprocess.call(
                        command_line, cwd=self._working_dir, stdin=self._stdin
                    )
                else:
                    error_code = subprocess.call(command_line, cwd=self._working_dir)
                if (
                    self._expected_return_codes is not None
                    and error_code not in self._expected_return_codes
                ):
                    raise ErrorInRun(f"Command failed with error code: {error_code}")
            elif self._press_any_key:
                output = subprocess.Popen(
                    command_line,
                    cwd=self._working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    env=self._env,
                )
                output_lines, err = output.communicate(b" ")
                for line in output_lines.splitlines():
                    print(f"    > {line}")
                if (
                    self._expected_return_codes is not None
                    and output.returncode not in self._expected_return_codes
                ):
                    raise subprocess.CalledProcessError(output.returncode, command_line)
            else:
                process = subprocess.Popen(
                    command_line,
                    cwd=self._working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                )
                if len(self._progress_metric) < 2:
                    self.output_no_progress(process)
                else:
                    self.output_progress(process)
                process.stdout.close()
                return_code = process.wait()
                if (
                    self._expected_return_codes is not None
                    and return_code not in self._expected_return_codes
                ):
                    raise subprocess.CalledProcessError(return_code, command_line)

            print("    ... finished")
        except subprocess.CalledProcessError as ex:
            if ex.output:
                print(
                    f"Process failed with return code {ex.returncode}"
                    f" (expected {self._expected_return_codes}). "
                    f"Output was: "
                )
                for line in ex.output.splitlines():
                    print(f"    > {line}")
                print(" --- ")
            else:
                print(
                    f"Process failed with return code {ex.returncode}"
                    f" (expected {self._expected_return_codes}) "
                    f"and no output."
                )

            raise ErrorInRun(
                f"Command failed with return code {ex.returncode}"
                f" (expected {self._expected_return_codes})"
            )
        except WindowsError as ex:
            if ex.errno == 2:
                raise ErrorInRun(f"Command '{self._bat_file}' not found in '{self._working_dir}'")
            elif ex.errno == 22:
                raise ErrorInRun(
                    f"Directory not found to run command '{self._bat_file}',"
                    f" command is in :  '{self._working_dir}'"
                )
            raise ex

    def output_no_progress(self, process: subprocess.Popen) -> None:
        if process.stdout is None or process.stdout is None:
            raise Exception(f"No output from process {process}")
        for stdout_line in iter(process.stdout.readline, ""):
            print(f"    > {stdout_line}")
            if self._capture_last_output:
                self.captured_output = stdout_line

    def output_progress(self, process: subprocess.Popen) -> None:
        if process.stdout is None or process.stdout is None:
            raise Exception(f"No output from process {process}")
        count = 0
        label = ""
        if len(self._progress_metric) > 2:
            label = self._progress_metric[2]
        for stdout_line in iter(process.stdout.readline, ""):
            if self._progress_metric[1] in stdout_line:
                count = count + 1
                print(f"{label}{count}/{self._progress_metric[0]}")
