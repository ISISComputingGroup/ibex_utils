"""
Tasks associated with install
"""

import os
import shutil
import socket
import subprocess
import git
import sys

from ibex_install_utils.exceptions import UserStop, ErrorInRun, ErrorInTask
from ibex_install_utils.file_utils import FileUtils

INSTRUMENT_BASE_DIR = os.path.join(r"c:\Instrument")
APPS_BASE_DIR = os.path.join(INSTRUMENT_BASE_DIR, "Apps")
EPICS_PATH = os.path.join(APPS_BASE_DIR, "EPICS")
GUI_PATH = os.path.join(APPS_BASE_DIR, "Client")
PYTHON_PATH = os.path.join(APPS_BASE_DIR, "Python")
EPICS_UTILS_PATH = os.path.join(APPS_BASE_DIR, "EPICS_UTILS")
DESKTOP_TRAINING_FOLDER_PATH = os.path.join(os.environ["userprofile"], "desktop", "Mantid+IBEX training")
SETTINGS_CONFIG_FOLDER = os.path.join("Settings", "config")
SETTINGS_CONFIG_PATH = os.path.join(INSTRUMENT_BASE_DIR, SETTINGS_CONFIG_FOLDER)
SOURCE_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
SOURCE_MACHINE_SETTINGS_CONFIG_PATH = os.path.join(SOURCE_FOLDER, SETTINGS_CONFIG_FOLDER, "NDXOTHER")
SOURCE_MACHINE_SETTINGS_COMMON_PATH = os.path.join(SOURCE_FOLDER, SETTINGS_CONFIG_FOLDER, "common")


