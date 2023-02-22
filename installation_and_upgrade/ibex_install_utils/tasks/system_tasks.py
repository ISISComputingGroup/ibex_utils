import filecmp
import sys, os
import shutil

import psutil

from ibex_install_utils.admin_runner import AdminCommandBuilder
from ibex_install_utils.exceptions import UserStop
from ibex_install_utils.kafka_utils import add_required_topics
from ibex_install_utils.run_process import RunProcess
from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import APPS_BASE_DIR, EPICS_PATH

GIGABYTE = 1024 ** 3

RAM_MIN = 7.5 * GIGABYTE  # 8 GB minus a small tolerance.
RAM_NORMAL_INSTRUMENT = 13 * GIGABYTE  # Should be 14GB ideally, but allow anything over 13GB.
FREE_DISK_MIN = 30 * GIGABYTE

SPUDULIKE = "spudulike"
USER_HOME = os.path.join("C:\\users\\", SPUDULIKE)
USER_START_MENU = os.path.join(USER_HOME, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu")
ALLUSERS_START_MENU = os.path.join("C:\\", "ProgramData", "Microsoft", "Windows", "Start Menu")
SECI = "SECI User interface.lnk"
SECI_ONE_PATH = os.path.join("C:\\", "Program Files (x86)", "CCLRC ISIS Facility")
AUTOSTART_LOCATIONS = [os.path.join(USER_START_MENU, "Programs", "Startup", SECI),
                       os.path.join(ALLUSERS_START_MENU, "Programs", "Startup", SECI)]

DESKTOP_TRAINING_FOLDER_PATH = os.path.join(os.environ["userprofile"], "desktop", "Mantid+IBEX training")


class SystemTasks(BaseTasks):
    """
    Tasks relating to the system e.g. installed software other than core IBEX components, windows, firewalls, etc.
    """
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
                   executable_directory=os.path.join("C:\\", "Program Files (x86)", "Notepad++", "updater")).run()

    @task("Removing training folder on desktop ...")
    def clean_up_desktop_ibex_training_folder(self):
        """
        Remove training folder from the desktop
        Returns:

        """
        self._file_utils.remove_tree(DESKTOP_TRAINING_FOLDER_PATH, self.prompt)


    @task("Remove SECI shortcuts")
    def remove_seci_shortcuts(self):
        """
        Remove (or at least ask the user to remove) all Seci shortcuts
        """
        for path in AUTOSTART_LOCATIONS:
            if os.path.exists(path):
                self.prompt.prompt_and_raise_if_not_yes(
                    f"SECI autostart found in {path}, delete this.")

        self.prompt.prompt_and_raise_if_not_yes("Remove task bar shortcut to SECI")
        self.prompt.prompt_and_raise_if_not_yes("Remove desktop shortcut to SECI")
        self.prompt.prompt_and_raise_if_not_yes("Remove start menu shortcut to SECI")

    @task("Remove Treesize shortcuts")
    def remove_treesize_shortcuts(self):
        """
        Remove (or at least ask the user to remove) all Treesize shortcuts.

        For justification see https://github.com/ISISComputingGroup/IBEX/issues/4214
        """
        self.prompt.prompt_and_raise_if_not_yes("Remove task bar shortcut to Treesize if it exists")
        self.prompt.prompt_and_raise_if_not_yes("Remove desktop shortcut to Treesize if it exists")
        self.prompt.prompt_and_raise_if_not_yes("Remove start menu shortcut to Treesize if it exists")

    @task("Remove SECI 1 Path")
    def remove_seci_one(self):
        """
        Removes SECI 1
        """
        if os.path.exists(SECI_ONE_PATH):
            try:
                self._file_utils.remove_tree(SECI_ONE_PATH, self.prompt, use_robocopy=False)
            except (IOError, WindowsError) as e:
                self.prompt.prompt_and_raise_if_not_yes(f"Failed to remove SECI 1 (located in '{SECI_ONE_PATH}') "
                                                        f"because '{e}'. Please remove it manually and type 'Y'"
                                                        f" to confirm")

    @task("Install java")
    def check_java_installation(self):
        """
        Checks Java installation
        """

        self.prompt.prompt_and_raise_if_not_yes(
            "Upgrade openJDK installation by following:\r\n"
            "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Upgrade-Java\r\n\r\n"
            "After following the installer, ensure you close and then re-open your remote desktop session (This "
            "is a workaround for windows not immediately picking up new environment variables)")

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

    @task("Update release notes")
    def update_release_notes(self):
        """
        Update the release notes.
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Have you updated the instrument release notes at https://github.com/ISISComputingGroup/IBEX/wiki?")

    @task("Update Instrument List")
    def update_instlist(self):
        """
        Prompt user to add instrument to the list of known IBEX instruments
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Add the host name of the instrument to the list saved in the CS:INSTLIST PV")

    @task("Update kafka topics")
    def update_kafka_topics(self):
        """
        Adds the required kafka topics to the cluster.
        """
        add_required_topics("livedata.isis.cclrc.ac.uk:9092", self._get_instrument_name())

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
        ibex_version = self._ibex_version if self._ibex_version is not None else "<Insert version number here>"
        email_template = f"""Please send the following email to your instrument scientists:
                    Hello,
                    We have finished the upgrade of {BaseTasks._get_machine_name()} to IBEX {ibex_version}.
                    The release notes for this are at the following link: https://github.com/ISISComputingGroup/IBEX/wiki/Release-Notes-v{ibex_version}

                    Please let us know if you have any queries or find any problems with the upgrade.
                    Thank you,
                    <your name>"""

        self.prompt.prompt_and_raise_if_not_yes(email_template)

    @task("Apply changes in release notes")
    def apply_changes_noted_in_release_notes(self):
        """
        Apply any changes noted in the release notes.
        """
        # For future reference, genie_python can send emails!
        self.prompt.prompt_and_raise_if_not_yes(
            "Look in the IBEX wiki at the release notes for the version you are deploying. Apply needed fixes.")

    def check_resources(self):
        """
        Check the machine's resources meet minimum requirements.
        """
        self.check_virtual_memory()
        self._check_disk_usage()

    @task("Check virtual machine memory")
    def check_virtual_memory(self):
        """
        Checks the machine's virtual memory meet minimum requirements.
        """
        ram = psutil.virtual_memory().total

        machine_type = self.prompt.prompt(
            "Is this machine an instrument (e.g. NDXALF) or a test machine (e.g. NDXSELAB)? (instrument/test) ",
            possibles=["instrument", "test"], default="test")

        if machine_type == "instrument":
            min_memory = RAM_NORMAL_INSTRUMENT
        else:
            min_memory = RAM_MIN

        if ram >= min_memory:
            print("Virtual memory ({:.1f}GB) is already at or above the recommended level for this machine type "
                  "({:.1f}GB). Nothing to do in this step.".format(ram / GIGABYTE, min_memory / GIGABYTE))
        else:
            self.prompt.prompt_and_raise_if_not_yes(
                "Current machine memory is {:.1f}GB, the recommended amount for this machine is {:.1f}GB.\n\n"
                "If appropriate, upgrade this machine's memory allowance by following the instructions in "
                "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Increase-VM-memory.\n\n"
                "Note, this will require a machine restart.".format(ram / GIGABYTE, min_memory / GIGABYTE)
            )

    @task("Check there is {:.1e}B free disk space".format(FREE_DISK_MIN))
    def _check_disk_usage(self):
        """
        Checks the machine's free disk space meets minimum requirements.
        """
        disk_space = psutil.disk_usage("/")

        if disk_space.free < FREE_DISK_MIN:
            self.prompt.prompt_and_raise_if_not_yes(
                "The machine requires at least {:.1f}GB of free disk space to run IBEX."
                    .format(FREE_DISK_MIN / GIGABYTE))

    @task("Put IBEX autostart into pc start menu")
    def put_autostart_script_in_startup_area(self):
        """
        Copies the ibex server autostart script into the PC startup folder so that the IBEX server starts
        automatically on startup.
        """

        autostart_script_name = "ibex_system_boot.bat"

        from_path = os.path.join(EPICS_PATH, autostart_script_name)
        allusers_path = os.path.join(ALLUSERS_START_MENU, "Programs", "Startup", autostart_script_name)
        user_folder = os.path.join(USER_START_MENU, "Programs", "Startup")
        user_path = os.path.join(user_folder, autostart_script_name)
        user_folder += "\\"

        if os.path.exists(allusers_path):
            # We need to run these as admin as the destination dir is not writable by standard users.
            admin_commands = AdminCommandBuilder()
            admin_commands.add_command("del", f'"{allusers_path}"')
            admin_commands.run_all()
            
        if os.path.exists(USER_HOME) and not os.path.exists(user_folder):
            # The user was created but we (Administrators) don't have access to the folder.
            admin_commands = AdminCommandBuilder()
            admin_commands.add_command("icacls", USER_HOME + " /inheritance:e /grant:r Administrators:R")
            admin_commands.run_all()

        if not os.path.exists(user_folder):
            # The user has not been created yet.
            admin_commands = AdminCommandBuilder()
            my_path = os.path.abspath(os.path.dirname(sys.argv[0]))
            admin_commands.add_command("start /wait", my_path + "\\create_spudulike.bat " + from_path)
            admin_commands.run_all()
            print("spudulike user start-up added")
            return

        if os.path.exists(user_path) and filecmp.cmp(from_path, user_path):
            print("Autostart script already installed correctly - nothing to do")
            return
            
        try:
            # We can copy this without admin if we are the spudulike user.
            shutil.copyfile(from_path, user_path)
        except PermissionError:
            # If we aren't, we need admin access to do it.
            admin_commands = AdminCommandBuilder()
            admin_commands.add_command("xcopy", "/I " + f'"{from_path}"' + " " + f'"{user_folder}"')
            admin_commands.run_all()
       

    @task("Restrict Internet Explorer")
    def restrict_ie(self):
        """
        Restrict access of external websites to address a security vulnerability in Internet Explorer.
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Configure Internet Explorer to restrict access to the web except for select whitelisted sites:\n"
            "- Open 'Internet Options' (from the gear symbol in the top right corner of the window).\n"
            "- Go to the 'Connections' tab and open 'Lan Settings'\n"
            "- Check 'Use Automatic configuration script' and enter http://dataweb.isis.rl.ac.uk/proxy.pac for 'Address'\n"
            "- Click 'Ok' on all dialogs.")

    @task("Update Git")
    def install_or_upgrade_git(self):
        """
        Install the latest git version
        """
        git_path = shutil.which("git")
        if os.path.exists(git_path):
            if "program files" in git_path.lower():
                print(f"git installed as admin detected in '{git_path}', attempting to upgrade as admin.")
                admin_commands = AdminCommandBuilder()
                admin_commands.add_command(f'"{git_path}"', "update-git-for-windows --yes", expected_return_val=None)
                log_file = admin_commands.run_all()

                with open(log_file, "r") as logfile:
                    for line in logfile.readlines():
                        print("git update output: {}".format(line.rstrip()))
            else:
                print(f"git installed as normal user detected in '{git_path}', attempting upgrade as normal user.")
                RunProcess(working_dir=os.curdir,
                           executable_file=git_path,
                           executable_directory="",
                           prog_args=["update-git-for-windows", "--yes"],
                           expected_return_code=None).run()
            self.prompt.prompt_and_raise_if_not_yes("Press Y/N if Git has installed correctly", default="Y")
        else:
            self.prompt.prompt_and_raise_if_not_yes("Download and Install Git from https://git-scm.com/downloads")
    

    def confirm(self, message):
        """
        Ask user to confirm correct script was chosen.
        """
        self.prompt.prompt_and_raise_if_not_yes(message, default="Y")

    def user_confirm_upgrade_type_on_machine(self, machine_type):
        """
        Print information about the current upgrade and prompt the user
        Returns:
        Raises UserStop: when the user doesn't want to continue

        """
        print(f"Upgrade {BaseTasks._get_machine_name()} as a {machine_type}")
        print(f"    Server source: {self._server_source_dir}")
        print(f"    Client source: {self._client_source_dir}")
        print(f"    Python 3 source: {self._genie_python_3_source_dir}")
        answer = self.prompt.prompt("Continue? [Y/N]", ["Y", "N"], "Y")
        if answer != "Y":
            raise UserStop()
    