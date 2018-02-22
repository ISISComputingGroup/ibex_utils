"""
Tasks associated with install
"""

import os
import shutil
import socket
import subprocess
import git
from datetime import date

from ibex_install_utils.exceptions import UserStop, ErrorInRun
from ibex_install_utils.file_utils import FileUtils
from ibex_install_utils.user_prompt import UserPrompt

INSTRUMENT_BASE_DIR = os.path.join("C:\\", "Instrument")
APPS_BASE_DIR = os.path.join(INSTRUMENT_BASE_DIR, "Apps")
EPICS_PATH = os.path.join(APPS_BASE_DIR, "EPICS")
SYSTEM_SETUP_PATH = os.path.join(EPICS_PATH, "SystemSetup")
GUI_PATH = os.path.join(APPS_BASE_DIR, "Client")
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

LABVIEW_DAE_DIR = os.path.join("C:\\", "LabVIEW modules", "DAE")

USER_START_MENU = os.path.join("C:\\", "users", "spudulike", "AppData", "Roaming", "Microsoft", "Windows", "Start Menu")
PC_START_MENU = os.path.join("C:\\", "ProgramData", "Microsoft", "Windows", "Start Menu")
SECI = "SECI User interface.lnk"
AUTOSTART_LOCATIONS = [os.path.join(USER_START_MENU, "Programs", "Startup", SECI),
                       os.path.join(PC_START_MENU, "Programs", "Startup", SECI)]


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

    def confirm(self, message):
        """
        Ask user to confirm correct script was chosen.
        """
        self._prompt.prompt_and_raise_if_not_yes(message)

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

    def user_confirm_upgrade_type_on_machine(self, machine_type):
        """
        Print information about the current upgrade and prompt the user
        Returns:
        Raises UserStop: when the user doesn't want to continue

        """
        print("Upgrade {0} as a {1}".format(self._machine_name, machine_type))
        print("    Server source: {0}".format(self._server_source_dir))
        print("    Client source: {0}".format(self._client_source_dir))
        answer = self._prompt.prompt("Continue? [Y/N]", ["Y", "N"], "Y")
        if answer != "Y":
            raise UserStop()

    def setup_config_repository(self):
        with Task("Set up configuration repository", self._prompt) as task:
            if task.do_step:
                inst_name = self._machine_name

                subprocess.call("git config --global core.autocrlf true")
                subprocess.call("git config --global credential.helper wincred")
                subprocess.call("git config --global user.name spudulike")
                subprocess.call("git config --global user.email spudulike@{}.isis.cclrc.ac.uk".format(inst_name.lower()))

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
                        subprocess.call("git commit -m\"create initial python\"".format(inst_name), cwd=inst_config_path)
                        subprocess.call("git push --set-upstream origin {}".format(inst_name), cwd=inst_config_path)
                    except Exception as e:
                        self._prompt.prompt_and_raise_if_not_yes(
                            "Something went wrong setting up the configurations repository. Please resolve manually, "
                            "instructions are in the developers manual under "
                            "First-time-installing-and-building-(Windows): \n {}".format(e.message))

    def upgrade_instrument_configuration(self):
        """
        Update the configuration on the instrument using its upgrade config script.
        """
        with Task("Upgrading instrument configuration", self._prompt) as task:
            if task.do_step:
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
                if self._prompt.confirm_step(automatic_prompt):
                    try:
                        repo = git.Repo(os.path.join(SETTINGS_CONFIG_PATH, self._machine_name))
                        repo.git.checkout("master")
                        repo.git.pull()
                        repo.git.checkout(self._machine_name.upper())
                        repo.git.merge("master")
                        repo.git.push()
                    except git.GitCommandError as e:
                        print("Error doing automatic merge, please perform the merge manually: {}".format(e))
                        self._prompt.prompt_and_raise_if_not_yes(manual_prompt)
                else:
                    self._prompt.prompt_and_raise_if_not_yes(manual_prompt)
                RunProcess(CONFIG_UPGRADE_SCRIPT_DIR, "upgrade.bat").run()

    def remove_seci_shortcuts(self):
        """
        Remove (or at least ask the user to remove) all Seci shortcuts
        """
        with Task("Remove SECI shortcuts", self._prompt) as task:
            if task.do_step:
                for path in AUTOSTART_LOCATIONS:
                    if os.path.exists(path):
                        self._prompt.prompt_and_raise_if_not_yes(
                            "SECI autostart found in {}, delete this.".format(path))

                self._prompt.prompt_and_raise_if_not_yes("Remove task bar shortcut to SECI")
                self._prompt.prompt_and_raise_if_not_yes("Remove desktop shortcut to SECI")
                self._prompt.prompt_and_raise_if_not_yes("Remove start menu shortcut to SECI")

    def setup_calibrations_repository(self):
        """
        Set up the calibration repository
        """
        with Task("Set up calibrations repository", self._prompt) as task:
            if task.do_step:
                if os.path.isdir(CALIBRATION_PATH):
                    if self._prompt("Calibrations directory already exists. Update calibrations repository?",
                                    ["Y", "N"], "N") == "Y":
                        self.update_calibrations_repository()
                else:
                    os.makedirs(CALIBRATION_PATH)
                    subprocess.call("git clone http://control-svcs.isis.cclrc.ac.uk/gitroot/instconfigs/common.git "
                                    "C:\Instrument\Settings\config\common", cwd=CALIBRATION_PATH)

    def update_calibrations_repository(self):
        """
        Update the calibration repository
        """
        with Task("Updating calibrations repository", self._prompt) as task:
            if task.do_step:
                try:
                    repo = git.Repo(CALIBRATION_PATH)
                    repo.git.pull()
                except git.GitCommandError:
                    self._prompt.prompt_and_raise_if_not_yes("There was an error pulling the calibrations repo.\n"
                                                             "Manually pull it. Path='{}'".format(CALIBRATION_PATH))

    def check_java_installation(self):
        """
        Checks Java installation
        """
        with Task("Install java", self._prompt) as task:
            if task.do_step:
                java_url = "http://www.java.com/en/"
                java_installed = subprocess.call(["java", "-version"]) == 0
                if java_installed:
                    self._prompt.prompt_and_raise_if_not_yes(
                        "Confirm that the java version above is the desired version or that you have "
                        "upgraded to the desired 64-bit version from {}".format(java_url))
                else:
                    self.install_java()

                self._prompt.prompt_and_raise_if_not_yes(
                    "Is auto-update turned off? This can be checked from the Java control panel in "
                    "C:\\Program Files\\Java\\jre\\bin\\javacpl.exe")

    def install_java(self):
        """
        Installs the latest version of the Java Runtime Environment
        """
        java_url = "http://www.java.com/en/"

        if self._prompt.confirm_step("Java is not installed. Attempt automatic install?"):
                subprocess.call("msiexec.exe /qb- /l*vx %LogPath%\Java.log REBOOT=ReallySuppress UILevel=67 ALLUSERS=2 "
                                "/i jre1.8.0_11164.msi")
        else:
            self._prompt.prompt_and_raise_if_not_yes(
                "Manual install: Please go to {} to download and install the desired 64-bit version".format(java_url))
        self.check_java_installation()

    def check_git_installation(self):
        """
        Checks Git installation
        """
        git_url = "https://git-scm.com/downloads"
        with Task("Install Git", self._prompt) as task:
            if task.do_step:
                git_installed = subprocess.call(["git", "--version"]) == 0
                if git_installed:
                    self._prompt.prompt_and_raise_if_not_yes(
                        "Git installation found. Check above that you have the desired version or that you have "
                        "upgraded to the desired version from {}".format(git_url))
                else:
                    self.install_git()

    def install_git(self):
        """
        Installs the latest version of Git
        """
        git_url = "https://git-scm.com/downloads"
        if self._prompt.confirm_step("Git is not installed. Attempt automatic install?"):
                subprocess.call("Git-2.8.2-64-bit.exe /VERYSILENT /SUPPRESSMSGBOXES /CLOSEAPPLICATIONS "
                                "/LOG=\"%LogPath%\Git.log\" /NORESTART /LOADINF=\"settings.inf\"")
        else:
            self._prompt.prompt_and_raise_if_not_yes(
                "Manual install: Please go to {} to download and install the desired version.".format(git_url))
        self.check_git_installation()

    def take_screenshots(self):
        """
        take screen shots of initial system
        """
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

    def configure_com_ports(self):
        """
        Configure the COM ports
        """
        with Task("Configure COM ports", self._prompt) as task:
            if task.do_step:
                self._prompt.prompt_and_raise_if_not_yes(
                    "Using NPort Administrator (available under /Kits$/CompGroup/Utilities/), check that the COM ports "
                    "on this machine are configured to standard, i.e.:\n"
                    "- Moxa 1 starts at COM5\n"
                    "- Moxa 2 starts at COM21\n"
                    "- etc.\n")

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
        """
        Backup old directories
        """
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
            mysql_versions = [d for d in os.listdir(mysql_base_dir) if os.path.isdir(os.path.join(mysql_base_dir, d))]
            if len(mysql_versions) == 0:
                raise OSError
            else:
                if len(mysql_versions) > 1:
                    print("Warning, more than 1 version of MySQL detected. Using {}".format(mysql_versions[0]))
                mysql_dir = os.path.join(mysql_base_dir, mysql_versions[0], "bin")

        return mysql_dir

    def backup_database(self):
        """
        Backup the database
        """
        with Task("Backup database", self._prompt) as task:
            if task.do_step:
                try:
                    mysql_bin_dir = self._get_mysql_dir()
                    mysql_path = os.path.join(mysql_bin_dir, "mysql.exe")
                    mysql_admin_path = os.path.join(mysql_bin_dir, "mysqladmin.exe")
                    if not all([os.path.exists(p) for p in [mysql_path, mysql_admin_path]]):
                        raise OSError
                    if subprocess.call([mysql_path, "-u", "root", "-p", "--execute",
                                        "SET GLOBAL innodb_fast_shutdown=0"]) != 0 or \
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
        """
        Update the release notes.
        """
        with Task("Update release notes", self._prompt) as task:
            if task.do_step:
                self._prompt.prompt_and_raise_if_not_yes(
                    "Have you updated the instrument release notes at https://github.com/ISISComputingGroup/IBEX/wiki?")

    def configure_mysql(self):
        """
        Run the MySQL configuration script
        """
        with Task("Configure MySQL", self._prompt) as task:
            if task.do_step:
                self._prompt.prompt_and_raise_if_not_yes(
                    "Run config_mysql.bat in {}. \n"
                    "WARNING: performing this step will wipe all existing historical data.".format(SYSTEM_SETUP_PATH))

    def upgrade_mysql(self):
        """
        Upgrade mysql step
        """
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
        """
        Reapply any hotfixes to the build.
        """
        with Task("Reapply Hotfixes", self._prompt) as task:
            if task.do_step:
                self._prompt.prompt_and_raise_if_not_yes(
                    "Have you applied any hotfixes listed that are not fixed by the release, as on the instrument "
                    "release notes at https://github.com/ISISComputingGroup/IBEX/wiki?")

    def restart_vis(self):
        """
        Restart Vis which were running on upgrade start.
        """
        with Task("Restart VIs", self._prompt) as task:
            if task.do_step:
                self._prompt.prompt_and_raise_if_not_yes(
                    "Please restart any VIs that were running at the start of the upgrade")

    def perform_client_tests(self):
        """
        Test that the client works
        """
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
        """
        Test that the server works
        """
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
                    "correctly: http://dataweb.isis.rl.ac.uk/IbexDataweb/default.html?Instrument={}".format(
                        self._get_instrument_name()))

    def update_instlist(self):
        """
        Add the instrument to the web dashboard
        """
        with Task("Update Instrument List", self._prompt) as task:
            if task.do_step:
                self._prompt.prompt_and_raise_if_not_yes(
                    "Add the host name of the instrument to the list saved ")

    def update_web_dashboard(self):
        """
        Add the instrument to the web dashboard
        """
        with Task("Update web dashboard", self._prompt) as task:
            if task.do_step:
                self._prompt.prompt_and_raise_if_not_yes(
                    "Add the host name of the instrument to NDX_INSTS or ALL_INSTS in webserver.py in the JSON_bourne "
                    "repository.")
                self._prompt.prompt_and_raise_if_not_yes(
                    "On NDAEXTWEB1, pull the updated code and add a link to the instrument dashboard on the main "
                    "dataweb page under C:\\inetpub\\wwwroot\\DataWeb\\Dashboards\\redirect.html")
                self._prompt.prompt_and_raise_if_not_yes(
                    "Restart JSON_bourne on NDAEXTWEB1 when appropriate. (THIS WILL KILL ALL EXISTING SESSIONS)")

    def install_wiring_tables(self):
        """
        Add the instrument to the web dashboard
        """
        with Task("Install wiring tables", self._prompt) as task:
            if task.do_step:
                tables_dir = os.path.join(SETTINGS_CONFIG_PATH, self._machine_name, "configurations", "tables")
                self._prompt.prompt_and_raise_if_not_yes("Install the wiring tables in {}.".format(tables_dir))

    def inform_instrument_scientists(self):
        """
        Inform instrument scientists that the machine has been upgraded.
        """
        with Task("Inform instrument scientists", self._prompt) as task:
            if task.do_step:
                # For future reference, genie_python can send emails!
                self._prompt.prompt_and_raise_if_not_yes(
                    "Inform the instrument scientists that the upgrade has been completed")

    def create_journal_sql_schema(self):
        with Task("Create journal table SQL schema if it doesn't exist", self._prompt) as task:
            if task.do_step:
                sql_password = self._prompt.prompt("Enter the MySQL root password:", UserPrompt.ANY,
                                                   os.getenv("MYSQL_PASSWORD", "environment variable not set"))
                RunProcess(SYSTEM_SETUP_PATH, "add_journal_table.bat", prog_args=[sql_password]).run()


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

    @staticmethod
    def _should_install_utils():
        """
        Condition on which to install ibex utils (ICP_Binaries)

        :return: True if utils should be installed, False otherwise
        """
        return not os.path.exists(LABVIEW_DAE_DIR)

    def run_test_update(self):
        # TODO what is the use case?
        """
        Run a complete test upgrade on the current system
        Returns:

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
        # TODO still needed?
        self._upgrade_tasks.user_confirm_upgrade_type_on_machine('Client/Server Machine')
        self._upgrade_tasks.stop_ibex_server()
        self._upgrade_tasks.remove_old_ibex()
        self._upgrade_tasks.install_ibex_server(self._should_install_utils())
        self._upgrade_tasks.install_ibex_client()
        self._upgrade_tasks.upgrade_instrument_configuration()
        self._upgrade_tasks.create_journal_sql_schema()

    def run_instrument_update(self):
        # TODO what is the use case?
        """
        Update an instrument (just configuration and seci shortcuts)
        """

        self._upgrade_tasks.confirm("This script updates this instrument's configurations directory only. Proceed?")

        self._upgrade_tasks.stop_ibex_server()
        self._upgrade_tasks.upgrade_instrument_configuration()
        self._upgrade_tasks.create_journal_sql_schema()
        self._upgrade_tasks.update_calibrations_repository()
        self._upgrade_tasks.remove_seci_shortcuts()

    def run_instrument_install(self):
        """
        Do a first installation of IBEX on a new instrument.
        """
        self._upgrade_tasks.confirm("This script performs a first-time full installation of the IBEX server and client "
                                    "on a new instrument. Proceed?")

        self._upgrade_tasks.check_git_installation()
        self._upgrade_tasks.check_java_installation()
        #TODO self._upgrade_tasks.check_mysql_installation()
        self._upgrade_tasks.remove_seci_shortcuts()

        self._upgrade_tasks.install_ibex_server(self._should_install_utils())
        self._upgrade_tasks.install_ibex_client()
        self._upgrade_tasks.setup_config_repository()
        # self._upgrade_tasks.upgrade_instrument_configuration()  TODO needed ?
        self._upgrade_tasks.configure_mysql()
        self._upgrade_tasks.create_journal_sql_schema()
        self._upgrade_tasks.configure_com_ports()
        self._upgrade_tasks.setup_calibrations_repository()
        # self._upgrade_tasks.update_calibrations_repository()  TODO needed ?
        self._upgrade_tasks.update_release_notes()
        # self._upgrade_tasks.upgrade_mysql()  # TODO check in install
        self._upgrade_tasks.restart_vis()
        self._upgrade_tasks.install_wiring_tables()

        self._upgrade_tasks.perform_client_tests()
        self._upgrade_tasks.perform_server_tests()
        self._upgrade_tasks.update_instlist()
        self._upgrade_tasks.update_web_dashboard()
        self._upgrade_tasks.inform_instrument_scientists()

    def run_instrument_upgrade(self):
        """
        Deploy a full IBEX upgrade on an existing instrument.
        """
        self._upgrade_tasks.confirm(
            "This script performs a full upgrade of the IBEX server and client on an existing instrument. Proceed?")

        self._upgrade_tasks.user_confirm_upgrade_type_on_machine('Client/Server Machine')
        self._upgrade_tasks.stop_ibex_server()
        self._upgrade_tasks.check_git_installation()
        self._upgrade_tasks.check_java_installation()
        # TODO self._upgrade_tasks.check_mysql_installation()
        self._upgrade_tasks.take_screenshots()
        self._upgrade_tasks.backup_old_directories()
        self._upgrade_tasks.backup_database()
        self._upgrade_tasks.remove_seci_shortcuts()

        self._upgrade_tasks.install_ibex_server(self._should_install_utils())
        self._upgrade_tasks.install_ibex_client()
        self._upgrade_tasks.upgrade_instrument_configuration()
        self._upgrade_tasks.update_calibrations_repository()
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
    def __init__(self, working_dir, executable_file, executable_directory=None, press_any_key=False, prog_args=None):
        """
        Create a process that needs running

        Args:
            working_dir: working directory of the process
            executable_file: file of the process to run, e.g. a bat file
            executable_directory: the directory in which the executable file lives, if None, default, use working dir
            press_any_key: if true then press a key to finish the run process
            prog_args(list[string]): arguments to pass to the program
        """
        self._working_dir = working_dir
        self._bat_file = executable_file
        self._press_any_key = press_any_key
        self._prog_args = prog_args
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
            if self._press_any_key:
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
            raise ErrorInRun("Command failed with error: {0}".format(ex))
        except WindowsError as ex:
            if ex.errno == 2:
                raise ErrorInRun("Command '{cmd}' not found in '{cwd}'".format(
                    cmd=self._bat_file, cwd=self._working_dir))
            elif ex.errno == 22:
                raise ErrorInRun("Directory not found to run command '{cmd}', command is in :  '{cwd}'".format(
                    cmd=self._bat_file, cwd=self._working_dir))
            raise ex