class UpgradeTasks(object):
    """
    Class containing separate upgrade tasks.
    """

    def __init__(self, user_prompt, server_source_dir, client_source_dir, file_utils=FileUtils()):
        """
        Initializer.
        Args:
            user_prompt: a object to allow prompting of the user
            server_source_dir: directory to install ibex server from
            client_source_dir: directory to install ibex client from
            file_utils : collection of file utilities
        """
        self._prompt = user_prompt
        self._server_source_dir = server_source_dir
        self._client_source_dir = client_source_dir
        self._file_utils = file_utils

        self._machine_name = None

    def get_machine_name(self):
        """
        Finds the machine name

        Returns:

        """
        self._machine_name = socket.gethostname()

    def stop_ibex_server(self):
        """
        Stop the current IBEX server running. Current this can not be run because it kills any python
        processes including this one.

        Returns:

        """
        # with Task("Stopping IBEX server", self._prompt):
        #     RunProcess(EPICS_PATH, "stop_ibex_server.bat").run()
        pass

    def remove_old_ibex(self):
        """
        Removes older versions of IBEX server, client, genie_python and epics utils
        Returns:

        """
        with Task("Removing old version of IBEX", self._prompt) as task:
            if task.do_step:
                for path in (EPICS_PATH, PYTHON_PATH, GUI_PATH, EPICS_UTILS_PATH):
                    self._file_utils.delete_if_exists(path)

    def clean_up_desktop_ibex_training_folder(self):
        """
        Remove training folder from the desktop
        Returns:

        """
        with Task("Removing training folder on desktop ...", self._prompt) as task:
            if task.do_step:
                self._file_utils.delete_if_exists(DESKTOP_TRAINING_FOLDER_PATH)

    def remove_settings(self):
        """
        remove old settings
        Returns:

        """
        with Task("Removing old settings file", self._prompt) as task:
            if task.do_step:
                self._file_utils.delete_if_exists(SETTINGS_CONFIG_PATH)

    def install_settings(self):
        """
        Install new settings from the current folder
        Returns:

        """
        with Task("Install settings", self._prompt) as task:
            if task.do_step:
                self._file_utils.mkdir_recursive(SETTINGS_CONFIG_PATH)
                settings_path = os.path.join(SETTINGS_CONFIG_PATH, self._machine_name)

                shutil.copytree(SOURCE_MACHINE_SETTINGS_CONFIG_PATH, settings_path)

                inst_name = self._machine_name.lower()
                for p in ["ndx", "nde"]:
                    if inst_name.startswith(p):
                        inst_name = inst_name.lower()[len(p):]
                        break
                inst_name = inst_name.replace("-", "_")
                shutil.move(os.path.join(settings_path, "Python", "init_inst_name.py"),
                            os.path.join(settings_path, "Python", "init_{inst_name}.py".format(inst_name=inst_name)))

                shutil.copytree(SOURCE_MACHINE_SETTINGS_COMMON_PATH, os.path.join(SETTINGS_CONFIG_PATH, "common"))

    def upgrade_notepad_pp(self):
        """
        Install (start installation of) notepad ++
        Returns:

        """
        with Task("Upgrading Notepad++. Please follow system dialogs", self._prompt) as task:
            if task.do_step:
                RunProcess(working_dir=APPS_BASE_DIR,
                           executable_file="GUP.exe",
                           executable_directory=r"C:\Program Files (x86)\Notepad++\updater").run()

    def install_ibex_server(self, with_utils):
        """
        Install ibex server.
        Args:
            with_utils: True also install epics utils using icp binaries; False don't

        Returns:

        """
        with Task("Installing IBEX Server", self._prompt) as task:
            if task.do_step:
                self._file_utils.mkdir_recursive(APPS_BASE_DIR)
                RunProcess(self._server_source_dir, "install_to_inst.bat").run()
                if with_utils and self._prompt.confirm_step("install icp binaries"):
                    RunProcess(EPICS_PATH, "create_icp_binaries.bat").run()

    def install_ibex_client(self):
        """
        Install the ibex client (which also installs genie python).
        Returns:

        """
        with Task("Installing IBEX GUI", self._prompt) as task:
            if task.do_step:
                self._file_utils.mkdir_recursive(APPS_BASE_DIR)
                RunProcess(self._client_source_dir, "install_client.bat", press_any_key=True).run()

    def _start_ibex_server(self):
        """
        Start the ibex server. Can not do this because it would kill the current python process.
        Returns:

        """
        # with Task("Starting IBEX server..."):
        #    RunProcess(EPICS_PATH, "start_ibex_server.bat").run()
        pass

    def check_upgrade_testing_machine(self):
        """
        Print information about the current upgrade and prompt the user
        Returns:
        Raises UserStop: when the user doesn't want to continue

        """
        print("Upgrade {0} as a Training Machine".format(self._machine_name))
        print("    Server source: {0}".format(self._server_source_dir))
        print("    Client source: {0}".format(self._client_source_dir))
        answer = self._prompt.prompt("Continue? [Y/N]", ["Y", "N"], "Y")
        if answer != "Y":
            raise UserStop()

    def upgrade_instrument_configuration(self):
        with Task("Upgrading instrument configuration", self._prompt) as task:
            if task.do_step:
                sys.path.append('..')
                from upgrade import Upgrade, UPGRADE_STEPS
                from src.local_logger import LocalLogger
                from src.file_access import FileAccess

                try:
                    config_root = os.path.abspath(os.path.join(os.environ["ICPCONFIGROOT"], os.pardir))
                    log_dir = os.path.join(os.environ["ICPVARDIR"], "logs", "upgrade")
                except KeyError:
                    raise ErrorInTask("Must be run in a terminal that has done config_env")

                logger = LocalLogger(log_dir)
                file_access = FileAccess(logger, config_root)

                upgrade = Upgrade(file_access=file_access, logger=logger, upgrade_steps=UPGRADE_STEPS)
                upgrade.upgrade()

    def remove_seci_shortcuts(self):
        with Task("Remove SECI shortcuts", self._prompt) as task:
            if task.do_step:
                USER_START_MENU = os.path.join("C:\\", "users", "spudulike", "AppData", "Roaming", "Microsoft", "Windows", "Start Menu")
                PC_START_MENU = os.path.join("C:\\", "ProgramData", "Microsoft", "Windows", "Start Menu")
                SECI = "SECI User interface.lnk"
                AUTOSTART_LOCATIONS = [os.path.join(USER_START_MENU, "Programs", "Startup", SECI),
                                       os.path.join(PC_START_MENU, "Programs", "Startup", SECI)]

                for path in AUTOSTART_LOCATIONS:
                    if os.path.exists(path):
                        self._prompt.prompt_and_raise_if_not_yes("SECI autostart found in {}, delete this.".format(path))

                self._prompt.prompt_and_raise_if_not_yes("Remove task bar shortcut to SECI")
                self._prompt.prompt_and_raise_if_not_yes("Remove desktop shortcut to SECI")
                self._prompt.prompt_and_raise_if_not_yes("Remove start menu shortcut to SECI")

    def update_calibrations_repository(self):
        with Task("Updating calibrations repository", self._prompt) as task:
            if task.do_step:
                path = os.path.join("C:\\", "Instrument", "Settings", "Config", "common")
                try:
                    repo = git.Repo(path)
                    repo.git.pull()
                except git.GitCommandError:
                    self._prompt.prompt_and_raise_if_not_yes("There was an error pulling the calibrations repo.\n"
                                                             "Manually pull it. Path='{}'".format(path))


