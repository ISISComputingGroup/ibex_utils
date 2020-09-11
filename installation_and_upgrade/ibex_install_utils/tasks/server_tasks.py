import datetime
import pprint
import shutil
import lxml.etree
import os
import subprocess

from installation_and_upgrade.ibex_install_utils.user_prompt import UserPrompt

try:
    from contextlib import contextmanager
except ImportError:
    from contextlib2 import contextmanager

import git

from installation_and_upgrade.ibex_install_utils.exceptions import ErrorInTask, ErrorInRun
from installation_and_upgrade.ibex_install_utils.motor_params import get_params_and_save_to_file
from installation_and_upgrade.ibex_install_utils.run_process import RunProcess
from installation_and_upgrade.ibex_install_utils.task import task
from installation_and_upgrade.ibex_install_utils.tasks import BaseTasks
from installation_and_upgrade.ibex_install_utils.tasks.common_paths import APPS_BASE_DIR, INSTRUMENT_BASE_DIR, VAR_DIR, EPICS_PATH, \
    SETTINGS_CONFIG_PATH, SETTINGS_CONFIG_FOLDER, INST_SHARE_AREA
from installation_and_upgrade.ibex_install_utils.file_utils import LABVIEW_DAE_DIR, get_latest_directory_path
from installation_and_upgrade.ibex_install_utils.admin_runner import AdminCommandBuilder

CONFIG_UPGRADE_SCRIPT_DIR = os.path.join(EPICS_PATH, "misc", "upgrade", "master")

CALIBRATION_PATH = os.path.join(SETTINGS_CONFIG_PATH, "common")

SOURCE_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
SOURCE_MACHINE_SETTINGS_CONFIG_PATH = os.path.join(SOURCE_FOLDER, SETTINGS_CONFIG_FOLDER, "NDXOTHER")
SOURCE_MACHINE_SETTINGS_COMMON_PATH = os.path.join(SOURCE_FOLDER, SETTINGS_CONFIG_FOLDER, "common")

PV_BACKUPS_DIR = os.path.join(VAR_DIR, "deployment_pv_backups")

