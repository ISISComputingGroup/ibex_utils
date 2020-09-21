"""
Running processes infrastructure.
"""

import os
import subprocess

from installation_and_upgrade.ibex_install_utils.exceptions import ErrorInRun


class RunProcess:
    """
    Create a process runner to run a process.
    """
    def __init__(self, working_dir, executable_file, executable_directory=None, press_any_key=False, prog_args=None,
                 capture_pipes=True, std_in=None, log_command_args=True):
        """
        Create a process that needs running

        Args:
            working_dir: working directory of the process
            executable_file: file of the process to run, e.g. a bat file
            executable_directory: the directory in which the executable file lives, if None, default, use working dir
            press_any_key: if true then press a key to finish the run process
            prog_args(list[string]): arguments to pass to the program
            capture_pipes: whether to capture pipes and manage in python or let the process access the console
            std_in: std_in sets the stdin pipe to be this
            log_command_args (bool): Whether to show the full command line that is being executed.
        """
        self._working_dir = working_dir
        self._bat_file = executable_file
        self._press_any_key = press_any_key
        self._prog_args = prog_args
        self._capture_pipes = capture_pipes
        self._stdin = std_in
        self.log_command_args = log_command_args
        if std_in is not None and self._capture_pipes:
            raise NotImplementedError("Capturing pipes and set standard in is not implemented.")
        if executable_directory is None:
            self._full_path_to_process_file = os.path.join(working_dir, executable_file)
        else:
            self._full_path_to_process_file = os.path.join(executable_directory, executable_file)

    def run(self):
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
                    error_code = subprocess.call(command_line, cwd=self._working_dir, stdin=self._stdin)
                else:
                    error_code = subprocess.call(command_line, cwd=self._working_dir)
                if error_code != 0:
                    raise ErrorInRun(f"Command failed with error code: {error_code}")
            elif self._press_any_key:
                output = subprocess.Popen(command_line, cwd=self._working_dir,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
                output_lines, err = output.communicate(" ")

                for line in output_lines.splitlines():
                    print(f"    > {line}")
            else:
                process = subprocess.Popen(command_line, cwd=self._working_dir,
                                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           universal_newlines=True)
                for stdout_line in iter(process.stdout.readline, ""):
                    print(f"    > {stdout_line}")
                process.stdout.close()
                return_code = process.wait()
                if return_code:
                    raise subprocess.CalledProcessError(return_code, command_line)

            print("    ... finished")
        except subprocess.CalledProcessError as ex:
            if ex.output:
                print(f"Process failed with return code {ex.returncode}. Output was: ")
                for line in ex.output.splitlines():
                    print(f"    > {line}")
                print(" --- ")
            else:
                print(f"Process failed with return code {ex.returncode} and no output.")

            raise ErrorInRun(f"Command failed with return code {ex.returncode}")
        except WindowsError as ex:
            if ex.errno == 2:
                raise ErrorInRun(f"Command '{self._bat_file}' not found in '{self._working_dir}'")
            elif ex.errno == 22:
                raise ErrorInRun(f"Directory not found to run command '{self._bat_file}', command is in :  '{self._working_dir}'")
            raise ex