class UpgradeInstrument(object):
    """
    Class to upgrade the instrument installation to the given version of IBEX.
    """
    def __init__(self, user_prompt, server_source_dir, client_source_dir, file_utils=FileUtils()):
        """
        Initializer.
        Args:
            user_prompt: a object to allow prompting of the user
            server_source_dir: directory to install ibex server from
            client_source_dir: directory to install ibex client from
            file_utils : collection of file utilities
        """
        self._upgrade_tasks = UpgradeTasks(user_prompt, server_source_dir, client_source_dir, file_utils)

    def run_test_update(self):
        """
        Run a complete test upgrade on the current system
        Returns:

        """
        self._upgrade_tasks.get_machine_name()
        self._upgrade_tasks.check_upgrade_testing_machine()
        self._upgrade_tasks.stop_ibex_server()
        self._upgrade_tasks.remove_old_ibex()
        self._upgrade_tasks.clean_up_desktop_ibex_training_folder()
        self._upgrade_tasks.remove_settings()
        self._upgrade_tasks.install_settings()
        self._upgrade_tasks.install_ibex_server(True)
        self._upgrade_tasks.install_ibex_client()
        self._upgrade_tasks.upgrade_notepad_pp()

    def run_demo_upgrade(self):
        """
        Run an upgrade of Demo
        Returns:

        """
        self._upgrade_tasks.get_machine_name()
        self._upgrade_tasks.check_upgrade_testing_machine()
        self._upgrade_tasks.stop_ibex_server()
        self._upgrade_tasks.remove_old_ibex()
        self._upgrade_tasks.install_ibex_server(True)
        self._upgrade_tasks.install_ibex_client()
        self._upgrade_tasks.upgrade_notepad_pp()

    def run_instrument_update(self):
        self._upgrade_tasks.stop_ibex_server()
        self._upgrade_tasks.upgrade_instrument_configuration()
        self._upgrade_tasks.update_calibrations_repository()
        self._upgrade_tasks.remove_seci_shortcuts()


class Task(object):
    """
    Task to be performed for install.

    Confirms a step is to be run (if needed) and places the answer in do_step.
    Wraps the task in print statements so users can see when a task starts and ends.
    """

    def __init__(self, task_name, user_prompt):
        """
        Initialised.
        Args:
            task_name: the name of the task
            user_prompt: object allowing the user to be prompted for an answer
        """
        self._task = task_name
        self._user_prompt = user_prompt
        self.do_step = True

    def __enter__(self):
        self.do_step = self._user_prompt.confirm_step(self._task)
        print("{task} ...".format(task=self._task))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            print("... Done".format(task=self._task))


class RunProcess(object):
    """
    Create a process runner to run a process.
    """
    def __init__(self, working_dir, executable_file, executable_directory=None, press_any_key=False):
        """
        Create a process that needs running

        Args:
            working_dir: working directory of the process
            executable_file: file of the process to run, e.g. a bat file
            executable_directory: the directory in which the executable file lives, if None, default, use working dir
            press_any_key: if true then press a key to finish
        """
        self._working_dir = working_dir
        self._bat_file = executable_file
        self._press_any_key = press_any_key
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

            if self._press_any_key:
                output = subprocess.Popen([self._full_path_to_process_file], cwd=self._working_dir,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
                output_lines, err = output.communicate(" ")
            else:
                output_lines = subprocess.check_output(
                    [self._full_path_to_process_file],
                    cwd=self._working_dir,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE)

            for line in output_lines.splitlines():
                print("    , {line}".format(line=line))
            print("    ... finished")
        except subprocess.CalledProcessError as ex:
            raise ErrorInRun("Command failed with error: {0}".format(ex))
        except WindowsError as ex:
            if ex.errno == 2:
                raise ErrorInRun("Command '{cmd}' not found in '{cwd}'".format(
                    cmd=self._bat_file, cwd=self._working_dir))
            raise ex
