"""
Tasks associated with install
"""

import pprint
import zipfile
from contextlib import contextmanager, closing

import os
import shutil
import socket
import subprocess
from datetime import date, datetime
from time import sleep

import psutil
import git
import six

from ibex_install_utils.admin_runner import AdminRunner, AdminCommandBuilder
from ibex_install_utils.ca_utils import CaWrapper
from ibex_install_utils.exceptions import UserStop, ErrorInRun, ErrorInTask
from ibex_install_utils.file_utils import FileUtils
from ibex_install_utils.run_process import RunProcess
from ibex_install_utils.task import task
from ibex_install_utils.user_prompt import UserPrompt
from ibex_install_utils.motor_params import get_params_and_save_to_file

BACKUP_DATA_DIR = os.path.join("C:\\", "data")
BACKUP_DIR = os.path.join(BACKUP_DATA_DIR, "old")

INSTRUMENT_BASE_DIR = os.path.join("C:\\", "Instrument")
APPS_BASE_DIR = os.path.join(INSTRUMENT_BASE_DIR, "Apps")
EPICS_PATH = os.path.join(APPS_BASE_DIR, "EPICS")

SYSTEM_SETUP_PATH = os.path.join(EPICS_PATH, "SystemSetup")
GUI_PATH = os.path.join(APPS_BASE_DIR, "Client")
GUI_PATH_E4 = os.path.join(APPS_BASE_DIR, "Client_E4")
PYTHON_PATH = os.path.join(APPS_BASE_DIR, "Python")
CONFIG_UPGRADE_SCRIPT_DIR = os.path.join(EPICS_PATH, "misc", "upgrade", "master")
EPICS_UTILS_PATH = os.path.join(APPS_BASE_DIR, "EPICS_UTILS")
DESKTOP_TRAINING_FOLDER_PATH = os.path.join(os.environ["userprofile"], "desktop", "Mantid+IBEX training")
SETTINGS_CONFIG_FOLDER = os.path.join("Settings", "config")
SETTINGS_CONFIG_PATH = os.path.join(INSTRUMENT_BASE_DIR, SETTINGS_CONFIG_FOLDER)
CALIBRATION_PATH = os.path.join(SETTINGS_CONFIG_PATH, "common")
SOURCE_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
SOURCE_MACHINE_SETTINGS_CONFIG_PATH = os.path.join(SOURCE_FOLDER, SETTINGS_CONFIG_FOLDER, "NDXOTHER")
SOURCE_MACHINE_SETTINGS_COMMON_PATH = os.path.join(SOURCE_FOLDER, SETTINGS_CONFIG_FOLDER, "common")

INST_SHARE_AREA = os.path.join(r"\\isis.cclrc.ac.uk", "inst$")

MYSQL8_INSTALL_DIR = os.path.join(APPS_BASE_DIR, "MySQL")
MYSQL57_INSTALL_DIR = os.path.join("C:\\", "Program Files", "MySQL", "MySQL Server 5.7")
MYSQL_LATEST_VERSION = "8.0.15"
MYSQL_ZIP = os.path.join(INST_SHARE_AREA, "kits$", "CompGroup", "ICP", "MySQL",
                         "mysql-{}-winx64.zip".format(MYSQL_LATEST_VERSION))

VAR_DIR = os.path.join(INSTRUMENT_BASE_DIR, "var")
MYSQL_FILES_DIR = os.path.join(VAR_DIR, "mysql")
PV_BACKUPS_DIR = os.path.join(VAR_DIR, "deployment_pv_backups")
SQLDUMP_FILE_TEMPLATE = "ibex_db_sqldump_{}.sql"

VCRUNTIME140 = os.path.join("C:\\", "Windows", "System32", "vcruntime140.dll")
VCRUNTIME140_INSTALLER = os.path.join(INST_SHARE_AREA, "kits$", "CompGroup", "ICP", "vcruntime140_installer", "vc_redist.x64.exe")

LABVIEW_DAE_DIR = os.path.join("C:\\", "LabVIEW modules", "DAE")

USER_START_MENU = os.path.join("C:\\", "users", "spudulike", "AppData", "Roaming", "Microsoft", "Windows", "Start Menu")
PC_START_MENU = os.path.join("C:\\", "ProgramData", "Microsoft", "Windows", "Start Menu")
SECI = "SECI User interface.lnk"
SECI_ONE_PATH = os.path.join("C:\\", "Program Files (x86)", "CCLRC ISIS Facility")
AUTOSTART_LOCATIONS = [os.path.join(USER_START_MENU, "Programs", "Startup", SECI),
                       os.path.join(PC_START_MENU, "Programs", "Startup", SECI)]

STAGE_DELETED = os.path.join(INST_SHARE_AREA, "backups$", "stage-deleted")
SMALLEST_PERMISSIBLE_MYSQL_DUMP_FILE_IN_BYTES = 100

RAM_MIN = 8e+9
FREE_DISK_MIN = 3e+10


