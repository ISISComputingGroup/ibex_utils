import glob
import os
import shutil
import subprocess
import time
from pathlib import Path
from time import sleep

import psutil
from ibex_install_utils.admin_runner import AdminCommandBuilder
from ibex_install_utils.exceptions import ErrorInTask, UserStop
from ibex_install_utils.kafka_utils import add_required_topics
from ibex_install_utils.run_process import RunProcess
from ibex_install_utils.software_dependency.git import Git
from ibex_install_utils.software_dependency.java import Java
from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import APPS_BASE_DIR, EPICS_PATH, VAR_DIR
from ibex_install_utils.version_check import version_check
from win32com.client import Dispatch

GIGABYTE = 1024**3

RAM_MIN = 7.5 * GIGABYTE  # 8 GB minus a small tolerance.
RAM_NORMAL_INSTRUMENT = 13 * GIGABYTE  # Should be 14GB ideally, but allow anything over 13GB.
FREE_DISK_MIN = 30 * GIGABYTE

CURRENT_USER = os.getlogin()
USER_STARTUP = os.path.join(
    "C:\\",
    "Users",
    CURRENT_USER,
    "AppData",
    "Roaming",
    "Microsoft",
    "Windows",
    "Start Menu",
    "Programs",
    "Startup",
)
ALLUSERS_STARTUP = os.path.join(
    "C:\\", "ProgramData", "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
)

SECI = "SECI User interface.lnk"
SECI_ONE_PATH = os.path.join("C:\\", "Program Files (x86)", "CCLRC ISIS Facility")
SECI_AUTOSTART_LOCATIONS = [os.path.join(USER_STARTUP, SECI), os.path.join(ALLUSERS_STARTUP, SECI)]
EPICS_CRTL_PATH = os.path.join(EPICS_PATH, "crtl")


DESKTOP_TRAINING_FOLDER_PATH = os.path.join(
    os.environ["userprofile"], "desktop", "Mantid+IBEX training"
)


