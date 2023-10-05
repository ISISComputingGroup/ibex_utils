import datetime
import multiprocessing.dummy as multiprocessing
import os
import pprint
import shutil
import subprocess
import tempfile
import time

import lxml.etree
from ibex_install_utils.user_prompt import UserPrompt

try:
    from contextlib import contextmanager
except ImportError:
    from contextlib2 import contextmanager

import git
from ibex_install_utils.admin_runner import AdminCommandBuilder
from ibex_install_utils.exceptions import ErrorInRun, ErrorInTask
from ibex_install_utils.file_utils import LABVIEW_DAE_DIR, FileUtils
from ibex_install_utils.motor_params import get_params_and_save_to_file
from ibex_install_utils.run_process import RunProcess
from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import (
    APPS_BASE_DIR,
    EPICS_IOC_PATH,
    EPICS_PATH,
    INST_SHARE_AREA,
    INSTRUMENT_BASE_DIR,
    SETTINGS_CONFIG_FOLDER,
    SETTINGS_CONFIG_PATH,
    VAR_DIR,
)

CONFIG_UPGRADE_SCRIPT_DIR = os.path.join(EPICS_PATH, "misc", "upgrade", "master")

CALIBRATION_PATH = os.path.join(SETTINGS_CONFIG_PATH, "common")

INST_SCRIPTS_PATH = os.path.join(INSTRUMENT_BASE_DIR, "Scripts")

SOURCE_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
SOURCE_MACHINE_SETTINGS_CONFIG_PATH = os.path.join(
    SOURCE_FOLDER, SETTINGS_CONFIG_FOLDER, "NDXOTHER"
)
SOURCE_MACHINE_SETTINGS_COMMON_PATH = os.path.join(
    SOURCE_FOLDER, SETTINGS_CONFIG_FOLDER, "common"
)

PV_BACKUPS_DIR = os.path.join(VAR_DIR, "deployment_pv_backups")