class UpgradeInstrument(object):
    """
    Class to upgrade the instrument installation to the given version of IBEX.
    """
    def __init__(self, user_prompt, server_source_dir, client_source_dir, client_e4_source_dir, file_utils=FileUtils()):
        """
        Initializer.
        Args:
            user_prompt: a object to allow prompting of the user
            server_source_dir: directory to install ibex server from
            client_source_dir: directory to install ibex client from
            client_e4_source_dir: directory to install ibex E4 client from
            file_utils : collection of file utilities
        """
        self._upgrade_tasks = UpgradeTasks(
            user_prompt, server_source_dir, client_source_dir, client_e4_source_dir, file_utils)

    @staticmethod
    def _should_install_utils():
        """
        Condition on which to install ibex utils (ICP_Binaries)

        :return: True if utils should be installed, False otherwise
        """
        return not os.path.exists(LABVIEW_DAE_DIR)

    def run_test_update(self):
        """
        Run a complete test upgrade on the current system
        """
        self._upgrade_tasks.user_confirm_upgrade_type_on_machine('Training Machine')
        self._upgrade_tasks.stop_ibex_server()
        self._upgrade_tasks.remove_old_ibex()
        self._upgrade_tasks.clean_up_desktop_ibex_training_folder()
        self._upgrade_tasks.remove_settings()
        self._upgrade_tasks.install_settings()
        self._upgrade_tasks.install_ibex_server(self._should_install_utils())
        self._upgrade_tasks.install_ibex_client()
        self._upgrade_tasks.upgrade_notepad_pp()

    def remove_all_and_install_client_and_server(self):
        """
        Either install or upgrade the ibex client and server
        """
        self._upgrade_tasks.confirm(
            "This script removes IBEX client and server and installs the latest build of both, and upgrade the "
            "config/schema without any extra steps. Proceed?")

        self._upgrade_tasks.user_confirm_upgrade_type_on_machine('Client/Server Machine')
        self._upgrade_tasks.stop_ibex_server()
        self._upgrade_tasks.remove_old_ibex()
        self._upgrade_tasks.install_ibex_server(self._should_install_utils())
        self._upgrade_tasks.install_e4_ibex_client()
        self._upgrade_tasks.upgrade_instrument_configuration()
        self._upgrade_tasks.create_journal_sql_schema()

    def run_instrument_tests(self):
        """
        Run through client and server tests once installation / deployment has completed.
        """
        self._upgrade_tasks.perform_client_tests()
        self._upgrade_tasks.perform_server_tests()
        self._upgrade_tasks.inform_instrument_scientists()

    def run_instrument_install(self):
        """
        Do a first installation of IBEX on a new instrument.
        """
        self._upgrade_tasks.confirm("This script performs a first-time full installation of the IBEX server and client "
                                    "on a new instrument. Proceed?")

        self._upgrade_tasks.check_resources()
        self._upgrade_tasks.check_java_installation()

        self._upgrade_tasks.remove_seci_shortcuts()
        self._upgrade_tasks.remove_seci_one()

        self._upgrade_tasks.install_ibex_server(self._should_install_utils())
        self._upgrade_tasks.install_mysql()
        self._upgrade_tasks.configure_mysql()
        self._upgrade_tasks.install_ibex_client()
        self._upgrade_tasks.setup_config_repository()
        self._upgrade_tasks.upgrade_instrument_configuration()
        self._upgrade_tasks.create_journal_sql_schema()
        self._upgrade_tasks.configure_com_ports()
        self._upgrade_tasks.setup_calibrations_repository()
        self._upgrade_tasks.update_calibrations_repository()
        self._upgrade_tasks.apply_changes_noted_in_release_notes()
        self._upgrade_tasks.update_release_notes()
        self._upgrade_tasks.restart_vis()
        self._upgrade_tasks.install_wiring_tables()
        self._upgrade_tasks.configure_motion()
        self._upgrade_tasks.add_nagios_checks()
        self._upgrade_tasks.update_instlist()
        self._upgrade_tasks.update_web_dashboard()
        self._upgrade_tasks.put_autostart_script_in_startup_area()

    def run_instrument_deploy(self):
        """
        Deploy a full IBEX upgrade on an existing instrument.
        """
        self._upgrade_tasks.confirm(
            "This script performs a full upgrade of the IBEX server and client on an existing instrument. Proceed?")
        self.run_instrument_deploy_pre_stop()
        self.run_instrument_deploy_main()
        self.run_instrument_deploy_post_start()

    def run_instrument_deploy_post_start(self):
        """
            Upgrade an instrument. Steps to do after ibex has been started.

            Current the server can not be started in this python script.
        """
        self._upgrade_tasks.start_ibex_server()
        self._upgrade_tasks.start_ibex_gui()
        self._upgrade_tasks.restart_vis()
        self._upgrade_tasks.perform_client_tests()
        self._upgrade_tasks.perform_server_tests()
        self._upgrade_tasks.save_motor_parameters_to_file()
        self._upgrade_tasks.save_blocks_to_file()
        self._upgrade_tasks.save_blockserver_pv_to_file()
        self._upgrade_tasks.put_autostart_script_in_startup_area()
        self._upgrade_tasks.inform_instrument_scientists()

    def run_instrument_deploy_main(self):
        """
            Upgrade an instrument. Steps to do after ibex has been stopped but before it is restarted.

            Current the server can not be started or stopped in this python script.
        """
        self._upgrade_tasks.check_java_installation()
        self._upgrade_tasks.backup_old_directories()
        self._upgrade_tasks.backup_database()
        self._upgrade_tasks.truncate_database()
        self._upgrade_tasks.remove_seci_shortcuts()
        self._upgrade_tasks.install_ibex_server(self._should_install_utils())
        self._upgrade_tasks.install_mysql()
        self._upgrade_tasks.configure_mysql()
        self._upgrade_tasks.install_ibex_client()
        self._upgrade_tasks.upgrade_instrument_configuration()
        self._upgrade_tasks.create_journal_sql_schema()
        self._upgrade_tasks.update_calibrations_repository()
        self._upgrade_tasks.apply_changes_noted_in_release_notes()
        self._upgrade_tasks.update_release_notes()
        self._upgrade_tasks.reapply_hotfixes()

    def run_instrument_deploy_pre_stop(self):
        """
            Upgrade an instrument. Steps to do before ibex is stopped.

            Current the server can not be started or stopped in this python script.
        """
        self._upgrade_tasks.user_confirm_upgrade_type_on_machine('Client/Server Machine')
        self._upgrade_tasks.record_running_vis()
        self._upgrade_tasks.save_motor_parameters_to_file()
        self._upgrade_tasks.save_blocks_to_file()
        self._upgrade_tasks.save_blockserver_pv_to_file()
        self._upgrade_tasks.stop_ibex_server()

    def run_truncate_database(self):
        """
        Backup and truncate databases only
        """
        self._upgrade_tasks.backup_database()
        self._upgrade_tasks.truncate_database()

    def run_force_upgrade_mysql(self):
        self._upgrade_tasks.install_mysql(force=True)
        self._upgrade_tasks.configure_mysql()