# This is needed for the DAE patch detailed in https://github.com/ISISComputingGroup/IBEX/issues/5164
RELEASE_5_5_0_ISISDAE_DIR = os.path.join(INST_SHARE_AREA, "Kits$", "CompGroup", "ICP", "Releases", "5.5.0", "EPICS",
                                         "ioc", "master", "ISISDAE", "bin", "windows-x64")


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
            os.path.join(settings_path, "Python", f"init_{inst_name}.py"),
            self.prompt)

        shutil.copytree(SOURCE_MACHINE_SETTINGS_COMMON_PATH, os.path.join(SETTINGS_CONFIG_PATH, "common"))

    @task("Installing IBEX Server")
    def install_ibex_server(self):
        """
        Install ibex server.
        """
        self._file_utils.mkdir_recursive(APPS_BASE_DIR)
        RunProcess(self._server_source_dir, "install_to_inst.bat", prog_args=["NOLOG"]).run()

    @task("Set up configuration repository")
    def setup_config_repository(self):
        """
        Creates the configuration repository, and swaps or creates a branch for the instrument.

        """
        inst_name = BaseTasks._get_machine_name()

        subprocess.call("git config --global core.autocrlf true")
        subprocess.call("git config --global credential.helper wincred")
        subprocess.call("git config --global user.name spudulike")
        set_user_email = f"git config --global user.email spudulike@{inst_name.lower()}.isis.cclrc.ac.uk"
        subprocess.call(set_user_email)

        if not os.path.exists(SETTINGS_CONFIG_PATH):
            os.makedirs(SETTINGS_CONFIG_PATH)

        subprocess.call(
            f"git clone http://spudulike@control-svcs.isis.cclrc.ac.uk/gitroot/instconfigs/inst.git {inst_name}", cwd=SETTINGS_CONFIG_PATH)

        inst_config_path = os.path.join(SETTINGS_CONFIG_PATH, inst_name)
        subprocess.call("git pull", cwd=inst_config_path)

        branch_exists = subprocess.call(f"git checkout {inst_name}", cwd=inst_config_path) == 0
        if not branch_exists:
            subprocess.call(f"git checkout -b {inst_name}", cwd=inst_config_path)

        inst_scripts_path = os.path.join(inst_config_path, "Python")
        if not os.path.exists(os.path.join(inst_scripts_path, f"init_{inst_name.lower()}.py")):
            try:
                os.rename(os.path.join(inst_scripts_path, "init_inst_name.py"),
                          os.path.join(inst_scripts_path, f"init_{inst_name.lower()}.py"))
                subprocess.call(f"git add init_{inst_name.lower()}.py", cwd=inst_scripts_path)
                subprocess.call("git rm init_inst_name.py", cwd=inst_scripts_path)
                subprocess.call('git commit -m"create initial python"', cwd=inst_config_path)
                subprocess.call(f"git push --set-upstream origin {inst_name}", cwd=inst_config_path)
            except Exception as e:
                self.prompt.prompt_and_raise_if_not_yes(
                    f"Something went wrong setting up the configurations repository. Please resolve manually, "
                    f"instructions are in the developers manual under "
                    f"First-time-installing-and-building-(Windows): \n {e}")

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
                    print(f"Git branch, '{repo.active_branch}', is not the same as machine name ,'{BaseTasks._get_machine_name()}' ")
                    raise ErrorInTask("Git branch is not the same as machine name")
                else:
                    print(f"     fetch: {repo.git.fetch()}")
                    print("     merge: {}".format(repo.git.merge("origin/master")))
                    # no longer push let the instrument do that on start up if needed
            except git.GitCommandError as e:
                print("Error doing automatic merge, please perform the merge manually: {}".format(e))
                self.prompt.prompt_and_raise_if_not_yes(manual_prompt)
        else:
            self.prompt.prompt_and_raise_if_not_yes(manual_prompt)

        RunProcess(CONFIG_UPGRADE_SCRIPT_DIR, "upgrade.bat", capture_pipes=False).run()

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
                    print(f"Couldn't get data from {pv} because: {e}")
                    f.write(e)

    @task("Update the ICP")
    def update_icp(self, icp_in_labview_modules, register_icp=True):
        """
        Updates the IPC to the latest version.
        Args:
            icp_in_labview_modules (bool): true if the ICP is in labview modules
            register_icp (bool): whether to re-register the ISISICP program (requires admin rights; interactive only)
        """
        register_icp_commands = AdminCommandBuilder()

        if BaseTasks._get_machine_name() == "NDEMUONFE":
            print("NDEMUONFE requires an old IOC")
            for filename in os.listdir(RELEASE_5_5_0_ISISDAE_DIR):
                if filename.lower() == "isisdae-ioc-01.exe":
                    continue

                source_path = os.path.join(RELEASE_5_5_0_ISISDAE_DIR, filename)
                dest_path = os.path.join(EPICS_PATH, "ioc", "master", "ISISDAE", "bin", "windows-x64", filename)

                print("Patching {}".format(filename))
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.copy2(source_path, dest_path)
            print("ISISDAE successfully patched")
            return

        if icp_in_labview_modules:
            config_filepath = os.path.join(LABVIEW_DAE_DIR, "icp_config.xml")
            root = lxml.etree.parse(config_filepath)
            try:
                dae_type = int(root.xpath("./I32/Name[text() = 'DAEType']/../Val/text()")[0])
            except Exception as e:
                print("Failed to find dae_type ({}), not installing ICP".format(e))
                return
            # If the ICP is talking to a DAE2 it's DAEType will be 1 or 2, if it's talking to a DAE3 it will be 3 or 4
            if dae_type in [1, 2]:
                dae_type = 2
            elif dae_type in [3, 4]:
                dae_type = 3
            else:
                print("DAE type {} not recognised, not installing ICP".format(dae_type))
                return
            self.prompt.confirm_step("Upgrade DAE{} type ICP found in Labview Modules".format(dae_type))
            icp_path = get_latest_directory_path(os.path.join(INST_SHARE_AREA, "kits$", "CompGroup", "ICP", "ISISICP",
                                                              "DAE{}".format(dae_type)), "")

            RunProcess(os.getcwd(), "update_inst.cmd", prog_args=["NOINT"], executable_directory=icp_path).run()

            register_icp_commands.add_command('cd "{}" && register_programs.cmd'.format(LABVIEW_DAE_DIR),
                                              "Release NOINT", expected_return_val=None)
        else:
            self.prompt.confirm_step("Install into EPICS/ICP_Binaries")
            RunProcess(EPICS_PATH, "create_icp_binaries.bat").run()

            icp_exe_path = os.path.join(EPICS_PATH, "ICP_Binaries", "isisdae", "x64", "Release")
            register_icp_commands.add_command(os.path.join(icp_exe_path, "isisicp.exe"), r"/RegServer")
            register_icp_commands.add_command(os.path.join(icp_exe_path, "isisdatasvr.exe"), r"/RegServer")

        if register_icp:
            print("ICP updated successfully, registering ICP")
            register_icp_commands.run_all()
            print("ICP registered")
        else:
            print("Not registering ICP as running a non-interactive deploy")

    @task("Set username and password for alerts (only required if this is a SECI to IBEX migration)")
    def set_alert_url_and_password(self):
        print("The URL and password for alerts are at http://www.facilities.rl.ac.uk/isis/computing/instruments/Lists/Access/AllItems.aspx")
        url = self.prompt.prompt("Input URL for alerts: ", possibles=UserPrompt.ANY, default=None)
        password = self.prompt.prompt("Input password for alerts: ", possibles=UserPrompt.ANY, default=None)

        if url is not None and password is not None:
            self._ca.set_pv("CS:AC:ALERTS:URL:SP", url, is_local=True)
            self._ca.set_pv("CS:AC:ALERTS:PW:SP", password, is_local=True)
        else:
            print("No username/password provided - skipping step")