# This is needed for the DAE patch detailed in https://github.com/ISISComputingGroup/IBEX/issues/5164
RELEASE_5_5_0_ISISDAE_DIR = os.path.join(
    INST_SHARE_AREA,
    "Kits$",
    "CompGroup",
    "ICP",
    "Releases",
    "5.5.0",
    "EPICS",
    "ioc",
    "master",
    "ISISDAE",
    "bin",
    "windows-x64",
)


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
        return os.path.join(
            INSTRUMENT_BASE_DIR, SETTINGS_CONFIG_FOLDER, ServerTasks._get_machine_name()
        )

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
        settings_path = os.path.join(
            SETTINGS_CONFIG_PATH, ServerTasks._get_machine_name()
        )

        shutil.copytree(SOURCE_MACHINE_SETTINGS_CONFIG_PATH, settings_path)

        inst_name = BaseTasks._get_machine_name().lower()
        for p in ["ndx", "nde"]:
            if inst_name.startswith(p):
                inst_name = inst_name.lower()[len(p) :]
                break
        inst_name = inst_name.replace("-", "_")
        self._file_utils.move_file(
            os.path.join(settings_path, "Python", "init_inst_name.py"),
            os.path.join(settings_path, "Python", f"init_{inst_name}.py"),
            self.prompt,
        )

        shutil.copytree(
            SOURCE_MACHINE_SETTINGS_COMMON_PATH,
            os.path.join(SETTINGS_CONFIG_PATH, "common"),
        )

    @task("Installing IBEX Server")
    def install_ibex_server(self, use_old_galil=None):
        """
        Install ibex server.
        Args:
            use_old_galil(bool): whether to restore old galil driver version
        """
        if use_old_galil is None:
            use_old_galil = self.select_galil_driver()
        self._file_utils.mkdir_recursive(APPS_BASE_DIR)
        RunProcess(
            self._server_source_dir, "install_to_inst.bat", prog_args=["NOLOG"]
        ).run()
        self._swap_galil_driver(use_old_galil)

    @task("Set up configuration repository")
    def setup_config_repository(self):
        """
        Creates the configuration repository, and swaps or creates a branch for the instrument.

        """
        inst_name = BaseTasks._get_machine_name()

        RunProcess(
            working_dir=os.curdir,
            executable_file="git",
            executable_directory="",
            prog_args=["config", "--global", "core.autocrlf", "true"],
        ).run()
        RunProcess(
            working_dir=os.curdir,
            executable_file="git",
            executable_directory="",
            prog_args=["config", "--global", "credential.helper", "wincred"],
        ).run()
        RunProcess(
            working_dir=os.curdir,
            executable_file="git",
            executable_directory="",
            prog_args=["config", "--global", "user.name", "spudulike"],
        ).run()
        email = f"spudulike@{inst_name.lower()}.isis.cclrc.ac.uk"
        RunProcess(
            working_dir=os.curdir,
            executable_file="git",
            executable_directory="",
            prog_args=["config", "--global", "user.email", email],
        ).run()

        if not os.path.exists(SETTINGS_CONFIG_PATH):
            os.makedirs(SETTINGS_CONFIG_PATH)

        configs_url = "http://spudulike@control-svcs.isis.cclrc.ac.uk/gitroot/instconfigs/inst.git"
        RunProcess(
            working_dir=SETTINGS_CONFIG_PATH,
            executable_file="git",
            executable_directory="",
            prog_args=["clone", configs_url, inst_name],
        ).run()

        inst_config_path = os.path.join(SETTINGS_CONFIG_PATH, inst_name)
        RunProcess(
            working_dir=inst_config_path,
            executable_file="git",
            executable_directory="",
            prog_args=["pull"],
        ).run()

        try:
            RunProcess(
                working_dir=inst_config_path,
                executable_file="git",
                executable_directory="",
                prog_args=["checkout", inst_name],
            ).run()
        except ErrorInRun:
            RunProcess(
                working_dir=inst_config_path,
                executable_file="git",
                executable_directory="",
                prog_args=["checkout", "-b", inst_name],
            ).run()

        inst_scripts_path = os.path.join(inst_config_path, "Python")

        generic_inst_file = os.path.join(inst_scripts_path, "init_inst_name.py")

        # Specific inst file postfix is inst_name.lower()[3:] as we need to trim off NDE/NDX/NDH/NDW
        specific_inst_file = os.path.join(
            inst_scripts_path, f"init_{inst_name.lower()[3:]}.py"
        )

        if not os.path.exists(os.path.join(inst_scripts_path, specific_inst_file)):
            try:
                if not os.path.exists(specific_inst_file):
                    if not os.path.exists(generic_inst_file):
                        raise IOError(
                            "Generic inst file at {} did not exist - cannot proceed".format(
                                generic_inst_file
                            )
                        )
                    os.rename(generic_inst_file, specific_inst_file)
                RunProcess(
                    working_dir=inst_scripts_path,
                    executable_file="git",
                    executable_directory="",
                    prog_args=["add", f"init_{inst_name.lower()}.py"],
                ).run()
                RunProcess(
                    working_dir=inst_scripts_path,
                    executable_file="git",
                    executable_directory="",
                    prog_args=["rm", "init_inst_name.py"],
                ).run()
                RunProcess(
                    working_dir=inst_config_path,
                    executable_file="git",
                    executable_directory="",
                    prog_args=["commit", "-m", "create initial python"],
                ).run()
                RunProcess(
                    working_dir=inst_config_path,
                    executable_file="git",
                    executable_directory="",
                    prog_args=["push", "--set-upstream", "origin", inst_name],
                ).run()
            except Exception as e:
                self.prompt.prompt_and_raise_if_not_yes(
                    f"Something went wrong setting up the configurations repository. Please resolve manually, "
                    f"instructions are in the developers manual under "
                    f"First-time-installing-and-building-(Windows): \n {e}"
                )

    @task("Upgrading instrument configuration")
    def upgrade_instrument_configuration(self):
        """
        Update the configuration on the instrument using its upgrade config script.
        """
        manual_prompt = (
            "Merge the master configurations branch into the instrument configuration. "
            "From C:\Instrument\Settings\config\[machine name] run:\n"
            "    0. Clean up any in progress merge (e.g. git merge --abort)\n"
            "    1. git checkout master\n"
            "    2. git pull\n"
            "    3. git checkout [machine name]\n"
            "    4. git merge master\n"
            "    5. Resolve any merge conflicts\n"
            "    6. git push\n"
        )
        automatic_prompt = "Attempt automatic configuration merge?"
        if self.prompt.confirm_step(automatic_prompt):
            try:
                repo = git.Repo(
                    os.path.join(SETTINGS_CONFIG_PATH, BaseTasks._get_machine_name())
                )
                if repo.active_branch.name != BaseTasks._get_machine_name():
                    print(
                        f"Git branch, '{repo.active_branch}', is not the same as machine name ,'{BaseTasks._get_machine_name()}' "
                    )
                    raise ErrorInTask("Git branch is not the same as machine name")
                else:
                    print(f"     fetch: {repo.git.fetch()}")
                    print("     merge: {}".format(repo.git.merge("origin/master")))
                    # no longer push let the instrument do that on start up if needed
            except git.GitCommandError as e:
                print(
                    f"Error doing automatic merge, please perform the merge manually: {e}"
                )
                self.prompt.prompt_and_raise_if_not_yes(manual_prompt)
        else:
            self.prompt.prompt_and_raise_if_not_yes(manual_prompt)

        RunProcess(CONFIG_UPGRADE_SCRIPT_DIR, "upgrade.bat", capture_pipes=False).run()

    @task("Install shared instrument scripts repository")
    def install_shared_scripts_repository(self):
        """
        Install shared instrument scripts repository containing
        """
        if os.path.isdir(INST_SCRIPTS_PATH):
            if (
                self.prompt.prompt(
                    "Scripts directory already exists. Update Scripts repository?",
                    ["Y", "N"],
                    "Y",
                )
                == "Y"
            ):
                self.update_shared_scripts_repository()
        else:
            repo_url = "https://github.com/ISISNeutronMuon/InstrumentScripts.git"
            RunProcess(
                working_dir=os.curdir,
                executable_file="git",
                executable_directory="",
                prog_args=["clone", repo_url, INST_SCRIPTS_PATH],
            ).run()

    @task("Set up shared instrument scripts library")
    def update_shared_scripts_repository(self):
        """
        Update the shared instrument scripts repository containing
        """
        try:
            repo = git.Repo(INST_SCRIPTS_PATH)
            repo.git.pull()
        except git.GitCommandError:
            self.prompt.prompt_and_raise_if_not_yes(
                "There was an error pulling the shared scripts repo.\n"
                "Manually pull it. Path='{}'".format(INST_SCRIPTS_PATH)
            )

    @task("Set up calibrations repository")
    def setup_calibrations_repository(self):
        """
        Set up the calibration repository
        """
        if os.path.isdir(CALIBRATION_PATH):
            if (
                self.prompt.prompt(
                    "Calibrations directory already exists. Update calibrations repository?",
                    ["Y", "N"],
                    "N",
                )
                == "Y"
            ):
                self.update_calibrations_repository()
        else:
            repo_url = (
                "http://control-svcs.isis.cclrc.ac.uk/gitroot/instconfigs/common.git"
            )
            location = "C:\Instrument\Settings\config\common"
            RunProcess(
                working_dir=os.curdir,
                executable_file="git",
                executable_directory="",
                prog_args=["clone", repo_url, location],
            ).run()

    @task("Updating calibrations repository")
    def update_calibrations_repository(self):
        """
        Update the calibration repository
        """
        try:
            repo = git.Repo(CALIBRATION_PATH)
            repo.git.pull()
        except git.GitCommandError:
            self.prompt.prompt_and_raise_if_not_yes(
                "There was an error pulling the calibrations repo.\n"
                "Manually pull it. Path='{}'".format(CALIBRATION_PATH)
            )

    @task("Server release tests")
    def perform_server_tests(self):
        """
        Test that the server works
        """
        server_release_tests_url = (
            "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/"
            "Server-Release-Tests"
        )

        print(f"For further details, see {server_release_tests_url}")
        self.prompt.prompt_and_raise_if_not_yes(
            "Check that blocks are logging as expected"
        )

        print(
            "Checking that configurations are being pushed to the appropriate repository"
        )
        repo = git.Repo(self._get_config_path())
        repo.git.fetch()
        status = repo.git.status()
        print(f"Current repository status is: {status}")
        if f"up-to-date with 'origin/{self._get_machine_name()}" in status:
            print("Configurations updating correctly")
        else:
            self.prompt.prompt_and_raise_if_not_yes(
                "Unexpected git status. Please confirm that configurations are being pushed to the appropriate "
                "remote repository"
            )

        self.prompt.prompt_and_raise_if_not_yes(
            f"Check that the web dashboard for this instrument is updating "
            f"correctly: http://dataweb.isis.rl.ac.uk/IbexDataweb/default.html?Instrument={self._get_instrument_name()}"
        )

    @task("Install wiring tables")
    def install_wiring_tables(self):
        """
        Prompt user to install wiring tables in the appropriate folder.
        """
        tables_dir = os.path.join(
            SETTINGS_CONFIG_PATH,
            BaseTasks._get_machine_name(),
            "configurations",
            "tables",
        )
        self.prompt.prompt_and_raise_if_not_yes(
            f"Install the wiring tables in {tables_dir}."
        )

    @task("Configure motion setpoints")
    def configure_motion(self):
        """
        Prompt user to configure Galils
        """
        url = (
            "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/"
            "Deployment-on-an-Instrument-Control-PC#set-up-motion-set-points"
        )
        if (
            self.prompt.prompt(
                "Please configure the motion set points for this instrument. Instructions can be"
                " found on the developer wiki. Open instructions in browser now?",
                ["Y", "N"],
                "N",
            )
            == "Y"
        ):
            subprocess.call(f"explorer {url}")
        self.prompt.prompt_and_raise_if_not_yes(
            "Confirm motion set points have been configured."
        )

    @contextmanager
    def timestamped_pv_backups_file(self, name, directory, extension="txt"):
        """
        Context manager to create a timestamped file in the pv backups directory

        Args:
            name (str): path to the file
            directory (str): directory of file
            extension (str): the extension of the file
        """
        filename = os.path.join(
            PV_BACKUPS_DIR,
            directory,
            "{}_{}.{}".format(
                name, datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S"), extension
            ),
        )

        if not os.path.exists(os.path.join(PV_BACKUPS_DIR, directory)):
            os.makedirs(os.path.join(PV_BACKUPS_DIR, directory))

        with open(filename, "w") as f:
            yield f

    @task("Backup motors, blocks and blockserver to csv files")
    def save_motor_blocks_blockserver_to_file(self):
        """
        Saves the motor, blocks and blockserver to csv file.

        """
        print("NOTE: Blocks and blockserver will finish much quicker than motors backup")
        motor_backup = multiprocessing.Process(target=self.save_motor_parameters_to_file)
        block_backup = multiprocessing.Process(target=self.save_blocks_to_file)
        blockserver_backup = multiprocessing.Process(target=self.save_blockserver_pv_to_file)
       
        
        block_backup.start()
        blockserver_backup.start()
        
        
        block_backup.join()
        blockserver_backup.join()

        # motor backup done on its own as for unknown reasons if not it will hang
        motor_backup.start()
        motor_backup.join()

    def save_motor_parameters_to_file(self):
        """
        Saves the motor parameters to csv file.
        """

        with self.timestamped_pv_backups_file(
            name="motors", directory="motors", extension="csv"
        ) as f:
            get_params_and_save_to_file(f)

        print("Backed up: motor params pvs")

    def save_blocks_to_file(self):
        """
        Saves block parameters in a file.
        """

        blocks = self._ca.get_blocks()
        if blocks is None:
            print("Blockserver unavailable - not archiving.")
        else:
            if blocks:
                block_processes = []
                counter = 0
                manager = multiprocessing.Manager()
                data = manager.list()
                for block in blocks:
                    data.append(" ")
                for block in blocks:
                    block_processes.append(
                        multiprocessing.Process(target=self.block_caget, args=(block, counter, data))
                    )
                    counter += 1

                for process in block_processes:
                    process.start()

                for process in block_processes:
                    process.join()
              
                counter = 0
                for block in blocks:
                    with self.timestamped_pv_backups_file(name=block, directory="blocks") as f:
                        f.write(data[counter])
                        counter += 1

            else:
                print(
                    "Blockserver available but no blocks found - not archiving anything"
                )

        print("Backed up: block pvs")

    def block_caget(self, block, counter, data):
        data[counter] = f"{self._ca.cget(block)}\r\n"

    def save_blockserver_pv_to_file(self):
        """
        Saves the blockserver PV to a file.
        """
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

        pv_processes = []
        for name, pv in pvs_to_save:
            pv_processes.append(
                multiprocessing.Process(target=self.get_pv, args=(pv, name,))
            )
        
        for process in pv_processes:
            process.start()

        for process in pv_processes:
            process.join()
           

        print("Backed up: blockserver config pvs")


    def get_pv(self, pv, name):
         def _pretty_print(data):
            return pprint.pformat(data, width=800, indent=2)

         with self.timestamped_pv_backups_file(
                directory="inst_servers", name=name
            ) as f:
                try:
                    f.write(
                        f"{_pretty_print(self._ca.get_object_from_compressed_hexed_json(pv))}\r\n"
                    )
                except:
                    pass


    @task("Update the ICP")
    def update_icp(self, icp_in_labview_modules, register_icp=True):
        """
        Updates the IPC to the latest version.
        Args:
            icp_in_labview_modules (bool): true if the ICP is in labview modules
            register_icp (bool): whether to re-register the ISISICP program (requires admin rights; interactive only)
        """
        register_icp_commands = AdminCommandBuilder()

        if icp_in_labview_modules:
            config_filepath = os.path.join(LABVIEW_DAE_DIR, "icp_config.xml")
            root = lxml.etree.parse(config_filepath)
            try:
                dae_type = int(
                    root.xpath("./I32/Name[text() = 'DAEType']/../Val/text()")[0]
                )
            except Exception as e:
                print(f"Failed to find dae_type ({e}), not installing ICP")
                return
            # If the ICP is talking to a DAE2 it's DAEType will be 1 or 2, if it's talking to a DAE3 it will be 3 or 4
            if dae_type in [1, 2]:
                dae_type = 2
            elif dae_type in [3, 4]:
                dae_type = 3
            else:
                print(f"DAE type {dae_type} not recognised, not installing ICP")
                return
            self.prompt.confirm_step(
                f"Upgrade ICP found in Labview Modules? (Detected type: DAE{dae_type})"
            )
            icp_path = FileUtils.get_latest_directory_path(
                os.path.join(
                    INST_SHARE_AREA,
                    "kits$",
                    "CompGroup",
                    "ICP",
                    "ISISICP",
                    f"DAE{dae_type}",
                ),
                "",
            )

            RunProcess(
                os.getcwd(),
                "update_inst.cmd",
                prog_args=["NOINT"],
                executable_directory=icp_path,
            ).run()

            register_icp_commands.add_command(
                f'cd /d "{LABVIEW_DAE_DIR}" && register_programs.cmd',
                "Release NOINT",
                expected_return_val=None,
            )
        else:
            self.prompt.confirm_step("Install into EPICS/ICP_Binaries")
            RunProcess(EPICS_PATH, "create_icp_binaries.bat").run()

            icp_top = os.path.join(EPICS_PATH, "ICP_Binaries", "isisdae")
            register_icp_commands.add_command(
                f'cd /d "{icp_top}" && register_programs.bat',
                "",
                expected_return_val=None,
            )

        if register_icp:
            print("ICP updated successfully, registering ICP")
            register_icp_commands.run_all()
            print("ICP registered")
        else:
            print("Not registering ICP as running a non-interactive deploy")

    @task(
        "Set username and password for alerts (only required if this is a SECI to IBEX migration)"
    )
    def set_alert_url_and_password(self):
        print(
            "The URL and password for alerts are at http://www.facilities.rl.ac.uk/isis/computing/instruments/Lists/Access/AllItems.aspx"
        )
        url = self.prompt.prompt(
            "Input URL for alerts: ", possibles=UserPrompt.ANY, default=None
        )
        password = self.prompt.prompt(
            "Input password for alerts: ", possibles=UserPrompt.ANY, default=None
        )

        if url is not None and password is not None:
            self._ca.set_pv("CS:AC:ALERTS:URL:SP", url, is_local=True)
            self._ca.set_pv("CS:AC:ALERTS:PW:SP", password, is_local=True)
        else:
            print("No username/password provided - skipping step")

    @task("Run config checker")
    def run_config_checker(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            print(f"Cloning InstrumentChecker to {tmpdir}")
            git.Repo.clone_from(
                "https://github.com/ISISComputingGroup/InstrumentChecker.git", tmpdir
            )
            print(f"Cloning configs repo to {os.path.join(tmpdir, 'configs')}")
            git.Repo.clone_from(
                "http://spudulike@control-svcs.isis.cclrc.ac.uk/gitroot/instconfigs/inst.git",
                os.path.join(tmpdir, "configs"),
            )
            print(f"Cloning GUI repo to {os.path.join(tmpdir, 'gui')}")
            git.Repo.clone_from(
                "https://github.com/ISISComputingGroup/ibex_gui.git",
                os.path.join(tmpdir, "gui"),
            )

            print("Running InstrumentChecker")
            python = os.path.join(
                "C:\\", "Instrument", "Apps", "Python3", "genie_python.bat"
            )
            args = [
                "-u",
                "run_tests.py",
                "--configs_repo_path",
                "configs",
                "--gui_repo_path",
                "gui",
                "--reports_path",
                "test-reports",
                "--instruments",
                self._get_instrument_name(),
            ]

            RunProcess(tmpdir, python, prog_args=args).run()

    def select_galil_driver(self):
        """
        Select galil driver to use. Return True if old driver in operation or should be used
        """
        # GALIL_OLD/NEW.txt file gets copied to the tmp dir by instrument_deploy.bat
        tmpdir = tempfile.gettempdir()

        if os.path.exists(os.path.join(tmpdir, "GALIL_OLD.txt")):
            os.remove(os.path.join(tmpdir, "GALIL_OLD.txt"))
            # we don't need to swap back to new GALIL for the update as install will remove all files anyway
            # we just need to record our current choice
            print(
                "Old galil driver version detected and will automatically be restored after update."
            )
            return True
        elif os.path.exists(os.path.join(tmpdir, "GALIL_NEW.txt")):
            os.remove(os.path.join(tmpdir, "GALIL_NEW.txt"))
            print(
                "New galil driver version detected and will automatically be restored after update."
            )
            return False
        else:
            print(
                "Should the old (Y) or new (N) Galil driver be the current default to run?"
            )
            print(
                "See https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/New-Galil-Driver"
            )
            answer = self.prompt.prompt(
                "Keep old Galil driver as default? [Y/N]", ["Y", "N"], "Y"
            )
            if answer == "Y":
                return True
            else:
                print(
                    "Old Galil driver is default - only change to new driver if you explicitly know this is needed!"
                )
                return not self.prompt.confirm_step("Use new Galil driver")

    def _swap_galil_driver(self, use_old):
        """
        Swap galil back to old if needed
        Args:
            use_old(bool): whether to restore old driver version
        """
        if use_old:
            print("Restoring Old galil driver version.")
            RunProcess(EPICS_PATH, "swap_galil.bat", prog_args=["OLD"]).run()

    def ioc_dir_exists(self, ioc_dirname):
        full_ioc_path = os.path.join(EPICS_IOC_PATH, ioc_dirname)
        return os.path.exists(full_ioc_path)
