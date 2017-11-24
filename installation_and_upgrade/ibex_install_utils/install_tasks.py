"""
Tasks associated with install
"""

import os
import shutil
import socket
import subprocess
import git
import sys
from datetime import date

from ibex_install_utils.exceptions import UserStop, ErrorInRun, ErrorInTask
from ibex_install_utils.file_utils import FileUtils

INSTRUMENT_BASE_DIR = os.path.join("C:\\", "Instrument")
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

        self._machine_name = self._get_machine_name()

    @staticmethod
    def _get_machine_name():
        """
        Returns:
            The current machine name

        """
        return socket.gethostname()

    @staticmethod
    def _get_instrument_name():
        """
        Returns:
            The name of the current instrument
        """
        return UpgradeTasks._get_machine_name().replace("NDX", "")

    @staticmethod
    def _get_config_path():

        """
        Returns:
            The path to the instrument's configurations directory

        """
        return os.path.join(INSTRUMENT_BASE_DIR, SETTINGS_CONFIG_FOLDER, UpgradeTasks._get_machine_name())

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
                    self._file_utils.remove_tree(path)

    def clean_up_desktop_ibex_training_folder(self):
        """
        Remove training folder from the desktop
        Returns:

        """
        with Task("Removing training folder on desktop ...", self._prompt) as task:
            if task.do_step:
                self._file_utils.remove_tree(DESKTOP_TRAINING_FOLDER_PATH)

    def remove_settings(self):
        """
        remove old settings
        Returns:

        """
        with Task("Removing old settings file", self._prompt) as task:
            if task.do_step:
                self._file_utils.remove_tree(SETTINGS_CONFIG_PATH)

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

    def _start_ibex_gui(self):
        """
        Start the IBEX GUI
        :return:
        """
        subprocess.Popen([os.path.join(GUI_PATH, "ibex-client.exe")])


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

    def install_java(self):
        with Task("Install java", self._prompt) as task:
            if task.do_step:
                java_url = "http://www.java.com/en/"
                java_installed = subprocess.call(["java","-version"]) == 0
                if java_installed:
                    self._prompt.prompt_and_raise_if_not_yes(
                        "Confirm that the java version above is the desired version or that you have "
                        "upgraded to the desired 64-bit version from {}".format(java_url))
                else:
                    self._prompt.prompt_and_raise_if_not_yes(
                        "Java is not installed. Please go to {}, then download and install "
                        "the desired 64-bit version".format(java_url))
                self._prompt.prompt_and_raise_if_not_yes(
                    "Is auto-update turned off? This can be checked from the Java control panel in "
                    "C:\\Program Files\\Java\\jre\\bin\\javacpl.exe")

    def take_screenshots(self):
        with Task("Take screenshots", self._prompt) as task:
            if task.do_step:
                self._prompt.prompt_and_raise_if_not_yes(
                    "Take screenshots of the current IBEX setup for future reference. These should include:\n"
                    "- Client and server versions\n"
                    "- Blocks\n"
                    "- Major perspectives\n"
                    "- Current configuration tabs\n"
                    "- Running IOCs\n"
                    "- Available configs\n"
                    "- Any open LabView VIs")

    @staticmethod
    def _get_backup_dir():
        new_backup_dir = os.path.join("C:\\", "data", "old", "ibex_backup_{}".format(date.today().strftime("%Y_%m_%d")))
        if not os.path.exists(new_backup_dir):
            os.mkdir(new_backup_dir)
        return new_backup_dir

    def _backup_dir(self, src, copy=True):
        backup_dir = os.path.join(self._get_backup_dir(), os.path.basename(src))
        if src in os.getcwd():
            self._prompt.prompt_and_raise_if_not_yes(
                "You appear to be trying to delete the folder, {}, containing the current working directory {}. "
                "Please do this manually to be on the safe side".format(src, os.getcwd()))
        elif os.path.exists(backup_dir):
            self._prompt.prompt_and_raise_if_not_yes(
                "Backup dir {} already exist. Please backup this app manually".format(backup_dir))
        elif os.path.exists(src):
            if copy:
                print("Copying {} to {}".format(src, backup_dir))
                shutil.copytree(src, backup_dir)
            else:
                print("Moving {} to {}".format(src, backup_dir))
                self._file_utils.move_dir(src, backup_dir)

    def backup_old_directories(self):
        with Task("Backup old directories", self._prompt) as task:
            if task.do_step:
                data = os.path.join("C:\\", "data")
                if os.path.exists(data):
                    old_data = os.path.join("C:\\", "data", "old")
                    if not os.path.exists(old_data):
                        os.mkdir(old_data)

                    # Delete all but the oldest backup
                    current_backups = [os.path.join(old_data, d) for d in os.listdir(old_data)
                                       if os.path.isdir(os.path.join(old_data, d)) and d.startswith("ibex_backup")]
                    if len(current_backups) > 0:
                        all_but_newest_backup = sorted(current_backups, key=os.path.getmtime)[:-1]
                        backups_to_delete = all_but_newest_backup
                    else:
                        backups_to_delete = []

                    for d in backups_to_delete:
                        print("Removing backup {}".format(d))
                        self._file_utils.remove_tree(os.path.join(old_data, d))

                    # Move the folders
                    for app_path in [EPICS_PATH, EPICS_UTILS_PATH, GUI_PATH, PYTHON_PATH]:
                        self._backup_dir(app_path, copy=False)

                    # Backup settings and autosave
                    self._backup_dir(os.path.join("C:\\", "Instrument", "Settings"))
                    self._backup_dir(os.path.join("C:\\", "Instrument", "var", "Autosave"))
                else:
                    self._prompt.prompt_and_raise_if_not_yes(
                        "Unable to find data directory C:\\data. Please backup the current installation of IBEX "
                        "manually")

    def _get_mysql_dir(self):
        mysql_base_dir = os.path.join("C:\\", "Program Files", "MySQL")
        if not os.path.exists(mysql_base_dir):
            raise OSError
        else:
            mysql_versions = [d for d in os.listdir(mysql_base_dir) if os.path.isdir(os.path.join(mysql_base_dir,d))]
            if len(mysql_versions) == 0:
                raise OSError
            else:
                if len(mysql_versions) > 1:
                    print("Warning, more than 1 version of MySQL detected. Using {}".format(mysql_versions[0]))
                mysql_dir = os.path.join(mysql_base_dir, mysql_versions[0], "bin")

        return mysql_dir

    def backup_database(self):
        with Task("Backup database", self._prompt) as task:
            if task.do_step:
                try:
                    mysql_bin_dir = self._get_mysql_dir()
                    mysql_path = os.path.join(mysql_bin_dir, "mysql.exe")
                    mysql_admin_path = os.path.join(mysql_bin_dir, "mysqladmin.exe")
                    if not all([os.path.exists(p) for p in [mysql_path, mysql_admin_path]]):
                        raise OSError
                    if subprocess.call([mysql_path, "-u", "root", "-p", "--execute",
                                        "SET GLOBAL innodb_fast_shutdown=0",]) != 0 or \
                                    subprocess.call([mysql_admin_path, "-u", "root", "-p", "shutdown"]) != 0:
                        self._prompt.prompt_and_raise_if_not_yes(
                            "Stopping the MySQL service failed. Please do it manually")
                except OSError:
                    self._prompt.prompt_and_raise_if_not_yes(
                        "Unable to find mysql location. Please shut down the service manually")
                finally:
                    self._backup_dir(os.path.join("C:\\", "Instrument", "var", "mysql"))
                    self._prompt.prompt_and_raise_if_not_yes("Data backup complete. Please restart the MYSQL service")

    def update_release_notes(self):
        with Task("Update release notes", self._prompt) as task:
            if task.do_step:
                self._prompt.prompt_and_raise_if_not_yes(
                    "Have you updated the instrument release notes at https://github.com/ISISComputingGroup/IBEX/wiki?")

    def upgrade_mysql(self):
        with Task("Upgrade MySQL", self._prompt) as task:
            if task.do_step:
                install_mysql_url = "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/" \
                                   "Installing-and-Upgrading-MySQL"
                try:
                    mysql_path = os.path.join(self._get_mysql_dir(), "mysql.exe")
                    if not os.path.exists(mysql_path):
                        raise OSError()
                    subprocess.call([mysql_path, "--version"])
                    self._prompt.prompt_and_raise_if_not_yes(
                        "If required, upgrade MySQL as per {}".format(install_mysql_url))
                except OSError:
                    self._prompt.prompt_and_raise_if_not_yes(
                        "MySQL not detected on system. Please verify and install if necessary via the instructions at "
                        "{}".format(install_mysql_url))
                finally:
                    self._prompt.prompt_and_raise_if_not_yes(
                        "Confirm that the MySQL catalog auto-update has been switched off as described at {}"
                        .format(install_mysql_url))

    def reapply_hotfixes(self):
        with Task("Reapply Hotfixes", self._prompt) as task:
            if task.do_step:
                self._prompt.prompt_and_raise_if_not_yes(
                    "Have you applied any hotfixes listed that are not fixed by the release, as on the instrument "
                    "release notes at https://github.com/ISISComputingGroup/IBEX/wiki?")

    def restart_vis(self):
        with Task("Restart VIs", self._prompt) as task:
            if task.do_step:
                self._prompt.prompt_and_raise_if_not_yes(
                    "Please restart any VIs that were running at the start of the upgrade")

    def perform_client_tests(self):
        with Task("Client release tests", self._prompt) as task:
            if task.do_step:
                self._start_ibex_server()
                self._start_ibex_gui()
                self._prompt.prompt_and_raise_if_not_yes(
                    "Check that the version displayed in the client is as expected after the deployment")
                self._prompt.prompt_and_raise_if_not_yes(
                    "Confirm that genie_python works from within the client and via genie_python.bat (this includes"
                    "verifying that the 'g.' and 'inst.' prefixes work as expected)")
                self._prompt.prompt_and_raise_if_not_yes(
                    "Verify that the current configuration is consistent with the system prior to upgrade")

    def perform_server_tests(self):
        with Task("Server release tests", self._prompt) as task:
            if task.do_step:
                self._start_ibex_server()
                server_release_tests_url = "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/" \
                                           "Server-Release-Tests"

                print("For further details, see {}".format(server_release_tests_url))
                self._prompt.prompt_and_raise_if_not_yes("Check that blocks are logging as expected")

                print("Checking that configurations are being pushed to the appropriate repository")
                repo = git.Repo(self._get_config_path())
                repo.git.fetch()
                status = repo.git.status()
                print("Current repository status is: {}".format(status))
                if "up-to-date with 'origin/{}".format(self._get_machine_name()) in status:
                    print("Configurations updating correctly")
                else:
                    self._prompt.prompt_and_raise_if_not_yes(
                        "Unexpected git status. Please confirm that configurations are being pushed to the appropriate "
                        "remote repository")

                self._prompt.prompt_and_raise_if_not_yes(
                    "Check that the web dashboard for this instrument is updating "
                    "correctly: http://dataweb.isis.rl.ac.uk/IbexDataweb/default.html?Instrument={}"
                        .format(self._get_instrument_name()))

    def inform_instrument_scientists(self):
        with Task("Inform instrument scientists", self._prompt) as task:
            if task.do_step:
                # For future reference, genie_python can send emails!
                self._prompt.prompt_and_raise_if_not_yes(
                    "Inform the instrument scientists that the upgrade has been completed")



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

    def run_instrument_upgrade(self):
        self._upgrade_tasks.stop_ibex_server()
        self._upgrade_tasks.install_java()
        self._upgrade_tasks.take_screenshots()
        self._upgrade_tasks.backup_old_directories()
        self._upgrade_tasks.backup_database()
        self._upgrade_tasks.upgrade_instrument_configuration()
        self._upgrade_tasks.update_calibrations_repository()
        self._upgrade_tasks.remove_seci_shortcuts()
        self._upgrade_tasks.install_ibex_server(True)
        self._upgrade_tasks.install_ibex_client()
        self._upgrade_tasks.update_release_notes()
        self._upgrade_tasks.upgrade_mysql()
        self._upgrade_tasks.reapply_hotfixes()
        self._upgrade_tasks.restart_vis()
        self._upgrade_tasks.perform_client_tests()
        self._upgrade_tasks.perform_server_tests()
        self._upgrade_tasks.inform_instrument_scientists()


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
