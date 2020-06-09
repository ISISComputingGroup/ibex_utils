import datetime
import pprint
import shutil

import os
import subprocess

try:
    from contextlib import contextmanager
except ImportError:
    from contextlib2 import contextmanager

import git

from ibex_install_utils.exceptions import ErrorInTask, ErrorInRun
from ibex_install_utils.motor_params import get_params_and_save_to_file
from ibex_install_utils.run_process import RunProcess
from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import APPS_BASE_DIR, INSTRUMENT_BASE_DIR, VAR_DIR, EPICS_PATH, \
    SETTINGS_CONFIG_PATH, SETTINGS_CONFIG_FOLDER

CONFIG_UPGRADE_SCRIPT_DIR = os.path.join(EPICS_PATH, "misc", "upgrade", "master")

CALIBRATION_PATH = os.path.join(SETTINGS_CONFIG_PATH, "common")

SOURCE_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
SOURCE_MACHINE_SETTINGS_CONFIG_PATH = os.path.join(SOURCE_FOLDER, SETTINGS_CONFIG_FOLDER, "NDXOTHER")
SOURCE_MACHINE_SETTINGS_COMMON_PATH = os.path.join(SOURCE_FOLDER, SETTINGS_CONFIG_FOLDER, "common")

PV_BACKUPS_DIR = os.path.join(VAR_DIR, "deployment_pv_backups")


class ServerTasks(BaseTasks):
    """
    Tasks relating to installing or maintaining an IBEX server and it's associated configuration files.
    """

    @staticmethod
    def _get_config_path():

        """
        Returns:
            The path to the instrument's configurations directory

        """
        return os.path.join(INSTRUMENT_BASE_DIR, SETTINGS_CONFIG_FOLDER, ServerTasks._get_machine_name())

    @task("Removing old settings file")
    def remove_settings(self):
        """
        remove old settings
        Returns:

        """
        self._file_utils.remove_tree(SETTINGS_CONFIG_PATH, self.prompt)

    @task("Install settings")
    def install_settings(self):
        """
        Install new settings from the current folder
        Returns:

        """

        self._file_utils.mkdir_recursive(SETTINGS_CONFIG_PATH)
        settings_path = os.path.join(SETTINGS_CONFIG_PATH, ServerTasks._get_machine_name())

        shutil.copytree(SOURCE_MACHINE_SETTINGS_CONFIG_PATH, settings_path)

        inst_name = BaseTasks._get_machine_name().lower()
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

    @task("Set up configuration repository")
    def setup_config_repository(self):
        """
        Creates the configuration repository, and swaps or creates a branch for the instrument.

        """
        inst_name = BaseTasks._get_machine_name()

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
                repo = git.Repo(os.path.join(SETTINGS_CONFIG_PATH, BaseTasks._get_machine_name()))
                if repo.active_branch.name != BaseTasks._get_machine_name():
                    print("Git branch, '{}', is not the same as machine name ,'{}' ".format(
                        repo.active_branch, BaseTasks._get_machine_name()))
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

    @task("Upgrading instrument configuration")
    def merge_changes_from_ticket_5262(self):
        """
        Merge the changes from ticket 5262 into the configs repository
        """
        try:
            repo = git.Repo(os.path.join(SETTINGS_CONFIG_PATH, BaseTasks._get_machine_name()))
            if repo.active_branch.name != BaseTasks._get_machine_name():
                print("Git branch, '{}', is not the same as machine name ,'{}' ".format(
                    repo.active_branch, BaseTasks._get_machine_name()))
                print("Error doing ticket 5262 merge, please perform the merge manually".format(e))
                self.prompt.prompt_and_raise_if_not_yes("Confirm when complete [y/n]")
            else:
                print(" fetch: {}".format(repo.git.fetch()))
                print(" merge: {}".format(repo.git.merge("origin/{}_Ticket5262".format(BaseTasks._get_machine_name()))))

                if BaseTasks._get_machine_name() in ["NDXLARMOR", "NDXMERLIN"]:
                    print(" merge 2: {}".format(
                        repo.git.merge("origin/{}_update_genie".format(BaseTasks._get_machine_name()))))
        except git.GitCommandError as e:
            print("Error doing ticket 5262 merge, please perform the merge manually".format(e))
            self.prompt.prompt_and_raise_if_not_yes("Confirm when complete [y/n]")

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

    @task("Install wiring tables")
    def install_wiring_tables(self):
        """
        Prompt user to install wiring tables in the appropriate folder.
        """
        tables_dir = os.path.join(SETTINGS_CONFIG_PATH, BaseTasks._get_machine_name(), "configurations", "tables")
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
                                .format(name, datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S'), extension))

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