class UpgradeTasks(object):
    """
    Class containing separate upgrade tasks.
    """

    def __init__(self, user_prompt, server_source_dir, client_source_dir, client_e4_source_dir, file_utils=FileUtils()):
        """
        Initializer.
        Args:
            user_prompt: a object to allow prompting of the user
            server_source_dir: directory to install ibex server from
            client_source_dir: directory to install ibex client from
            client_e4_source_dir: directory to install ibex E4 client from
            file_utils : collection of file utilities
        """
        self.prompt = user_prompt  # This is needed to allow @tasks to work
        self._server_source_dir = server_source_dir
        self._client_source_dir = client_source_dir
        self._client_e4_source_dir = client_e4_source_dir
        self._file_utils = file_utils

        self._machine_name = self._get_machine_name()

        self._ca = CaWrapper()

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

    def confirm(self, message):
        """
        Ask user to confirm correct script was chosen.
        """
        self.prompt.prompt_and_raise_if_not_yes(message, default="Y")

    def stop_ibex_server(self):
        """
        Stop the current IBEX server running. Current this can not be run because it kills any python
        processes including this one.

        Returns:

        """
        # with Task("Stopping IBEX server", self.prompt):
        #     RunProcess(EPICS_PATH, "stop_ibex_server.bat").run()
        pass

    @task("Removing old version of IBEX")
    def remove_old_ibex(self):
        """
        Removes older versions of IBEX server, client, genie_python and epics utils
        Returns:

        """
        for path in (EPICS_PATH, PYTHON_PATH, GUI_PATH, GUI_PATH_E4, EPICS_UTILS_PATH):
            self._file_utils.remove_tree(path)

    @task("Removing training folder on desktop ...")
    def clean_up_desktop_ibex_training_folder(self):
        """
        Remove training folder from the desktop
        Returns:

        """
        self._file_utils.remove_tree(DESKTOP_TRAINING_FOLDER_PATH)

    @task("Removing old settings file")
    def remove_settings(self):
        """
        remove old settings
        Returns:

        """
        self._file_utils.remove_tree(SETTINGS_CONFIG_PATH)

    @task("Install settings")
    def install_settings(self):
        """
        Install new settings from the current folder
        Returns:

        """

        self._file_utils.mkdir_recursive(SETTINGS_CONFIG_PATH)
        settings_path = os.path.join(SETTINGS_CONFIG_PATH, self._machine_name)

        shutil.copytree(SOURCE_MACHINE_SETTINGS_CONFIG_PATH, settings_path)

        inst_name = self._machine_name.lower()
        for p in ["ndx", "nde"]:
            if inst_name.startswith(p):
                inst_name = inst_name.lower()[len(p):]
                break
        inst_name = inst_name.replace("-", "_")
        self._file_utils.move_file(
            os.path.join(settings_path, "Python", "init_inst_name.py"),
            os.path.join(settings_path, "Python", "init_{inst_name}.py".format(inst_name=inst_name)),
            self.prompt)

        shutil.copytree(SOURCE_MACHINE_SETTINGS_COMMON_PATH, os.path.join(SETTINGS_CONFIG_PATH, "common"))

    @task("Record running vis")
    def record_running_vis(self):
        """
        Get user to record running vis
        """
        self.prompt.prompt_and_raise_if_not_yes("Write down any VIs which are running for use later?")

    @task("Upgrading Notepad++. Please follow system dialogs")
    def upgrade_notepad_pp(self):
        """
        Install (start installation of) notepad ++
        Returns:

        """
        RunProcess(working_dir=APPS_BASE_DIR,
                   executable_file="GUP.exe",
                   executable_directory=r"C:\Program Files (x86)\Notepad++\updater").run()

    @task("Installing IBEX Server")
    def install_ibex_server(self, with_utils):
        """
        Install ibex server.
        Args:
            with_utils: True also install epics utils using icp binaries; False don't

        """
        self._file_utils.mkdir_recursive(APPS_BASE_DIR)
        RunProcess(self._server_source_dir, "install_to_inst.bat", prog_args=["NOLOG"]).run()
        if with_utils and self.prompt.confirm_step("install icp binaries"):
            RunProcess(EPICS_PATH, "create_icp_binaries.bat").run()

    @task("Installing IBEX Client (Old E3)")
    def install_ibex_client(self):
        """
        Install the ibex client (which also installs genie python).

        """
        self._install_set_version_of_ibex_client(self._client_source_dir)

    @task("Installing IBEX Client")
    def install_e4_ibex_client(self):
        """
        Install the ibex client E4 version (which also installs genie python).

        """
        source_dir = self._client_e4_source_dir
        if source_dir is None:
            self.prompt.prompt_and_raise_if_not_yes("The E4 client path has not been set; continue with installation?")
        else:
            self._install_set_version_of_ibex_client(source_dir)

    def _install_set_version_of_ibex_client(self, source_dir):
        """
        Install a given version of the Ibex client.
        Args:
            source_dir: source directory for the client
        """
        self._file_utils.mkdir_recursive(APPS_BASE_DIR)

        RunProcess(source_dir, "install_client.bat", press_any_key=True).run()

    # @task("Starting IBEX server")
    def start_ibex_server(self):
        """
        Start the ibex server. Can not do this because it would kill the current python process.
        Returns:

        """
        pass

    @task("Starting IBEX gui")
    def start_ibex_gui(self):
        """
        Start the IBEX GUI
        :return:
        """
        subprocess.Popen([os.path.join(GUI_PATH_E4, "ibex-client.exe")], cwd=GUI_PATH_E4)

    def user_confirm_upgrade_type_on_machine(self, machine_type):
        """
        Print information about the current upgrade and prompt the user
        Returns:
        Raises UserStop: when the user doesn't want to continue

        """
        print("Upgrade {0} as a {1}".format(self._machine_name, machine_type))
        print("    Server source: {0}".format(self._server_source_dir))
        print("    Client source: {0}".format(self._client_source_dir))
        answer = self.prompt.prompt("Continue? [Y/N]", ["Y", "N"], "Y")
        if answer != "Y":
            raise UserStop()

    @task("Set up configuration repository")
    def setup_config_repository(self):
        """
        Creates the configuration repository, and swaps or creates a branch for the instrument.

        """
        inst_name = self._machine_name

        subprocess.call("git config --global core.autocrlf true")
        subprocess.call("git config --global credential.helper wincred")
        subprocess.call("git config --global user.name spudulike")
        set_user_email = "git config --global user.email spudulike@{}.isis.cclrc.ac.uk"
        subprocess.call(set_user_email.format(inst_name.lower()))

        if not os.path.exists(SETTINGS_CONFIG_PATH):
            os.makedirs(SETTINGS_CONFIG_PATH)

        subprocess.call(
            "git clone http://spudulike@control-svcs.isis.cclrc.ac.uk/gitroot/instconfigs/inst.git {}".format(
                inst_name), cwd=SETTINGS_CONFIG_PATH)

        inst_config_path = os.path.join(SETTINGS_CONFIG_PATH, inst_name)
        subprocess.call("git pull", cwd=inst_config_path)

        branch_exists = subprocess.call("git checkout {}".format(inst_name), cwd=inst_config_path) == 0
        if not branch_exists:
            subprocess.call("git checkout -b {}".format(inst_name), cwd=inst_config_path)

        inst_scripts_path = os.path.join(inst_config_path, "Python")
        if not os.path.exists(os.path.join(inst_scripts_path, "init_{}.py".format(inst_name.lower()))):
            try:
                os.rename(os.path.join(inst_scripts_path, "init_inst_name.py"),
                          os.path.join(inst_scripts_path, "init_{}.py".format(inst_name.lower())))
                subprocess.call("git add init_{}.py".format(inst_name.lower()), cwd=inst_scripts_path)
                subprocess.call("git rm init_inst_name.py", cwd=inst_scripts_path)
                subprocess.call('git commit -m"create initial python"'.format(inst_name), cwd=inst_config_path)
                subprocess.call("git push --set-upstream origin {}".format(inst_name), cwd=inst_config_path)
            except Exception as e:
                self.prompt.prompt_and_raise_if_not_yes(
                    "Something went wrong setting up the configurations repository. Please resolve manually, "
                    "instructions are in the developers manual under "
                    "First-time-installing-and-building-(Windows): \n {}".format(e.message))

    @task("Upgrading instrument configuration")
    def upgrade_instrument_configuration(self):
        """
        Update the configuration on the instrument using its upgrade config script.
        """
        manual_prompt = "Merge the master configurations branch into the instrument configuration. "\
                        "From C:\Instrument\Settings\config\[machine name] run:\n"\
                        "    0. Clean up any in progress merge (e.g. git merge --abort)\n"\
                        "    1. git checkout master\n"\
                        "    2. git pull\n"\
                        "    3. git checkout [machine name]\n"\
                        "    4. git merge master\n"\
                        "    5. Resolve any merge conflicts\n"\
                        "    6. git push\n"
        automatic_prompt = "Attempt automatic configuration merge?"
        if self.prompt.confirm_step(automatic_prompt):
            try:
                repo = git.Repo(os.path.join(SETTINGS_CONFIG_PATH, self._machine_name))
                if repo.active_branch.name != self._machine_name:
                    print("Git branch, '{}', is not the same as machine name ,'{}' ".format(
                        repo.active_branch, self._machine_name))
                    raise ErrorInTask("Git branch is not the same as machine name")
                else:
                    print("     fetch: {}".format(repo.git.fetch()))
                    print("     merge: {}".format(repo.git.merge("origin/master")))
                    # no longer push let the instrument do that on start up if needed
            except git.GitCommandError as e:
                print("Error doing automatic merge, please perform the merge manually: {}".format(e))
                self.prompt.prompt_and_raise_if_not_yes(manual_prompt)
        else:
            self.prompt.prompt_and_raise_if_not_yes(manual_prompt)

        RunProcess(CONFIG_UPGRADE_SCRIPT_DIR, "upgrade.bat", capture_pipes=False).run()

    @task("Remove SECI shortcuts")
    def remove_seci_shortcuts(self):
        """
        Remove (or at least ask the user to remove) all Seci shortcuts
        """
        for path in AUTOSTART_LOCATIONS:
            if os.path.exists(path):
                self.prompt.prompt_and_raise_if_not_yes(
                    "SECI autostart found in {}, delete this.".format(path))

        self.prompt.prompt_and_raise_if_not_yes("Remove task bar shortcut to SECI")
        self.prompt.prompt_and_raise_if_not_yes("Remove desktop shortcut to SECI")
        self.prompt.prompt_and_raise_if_not_yes("Remove start menu shortcut to SECI")

    @task("Remove SECI 1 Path")
    def remove_seci_one(self):
        """
        Removes SECI 1
        """
        if os.path.exists(SECI_ONE_PATH):
            try:
                self._file_utils.remove_tree(SECI_ONE_PATH, use_robocopy=False)
            except (IOError, WindowsError) as e:
                self.prompt.prompt_and_raise_if_not_yes("Failed to remove SECI 1 (located in '{}') because "
                                                        "'{}'. Please remove it manually and type 'Y' to "
                                                        "confirm".format(SECI_ONE_PATH, e.message))

    @task("Set up calibrations repository")
    def setup_calibrations_repository(self):
        """
        Set up the calibration repository
        """
        if os.path.isdir(CALIBRATION_PATH):
            if self.prompt.prompt("Calibrations directory already exists. Update calibrations repository?",
                           ["Y", "N"], "N") == "Y":
                self.update_calibrations_repository()
        else:
            exit_code = subprocess.call("git clone http://control-svcs.isis.cclrc.ac.uk/gitroot/instconfigs/common.git "
                            "C:\Instrument\Settings\config\common")
            if exit_code is not 0:
                raise ErrorInRun("Failed to set up common calibration directory.")

    @task("Updating calibrations repository")
    def update_calibrations_repository(self):
        """
        Update the calibration repository
        """
        try:
            repo = git.Repo(CALIBRATION_PATH)
            repo.git.pull()
        except git.GitCommandError:
            self.prompt.prompt_and_raise_if_not_yes("There was an error pulling the calibrations repo.\n"
                                                    "Manually pull it. Path='{}'".format(CALIBRATION_PATH))

    @task("Install java")
    def check_java_installation(self):
        """
        Checks Java installation
        """
        java_url = "/<Public Share>/third_party_installers/"
        try:
            subprocess.call(["java", "-version"])
            self.prompt.prompt_and_raise_if_not_yes(
                "Confirm that the java version above is the desired version or that you have "
                "upgraded to the desired 64-bit version from {}".format(java_url))
        except (subprocess.CalledProcessError, WindowsError):
            self.prompt.prompt_and_raise_if_not_yes(
                    "No installation of Java found on this machine. You can find an installer for the java"
                    "version used in the current release in {}.".format(java_url))

        self.prompt.prompt_and_raise_if_not_yes(
            "Is auto-update turned off? This can be checked from the Java control panel in "
            "C:\\Program Files\\Java\\jre\\bin\\javacpl.exe")

    @task("Configure COM ports")
    def configure_com_ports(self):
        """
        Configure the COM ports
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Using NPort Administrator (available under /Kits$/CompGroup/Utilities/), check that the COM ports "
            "on this machine are configured to standard, i.e.:\n"
            "- Moxa 1 starts at COM5\n"
            "- Moxa 2 starts at COM21\n"
            "- etc.\n")

    @staticmethod
    def _get_backup_dir():
        """
        Returns: The backup dir, will create it if needed (both old and dir).
        Raises: IOError if the base dir doesn't exist
        """
        new_backup_dir = os.path.join(BACKUP_DIR, "ibex_backup_{}".format(UpgradeTasks._today_date_for_filenames()))

        if not os.path.exists(BACKUP_DATA_DIR):
            raise IOError("Base directory does not exist {} should be a provided linked dir".format(BACKUP_DATA_DIR))
        if not os.path.exists(BACKUP_DIR):
            os.mkdir(BACKUP_DIR)
        if not os.path.exists(new_backup_dir):
            os.mkdir(new_backup_dir)
        return new_backup_dir

    @staticmethod
    def _today_date_for_filenames():
        return date.today().strftime("%Y_%m_%d")

    def _backup_dir(self, src, copy=True):
        backup_dir = os.path.join(self._get_backup_dir(), os.path.basename(src))
        if src in os.getcwd():
            self.prompt.prompt_and_raise_if_not_yes(
                "You appear to be trying to delete the folder, {}, containing the current working directory {}. "
                "Please do this manually to be on the safe side".format(src, os.getcwd()))
        elif os.path.exists(backup_dir):
            self.prompt.prompt_and_raise_if_not_yes(
                "Backup dir {} already exist. Please backup this app manually".format(backup_dir))
        elif os.path.exists(src):
            if copy:
                print("Copying {} to {}".format(src, backup_dir))
                shutil.copytree(src, backup_dir)
            else:
                print("Moving {} to {}".format(src, backup_dir))
                self._file_utils.move_dir(src, backup_dir)

    @task("Backup old directories")
    def backup_old_directories(self):
        """
        Backup old directories
        """
        if os.path.exists(BACKUP_DATA_DIR):
            if not os.path.exists(BACKUP_DIR):
                os.mkdir(BACKUP_DIR)

            # Delete all but the oldest backup
            current_backups = [os.path.join(BACKUP_DIR, d) for d in os.listdir(BACKUP_DIR)
                               if os.path.isdir(os.path.join(BACKUP_DIR, d)) and d.startswith("ibex_backup")]
            if len(current_backups) > 0:
                all_but_newest_backup = sorted(current_backups, key=os.path.getmtime)[:-1]
                backups_to_delete = all_but_newest_backup
            else:
                backups_to_delete = []

            for d in backups_to_delete:
                print("Removing backup {}".format(d))
                self._file_utils.remove_tree(os.path.join(BACKUP_DIR, d))

            # Move the folders
            for app_path in [EPICS_PATH, EPICS_UTILS_PATH, GUI_PATH, PYTHON_PATH, GUI_PATH_E4]:
                self._backup_dir(app_path, copy=False)

            # Backup settings and autosave
            self._backup_dir(os.path.join(INSTRUMENT_BASE_DIR, "Settings"))
            self._backup_dir(os.path.join(INSTRUMENT_BASE_DIR, "var", "Autosave"))
        else:
            self.prompt.prompt_and_raise_if_not_yes(
                "Unable to find data directory '{}'. Please backup the current installation of IBEX "
                "manually".format(BACKUP_DATA_DIR))

    def _get_mysql_dir(self):
        return os.path.join(MYSQL8_INSTALL_DIR, "bin")

    @task("Backup database")
    def backup_database(self):
        """
        Backup the database
        """
        result_file = os.path.join(self._get_backup_dir(),
                                   SQLDUMP_FILE_TEMPLATE.format(UpgradeTasks._today_date_for_filenames()))

        mysql_bin_dir = self._get_mysql_dir()
        dump_command = ["-u", "root", "-p", "--all-databases", "--single-transaction",
                        "--result-file={}".format(result_file)]
        RunProcess(MYSQL_FILES_DIR, "mysqldump.exe", executable_directory=mysql_bin_dir,
                   prog_args=dump_command,
                   capture_pipes=False).run()

        if os.path.getsize(result_file) < SMALLEST_PERMISSIBLE_MYSQL_DUMP_FILE_IN_BYTES:
            self.prompt.prompt_and_raise_if_not_yes(
                "Dump file '{}' seems to be small is it correct? ".format(result_file))

        self._file_utils.move_file(result_file, os.path.join(STAGE_DELETED, self._get_machine_name()),
                                   self.prompt)

    @task("Truncate database")
    def truncate_database(self):
        """
        Truncate the message log and sample tables
        """
        try:
            mysql_bin_dir = self._get_mysql_dir()

            RunProcess(MYSQL_FILES_DIR, "mysql.exe", executable_directory=mysql_bin_dir,
                       prog_args=["-u", "root", "-p",
                                  "--execute", "truncate table msg_log.message;truncate table archive.sample"],
                       capture_pipes=False).run()

        except ErrorInRun as ex:
            self.prompt.prompt_and_raise_if_not_yes(
                "Unable to run mysql command, please truncate the database manually. "
                "Error is {}".format(ex.message))

    @task("Update release notes")
    def update_release_notes(self):
        """
        Update the release notes.
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Have you updated the instrument release notes at https://github.com/ISISComputingGroup/IBEX/wiki?")

    @task("Configure MySQL")
    def configure_mysql(self):
        """
        Copy mysql settings and run the MySQL configuration script
        """
        my_ini_file = os.path.join(EPICS_PATH, "systemsetup", "my.ini")
        try:
            shutil.copy(my_ini_file, MYSQL8_INSTALL_DIR)
        except (OSError, IOError) as e:
            self.prompt.prompt_and_raise_if_not_yes("Couldn't copy my.ini from {} to {} because {}. "
                                                    "Please do this manually confirm when complete."
                                                    .format(my_ini_file, MYSQL8_INSTALL_DIR, e))

        # Restart to pick up new my.ini
        admin_commands = AdminCommandBuilder()
        admin_commands.add_command("sc", "stop MYSQL80")
        # Sleep to wait for service to stop so we can restart it.
        admin_commands.add_command("ping", "-n 10 127.0.0.1 >nul", expected_return_val=None)
        admin_commands.add_command("sc", "start MYSQL80")
        admin_commands.run_all()


        self.prompt.prompt_and_raise_if_not_yes(
            "Run config_mysql.bat in {} now. \n"
            "WARNING: performing this step will wipe all existing historical data. \n"
            "Confirm you have done this. ".format(SYSTEM_SETUP_PATH))



    def _remove_old_versions_of_mysql8(self):
        self.prompt.prompt_and_raise_if_not_yes("Warning: this will erase all data held in the MySQL database. "
                                                "Are you sure you want to continue?")

        admin_commands = AdminCommandBuilder()
        admin_commands.add_command("sc", "stop MYSQL80", expected_return_val=None)
        admin_commands.add_command("sc", "delete MYSQL80", expected_return_val=None)
        admin_commands.run_all()

        sleep(5)  # Time for service to stop

        if os.path.exists(MYSQL8_INSTALL_DIR):
            shutil.rmtree(MYSQL8_INSTALL_DIR)

        self._remove_old_mysql_data_dir()

    def _remove_old_mysql_data_dir(self):
        if os.path.exists(MYSQL_FILES_DIR):
            shutil.rmtree(MYSQL_FILES_DIR)

    def _install_latest_mysql8(self):

        self._remove_old_mysql_data_dir()

        os.makedirs(MYSQL8_INSTALL_DIR)

        mysql_unzip_temp = os.path.join(APPS_BASE_DIR, "temp-mysql-unzip")

        with closing(zipfile.ZipFile(MYSQL_ZIP)) as f:
            f.extractall(mysql_unzip_temp)

        mysql_unzip_temp_release = os.path.join(mysql_unzip_temp, "mysql-{}-winx64".format(MYSQL_LATEST_VERSION))
        for item in os.listdir(mysql_unzip_temp_release):
            shutil.move(os.path.join(mysql_unzip_temp_release, item), MYSQL8_INSTALL_DIR)

        shutil.rmtree(mysql_unzip_temp)

        os.makedirs(MYSQL_FILES_DIR)

        mysql = os.path.join(MYSQL8_INSTALL_DIR, "bin", "mysql.exe")
        mysqld = os.path.join(MYSQL8_INSTALL_DIR, "bin", "mysqld.exe")

        admin_commands = AdminCommandBuilder()

        admin_commands.add_command(mysqld, '--datadir="{}" --initialize-insecure --console --log-error-verbosity=3'
                                   .format(os.path.join(MYSQL_FILES_DIR, "data")))

        # Wait for initialize since admin runner can't wait for completion. Maybe we can detect completion another way?
        admin_commands.add_command(mysqld, '--install MYSQL80 --datadir="{}"'
                                   .format(os.path.join(MYSQL_FILES_DIR, "data")))

        admin_commands.add_command("sc", "start MYSQL80")
        admin_commands.add_command("sc", "config MYSQL80 start= auto")

        admin_commands.run_all()

        sleep(5)  # Time for service to start

        sql_password = self.prompt.prompt("Enter the MySQL root password:", UserPrompt.ANY,
                                          os.getenv("MYSQL_PASSWORD", "environment variable not set"))

        subprocess.check_call('{} -u root -e "ALTER USER \'root\'@\'localhost\' '
                              'IDENTIFIED WITH mysql_native_password BY \'{}\';FLUSH privileges;"'
                              .format(mysql, sql_password))

    def _install_vcruntime140(self):
        if not os.path.exists(VCRUNTIME140):
            self.prompt.prompt_and_raise_if_not_yes(
                "MySQL server 8 requires microsoft visual C++ runtime to be installed.\r\n"
                "Install it from {} and confirm when complete".format(VCRUNTIME140_INSTALLER))

    @task("Install latest MySQL")
    def install_mysql(self, force=False):
        """
        Upgrade mysql step
        """
        if os.path.exists(os.path.join(MYSQL57_INSTALL_DIR, "bin", "mysql.exe")):
            self.prompt.prompt_and_raise_if_not_yes("MySQL 5.7 detected. Please use the MySQL installer application"
                                                    "to remove MySQL 5.7. When it asks you whether to remove data"
                                                    "directories, answer yes. Type 'Y' when complete.")

        mysql_8_exe = os.path.join(MYSQL8_INSTALL_DIR, "bin", "mysql.exe")

        if os.path.exists(mysql_8_exe):
            version = subprocess.check_output("{} --version".format(mysql_8_exe))
            if MYSQL_LATEST_VERSION in version and not force:
                print("MySQL already on latest version ({}) - nothing to do.".format(MYSQL_LATEST_VERSION))
                return

            self._remove_old_versions_of_mysql8()

        self._install_vcruntime140()
        self._install_latest_mysql8()

    @task("Reapply Hotfixes")
    def reapply_hotfixes(self):
        """
        Reapply any hotfixes to the build.
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Have you applied any hotfixes listed that are not fixed by the release, as on the instrument "
            "release notes at https://github.com/ISISComputingGroup/IBEX/wiki?")

    @task("Restart VIs")
    def restart_vis(self):
        """
        Restart Vis which were running on upgrade start.
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Please restart any VIs that were running at the start of the upgrade")

    @task("Client release tests")
    def perform_client_tests(self):
        """
        Test that the client works
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Check that the version displayed in the client is as expected after the deployment")
        self.prompt.prompt_and_raise_if_not_yes(
            "Confirm that genie_python works from within the client and via genie_python.bat (this includes"
            "verifying that the 'g.' and 'inst.' prefixes work as expected)")
        self.prompt.prompt_and_raise_if_not_yes(
            "Verify that the current configuration is consistent with the system prior to upgrade")

    @task("Server release tests")
    def perform_server_tests(self):
        """
        Test that the server works
        """
        server_release_tests_url = "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/" \
                                   "Server-Release-Tests"

        print("For further details, see {}".format(server_release_tests_url))
        self.prompt.prompt_and_raise_if_not_yes("Check that blocks are logging as expected")

        print("Checking that configurations are being pushed to the appropriate repository")
        repo = git.Repo(self._get_config_path())
        repo.git.fetch()
        status = repo.git.status()
        print("Current repository status is: {}".format(status))
        if "up-to-date with 'origin/{}".format(self._get_machine_name()) in status:
            print("Configurations updating correctly")
        else:
            self.prompt.prompt_and_raise_if_not_yes(
                "Unexpected git status. Please confirm that configurations are being pushed to the appropriate "
                "remote repository")

        self.prompt.prompt_and_raise_if_not_yes(
            "Check that the web dashboard for this instrument is updating "
            "correctly: http://dataweb.isis.rl.ac.uk/IbexDataweb/default.html?Instrument={}".format(
                self._get_instrument_name()))

    @task("Update Instrument List")
    def update_instlist(self):
        """
        Prompt user to add instrument to the list of known IBEX instruments
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Add the host name of the instrument to the list saved in the CS:INSTLIST PV")

    @task("Update web dashboard")
    def update_web_dashboard(self):
        """
        Prompt user to add the instrument to the web dashboard
        """
        redirect_page = os.path.join("C:", "inetpub", "wwwroot", "DataWeb", "Dashboards", "redirect.html")
        self.prompt.prompt_and_raise_if_not_yes(
            "Add the host name of the instrument to NDX_INSTS or ALL_INSTS in webserver.py in the JSON_bourne "
            "repository.")
        self.prompt.prompt_and_raise_if_not_yes(
            "On NDAEXTWEB1, pull the updated code and add a link to the instrument dashboard on the main "
            "dataweb page under {}".format(redirect_page))
        self.prompt.prompt_and_raise_if_not_yes(
            "Restart JSON_bourne on NDAEXTWEB1 when appropriate. "
            "(WARNING: This will kill all existing sessions!)")

    @task("Install wiring tables")
    def install_wiring_tables(self):
        """
        Prompt user to install wiring tables in the appropriate folder.
        """
        tables_dir = os.path.join(SETTINGS_CONFIG_PATH, self._machine_name, "configurations", "tables")
        self.prompt.prompt_and_raise_if_not_yes("Install the wiring tables in {}.".format(tables_dir))

    @task("Configure motion setpoints")
    def configure_motion(self):
        """
        Prompt user to configure Galils
        """
        url = "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/" \
              "Deployment-on-an-Instrument-Control-PC#set-up-motion-set-points"
        if self.prompt.prompt("Please configure the motion set points for this instrument. Instructions can be"
                              " found on the developer wiki. Open instructions in browser now?",
                              ["Y", "N"], "N") == "Y":
            subprocess.call("explorer {}".format(url))
        self.prompt.prompt_and_raise_if_not_yes("Confirm motion set points have been configured.")

    @task("Add Nagios checks")
    def add_nagios_checks(self):
        """
        Prompt user to add nagios checks.
        """
        # For future reference, genie_python can send emails!
        self.prompt.prompt_and_raise_if_not_yes("Add this instrument to the Nagios monitoring system. Talk to "
                                                "Freddie Akeroyd for help with this.")

    @task("Inform instrument scientists")
    def inform_instrument_scientists(self):
        """
        Inform instrument scientists that the machine has been upgraded.
        """
        # For future reference, genie_python can send emails!
        self.prompt.prompt_and_raise_if_not_yes(
            "Inform the instrument scientists that the upgrade has been completed")

    @task("Apply changes in release notes")
    def apply_changes_noted_in_release_notes(self):
        """
        Apply any changes noted in the release notes.
        """
        # For future reference, genie_python can send emails!
        self.prompt.prompt_and_raise_if_not_yes(
            "Look in the IBEX wiki at the release notes for the version you are deploying. Apply needed fixes.")

    @task("Create journal table SQL schema if it doesn't exist")
    def create_journal_sql_schema(self):
        """
        Create the journal schema if it doesn't exist.
        """
        sql_password = self.prompt.prompt("Enter the MySQL root password:", UserPrompt.ANY,
                                          os.getenv("MYSQL_PASSWORD", "environment variable not set"))
        RunProcess(SYSTEM_SETUP_PATH, "add_journal_table.bat", prog_args=[sql_password]).run()

    @contextmanager
    def timestamped_pv_backups_file(self, name, directory, extension="txt"):
        """
        Context manager to create a timestamped file in the pv backups directory

        Args:
            name (str): path to the file
            directory (str): directory of file
            extension (str): the extension of the file
        """
        filename = os.path.join(PV_BACKUPS_DIR, directory, "{}_{}.{}"
                                .format(name, datetime.today().strftime('%Y-%m-%d-%H-%M-%S'), extension))

        if not os.path.exists(os.path.join(PV_BACKUPS_DIR, directory)):
            os.makedirs(os.path.join(PV_BACKUPS_DIR, directory))

        with open(filename, "w") as f:
            yield f

    @task("Save motor parameters to csv file")
    def save_motor_parameters_to_file(self):
        """
        Saves the motor parameters to csv file.
        """
        with self.timestamped_pv_backups_file(name="motors", directory="motors", extension="csv") as f:
            get_params_and_save_to_file(f)

    @task("Save block parameters to file")
    def save_blocks_to_file(self):
        """
        Saves block parameters in a file.
        """

        blocks = self._ca.get_blocks()

        if blocks is None:
            print("Blockserver unavailable - not archiving.")
        else:
            if blocks:
                for block in blocks:
                    with self.timestamped_pv_backups_file(name=block, directory="blocks") as f:
                        f.write("{}\r\n".format(self._ca.cget(block)))
            else:
                print("Blockserver available but no blocks found - not archiving anything")

    @task("Save blockserver PV to file")
    def save_blockserver_pv_to_file(self):
        """
        Saves the blockserver PV to a file.
        """

        def _pretty_print(data):
            return pprint.pformat(data, width=800, indent=2)

        pvs_to_save = [
            ("all_component_details", "CS:BLOCKSERVER:ALL_COMPONENT_DETAILS"),
            ("block_names", "CS:BLOCKSERVER:BLOCKNAMES"),
            ("groups", "CS:BLOCKSERVER:GROUPS"),
            ("configs", "CS:BLOCKSERVER:CONFIGS"),
            ("components", "CS:BLOCKSERVER:COMPS"),
            ("runcontrol_out", "CS:BLOCKSERVER:GET_RC_OUT"),
            ("runcontrol_pars", "CS:BLOCKSERVER:GET_RC_PARS"),
            ("curr_config_details", "CS:BLOCKSERVER:GET_CURR_CONFIG_DETAILS"),
            ("server_status", "CS:BLOCKSERVER:SERVER_STATUS"),
            ("synoptic_names", "CS:SYNOPTICS:NAMES"),
        ]

        for name, pv in pvs_to_save:
            with self.timestamped_pv_backups_file(directory="inst_servers", name=name) as f:
                try:
                    f.write("{}\r\n".format(_pretty_print(self._ca.get_object_from_compressed_hexed_json(pv))))
                except Exception as e:
                    print("Couldn't get data from {} because: {}".format(pv, e.message))
                    f.write(e.message)

    def check_resources(self):
        """
        Check the machine's resources meet minimum requirements.
        """
        self.check_virtual_memory()
        self._check_disk_usage()

    @task("Check virtual memory is above {:.1e}B".format(RAM_MIN))
    def check_virtual_memory(self):
        """
        Checks the machine's virtual memory meet minimum requirements.
        """
        ram = psutil.virtual_memory()
        if ram.total < RAM_MIN:
            self.prompt.prompt_and_raise_if_not_yes(
                "The machine requires at least {:.1e}B of RAM to run IBEX.".format(RAM_MIN))

    @task("Check there is {:.1e}B free disk space".format(FREE_DISK_MIN))
    def _check_disk_usage(self):
        """
        Checks the machine's free disk space meets minimum requirements.
        """
        disk_space = psutil.disk_usage("/")
        if disk_space.free < FREE_DISK_MIN:
            self.prompt.prompt_and_raise_if_not_yes(
                "The machine requires at least {:.1e}B of free disk space to run IBEX.".format(FREE_DISK_MIN))

    @task("Put IBEX autostart into pc start menu")
    def put_autostart_script_in_startup_area(self):
        """
        Copies the ibex server autostart script into the PC startup folder so that the IBEX server starts
        automatically on startup.
        """

        autostart_script_name = "ibex_system_boot.bat"

        from_path = os.path.join(EPICS_PATH, autostart_script_name)
        to_path = os.path.join(PC_START_MENU, "Programs", "Startup", autostart_script_name)

        # Remove old version if exists
        if os.path.exists(to_path):
            try:
                os.remove(to_path)
            except (OSError, IOError):
                self.prompt.prompt_and_raise_if_not_yes("Please manually remove file at '{}'".format(to_path))

        try:
            shutil.copyfile(from_path, to_path)
        except (OSError, IOError):
            self.prompt.prompt_and_raise_if_not_yes("Please manually copy file from '{}' to '{}'"
                                                    .format(from_path, to_path))

