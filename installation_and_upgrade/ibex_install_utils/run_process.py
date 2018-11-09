"""
Running processes infrastructure.
"""

import os
import subprocess
import traceback

from ibex_install_utils.exceptions import ErrorInRun


class RunProcess(object):
    """
    Create a process runner to run a process.
    """
    def __init__(self, working_dir, executable_file, executable_directory=None, press_any_key=False, prog_args=None,
                 capture_pipes=True):
        """
        Create a process that needs running

        Args:
            working_dir: working directory of the process
            executable_file: file of the process to run, e.g. a bat file
            executable_directory: the directory in which the executable file lives, if None, default, use working dir
            press_any_key: if true then press a key to finish the run process
            prog_args(list[string]): arguments to pass to the program
            capture_pipes: whether to capture pipes and manage in python or let the process access the console
        """
        self._working_dir = working_dir
        self._bat_file = executable_file
        self._press_any_key = press_any_key
        self._prog_args = prog_args
        self._capture_pipes = capture_pipes
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
            print("    Running {0} ...".format(self._bat_file))

            command_line = [self._full_path_to_process_file]
            if self._prog_args is not None:
                command_line.extend(self._prog_args)

            if not self._capture_pipes:
                error_code = subprocess.call(command_line, cwd=self._working_dir)
                if error_code != 0:
                    raise ErrorInRun("Command failed with error code: {0}".format(error_code))
                output_lines = ""
            elif self._press_any_key:
                output = subprocess.Popen(command_line, cwd=self._working_dir,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
                output_lines, err = output.communicate(" ")
            else:
                output_lines = subprocess.check_output(
                    command_line,
                    cwd=self._working_dir,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE)

            for line in output_lines.splitlines():
                print("    > {line}".format(line=line))
            print("    ... finished")
        except subprocess.CalledProcessError as ex:
            traceback.print_exc()
            raise ErrorInRun("Command failed with error: {0}".format(ex))
        except WindowsError as ex:
            if ex.errno == 2:
                raise ErrorInRun("Command '{cmd}' not found in '{cwd}'".format(
                    cmd=self._bat_file, cwd=self._working_dir))
            elif ex.errno == 22:
                raise ErrorInRun("Directory not found to run command '{cmd}', command is in :  '{cwd}'".format(
                    cmd=self._bat_file, cwd=self._working_dir))
            raise ex