class SystemTasks(BaseTasks):
    """
    Tasks relating to the system e.g. installed software other than core IBEX components, windows,
     firewalls, etc.
    """


    @task("Upgrading Notepad++. Please follow system dialogs")
    def upgrade_notepad_pp(self) -> None:
        """
        Install (start installation of) notepad ++
        Returns:

        """
        RunProcess(
            working_dir=APPS_BASE_DIR,
            executable_file="GUP.exe",
            executable_directory=os.path.join(
                "C:\\", "Program Files (x86)", "Notepad++", "updater"
            ),
        ).run()

    @task("Removing training folder on desktop ...")
    def clean_up_desktop_ibex_training_folder(self) -> None:
        """
        Remove training folder from the desktop
        Returns:

        """
        self._file_utils.remove_tree(DESKTOP_TRAINING_FOLDER_PATH, self.prompt)

    @task("Remove SECI shortcuts")
    def remove_seci_shortcuts(self) -> None:
        """
        Remove (or at least ask the user to remove) all Seci shortcuts
        """
        for path in SECI_AUTOSTART_LOCATIONS:
            if os.path.exists(path):
                self.prompt.prompt_and_raise_if_not_yes(
                    f"SECI autostart found in {path}, delete this."
                )

        self.prompt.prompt_and_raise_if_not_yes("Remove task bar shortcut to SECI")
        self.prompt.prompt_and_raise_if_not_yes("Remove desktop shortcut to SECI")
        self.prompt.prompt_and_raise_if_not_yes("Remove start menu shortcut to SECI")

    @task("Remove Treesize shortcuts")
    def remove_treesize_shortcuts(self) -> None:
        """
        Remove (or at least ask the user to remove) all Treesize shortcuts.

        For justification see https://github.com/ISISComputingGroup/IBEX/issues/4214
        """
        self.prompt.prompt_and_raise_if_not_yes("Remove task bar shortcut to Treesize if it exists")
        self.prompt.prompt_and_raise_if_not_yes("Remove desktop shortcut to Treesize if it exists")
        self.prompt.prompt_and_raise_if_not_yes(
            "Remove start menu shortcut to Treesize if it exists"
        )

    @task("Remove SECI 1 Path")
    def remove_seci_one(self) -> None:
        """
        Removes SECI 1
        """
        if os.path.exists(SECI_ONE_PATH):
            try:
                self._file_utils.remove_tree(SECI_ONE_PATH, self.prompt, use_robocopy=False)
            except (IOError, WindowsError) as e:
                self.prompt.prompt_and_raise_if_not_yes(
                    f"Failed to remove SECI 1 (located in '{SECI_ONE_PATH}') "
                    f"because '{e}'. Please remove it manually and type 'Y'"
                    f" to confirm"
                )

    @version_check(Java())
    @task("Install java")
    def check_java_installation(self) -> None:
        """
        Checks Java installation
        """
        installer, _ = Java().find_latest()

        if os.path.exists(installer):
            print(f"Running installer at ({installer})...")
            subprocess.call(f"msiexec /i {installer}")
            self.prompt.prompt_and_raise_if_not_yes(
                "Make sure java installed correctly.\r\n"
                "After following the installer, ensure you close and then re-open"
                " your remote desktop session (This "
                "is a workaround for windows not immediately picking up new environment variables)"
            )
        else:
            self.prompt.prompt_and_raise_if_not_yes(
                "Upgrade openJDK installation by following:\r\n"
                "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Upgrade-Java\r\n\r\n"
                "After following the installer, ensure you close and then re-open"
                " your remote desktop session (This "
                "is a workaround for windows not immediately picking up new environment variables)"
            )

    @task("Configure COM ports")
    def configure_com_ports(self) -> None:
        """
        Configure the COM ports
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Using NPort Administrator (available under /Kits$/CompGroup/Utilities/), "
            "check that the COM ports "
            "on this machine are configured to standard, i.e.:\n"
            "- Moxa 1 starts at COM5\n"
            "- Moxa 2 starts at COM21\n"
            "- etc.\n"
        )

    @task("Restart VIs")
    def restart_vis(self) -> None:
        """
        Restart Vis which were running on upgrade start.
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Please restart any VIs that were running at the start of the upgrade"
        )

    @task("Update Instrument List")
    def update_instlist(self) -> None:
        """
        Prompt user to add instrument to the list of known IBEX instruments
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Add the host name of the instrument to the list saved in the CS:INSTLIST PV"
        )

    @task("Update kafka topics")
    def update_kafka_topics(self) -> None:
        """
        Adds the required kafka topics to the cluster.
        """
        add_required_topics("livedata.isis.cclrc.ac.uk:9092", self._get_instrument_name())

    @task("Add Nagios checks")
    def add_nagios_checks(self) -> None:
        """
        Prompt user to add nagios checks.
        """
        # For future reference, genie_python can send emails!
        self.prompt.prompt_and_raise_if_not_yes(
            "Add this instrument to the Nagios monitoring system. Talk to "
            "Freddie Akeroyd for help with this."
        )

    @task("Inform instrument scientists")
    def inform_instrument_scientists(self) -> None:
        """
        Inform instrument scientists that the machine has been upgraded.
        """
        # For future reference, genie_python can send emails!
        ibex_version = (
            self._ibex_version if self._ibex_version is not None else "<Insert version number here>"
        )
        email_template = f"""Please send the following email to your instrument scientists:
                    Hello,
                    We have finished the upgrade of {BaseTasks._get_machine_name()} to IBEX {ibex_version}.
                    The release notes for this are at the following link: https://github.com/ISISComputingGroup/IBEX/wiki/Release-Notes-v{ibex_version}

                    Please let us know if you have any queries or find any problems with the upgrade.
                    Thank you,
                    <your name>"""  # noqa: E501

        self.prompt.prompt_and_raise_if_not_yes(email_template)

    @task("Clear/reapply hotfixes")
    def clear_or_reapply_hotfixes(self) -> None:
        """
        Apply any changes noted in the release notes.
        """
        # For future reference, genie_python can send emails!
        self.prompt.prompt_and_raise_if_not_yes(
            "Have you cleared/reapplied hotfixes listed in https://github.com/ISISComputingGroup/IBEX/wiki#instrument-information--hotfixes?"
        )

    def check_resources(self) -> None:
        """
        Check the machine's resources meet minimum requirements.
        """
        self.check_virtual_memory()
        self._check_disk_usage()

    @task("Check virtual machine memory")
    def check_virtual_memory(self) -> None:
        """
        Checks the machine's virtual memory meet minimum requirements.
        """
        ram = psutil.virtual_memory().total

        machine_type = self.prompt.prompt(
            "Is this machine an instrument (e.g. NDXALF) or a test machine (e.g. NDXSELAB)?"
            " (instrument/test) ",
            possibles=["instrument", "test"],
            default="test",
        )

        if machine_type == "instrument":
            min_memory = RAM_NORMAL_INSTRUMENT
        else:
            min_memory = RAM_MIN

        if ram >= min_memory:
            print(
                "Virtual memory ({:.1f}GB) is already at or above the recommended level"
                " for this machine type "
                "({:.1f}GB). Nothing to do in this step.".format(
                    ram / GIGABYTE, min_memory / GIGABYTE
                )
            )
        else:
            self.prompt.prompt_and_raise_if_not_yes(
                "Current machine memory is {:.1f}GB, the recommended amount for"
                " this machine is {:.1f}GB.\n\n"
                "If appropriate, upgrade this machine's memory allowance by following"
                " the instructions in "
                "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Increase-VM-memory.\n\n"
                "Note, this will require a machine restart.".format(
                    ram / GIGABYTE, min_memory / GIGABYTE
                )
            )

    @task("Check there is {:.1e}B free disk space".format(FREE_DISK_MIN))
    def _check_disk_usage(self) -> None:
        """
        Checks the machine's free disk space meets minimum requirements.
        """
        disk_space = psutil.disk_usage("/")

        if disk_space.free < FREE_DISK_MIN:
            self.prompt.prompt_and_raise_if_not_yes(
                "The machine requires at least {:.1f}GB of free disk space to run IBEX.".format(
                    FREE_DISK_MIN / GIGABYTE
                )
            )

    @task("Put IBEX autostart script into startup for current user")
    def put_autostart_script_in_startup_area(self) -> None:
        """
        Checks the startup location for all users for the autostart script and removes
         any instances.

        Checks the startup location of the current user and removes the autostart script
         if it was copied.

        Creates a shortcut of the ibex server autostart script into the current user startup folder
        so that the IBEX server starts automatically on startup.
        """

        autostart_script_name = "ibex_system_boot"

        # Check all users startup folder.
        paths = glob.glob(os.path.join(ALLUSERS_STARTUP, f"{autostart_script_name}*"))
        if len(paths):
            admin_commands = AdminCommandBuilder()
            for path in paths:
                print(f"Removing: '{path}'.")
                admin_commands.add_command("del", f'"{path}"')
            admin_commands.run_all()

        # Check current user startup folder for copied batch file.
        autostart_batch_path = os.path.join(USER_STARTUP, f"{autostart_script_name}.bat")
        if os.path.exists(autostart_batch_path):
            print(f"Removing: '{autostart_batch_path}'.")
            os.remove(autostart_batch_path)

        # Create shortcut to autostart batch file.
        autostart_shortcut_path = os.path.join(USER_STARTUP, f"{autostart_script_name}.lnk")
        if not os.path.exists(autostart_shortcut_path):
            print(f"Adding shortcut: '{autostart_shortcut_path}'.")
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(autostart_shortcut_path)
            shortcut.Targetpath = os.path.join(EPICS_PATH, f"{autostart_script_name}.bat")
            shortcut.save()
        else:
            print("Shortcut already exists.")

    @task("Restrict Internet Explorer")
    def restrict_ie(self) -> None:
        """
        Restrict access of external websites to address a security vulnerability
         in Internet Explorer.
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Configure Internet Explorer to restrict access to the web except for"
            " select whitelisted sites:\n"
            "- Open 'Internet Options' (from the gear symbol in the top right corner of the window)"
            ".\n"
            "- Go to the 'Connections' tab and open 'Lan Settings'\n"
            "- Check 'Use Automatic configuration script' and enter"
            " http://dataweb.isis.rl.ac.uk/proxy.pac for 'Address'\n"
            "- Click 'Ok' on all dialogs."
        )

    @version_check(Git())
    @task("Update Git")
    def install_or_upgrade_git(self) -> None:
        """
        Install the latest git version
        """
        git_path = shutil.which("git")
        if os.path.exists(git_path):
            if "program files" in os.path.realpath(git_path).lower():
                print(
                    f"git installed as admin detected in '{git_path}', attempting to"
                    f" upgrade as admin."
                )
                admin_commands = AdminCommandBuilder()
                admin_commands.add_command(
                    f'"{git_path}"', "update-git-for-windows --yes", expected_return_val=None
                )
                log_file = admin_commands.run_all()

                with open(log_file, "r") as logfile:
                    for line in logfile.readlines():
                        print("git update output: {}".format(line.rstrip()))
            else:
                print(
                    f"git installed as normal user detected in '{git_path}', attempting upgrade "
                    f"as normal user."
                )
                RunProcess(
                    working_dir=os.curdir,
                    executable_file=git_path,
                    executable_directory="",
                    prog_args=["update-git-for-windows", "--yes"],
                    expected_return_codes=None,
                ).run()
            self.prompt.prompt_and_raise_if_not_yes(
                "Press Y/N if Git has installed correctly", default="Y"
            )
        else:
            self.prompt.prompt_and_raise_if_not_yes(
                "Download and Install Git from https://git-scm.com/downloads"
            )

    @task("Update visual studio redistributable files")
    def install_or_upgrade_vc_redist(self) -> None:
        """
        Install the latest visual studio redistributable files
        """
        import ibex_install_utils.current_args

        arch = ibex_install_utils.current_args.SERVER_ARCH

        print(f"Installing vc_redist for arch: {arch}")

        files_to_run = ["vc_redist.x64.exe"]
        if arch == "x86":
            files_to_run.insert(0, "vc_redist.x86.exe")
        for file in files_to_run:
            exe_file = Path(EPICS_CRTL_PATH, file)
            if exe_file.exists() and exe_file.is_file():
                log_file = Path(
                    VAR_DIR, "logs", "deploy", f"vc_redist_log{time.strftime('%Y%m%d%H%M%S')}.txt"
                )

                # AdminRunner doesn't seem to work here, saying it can't find a handle, so just
                # run as a normal command as the process itself prompts for admin.
                RunProcess(
                    working_dir=str(exe_file.parent),
                    executable_file=exe_file.name,
                    prog_args=[
                        "/install",
                        "/norestart",
                        "/passive",
                        "/quiet",
                        "/log",
                        str(log_file),
                    ],
                    expected_return_codes=[0],
                ).run()

                # vc_redist helpfully finishes with errorlevel 0 before actually
                # copying the files over, therefore we'll sleep for 5 seconds here
                print("waiting for install to finish")
                sleep(5)

                last_line = ""
                with open(log_file, "r") as f:
                    for line in f.readlines():
                        print("vc_redist install output: {}".format(line.rstrip()))
                        last_line = line

                status = (
                    "It looked like it installed correctly, but "
                    if "Exit code: 0x0" in last_line
                    else "it looked like the process errored,"
                )

                self.prompt.prompt_and_raise_if_not_yes(
                    f"Installing vc redistributable files finished.\n"
                    f"{status}"
                    f"please check log output above for errors,\nor alternatively {log_file}",
                    default="Y",
                )
            else:
                raise ErrorInTask(
                    f"VC redistributable files not found in {exe_file.parent}, please check"
                    f" and make sure {exe_file} is present. "
                )

    def confirm(self, message: str) -> None:
        """
        Ask user to confirm correct script was chosen.
        """
        self.prompt.prompt_and_raise_if_not_yes(message, default="Y")

    def _read_file(self, path: str | os.PathLike[str], error_text: str) -> str:
        """
        print a file contents to screen
        """
        data = ""
        try:
            with open(path, "r") as fin:
                data = fin.read()
        except OSError:
            data = error_text
        return data

    def user_confirm_upgrade_type_on_machine(self, machine_type: str) -> None:
        """
        Print information about the current upgrade and prompt the user
        Returns:
        Raises UserStop: when the user doesn't want to continue

        """
        print(f"Upgrade {BaseTasks._get_machine_name()} as a {machine_type}")
        server_version = self._read_file(
            os.path.join(self._server_source_dir, "VERSION.txt"), "UNKNOWN"
        )
        print(f"    Server source: {self._server_source_dir}")
        print(f"          version: {server_version}")
        client_version = self._read_file(
            os.path.join(self._client_source_dir, "Client", "VERSION.txt"), "UNKNOWN"
        )
        print(f"    Client source: {self._client_source_dir}")
        print(f"          version: {client_version}")
        python_version = self._read_file(
            os.path.join(self._genie_python_3_source_dir, "VERSION.txt"), "UNKNOWN"
        )
        print(f"    Python 3 source: {self._genie_python_3_source_dir}")
        print(f"            version: {python_version}")
        answer = self.prompt.prompt("Continue? [Y/N]", ["Y", "N"], "Y")
        if answer != "Y":
            raise UserStop()
