import os
import shutil
import tempfile
from time import sleep

from installation_and_upgrade.ibex_install_utils.admin_runner import AdminCommandBuilder
from installation_and_upgrade.ibex_install_utils.run_process import RunProcess
from installation_and_upgrade.ibex_install_utils.task import task
from installation_and_upgrade.ibex_install_utils.tasks import BaseTasks
from installation_and_upgrade.ibex_install_utils.tasks.common_paths import INSTRUMENT_BASE_DIR, INST_SHARE_AREA, EPICS_PATH, APPS_BASE_DIR, \
    SETTINGS_CONFIG_PATH, VAR_DIR


class Vhd:
    def __init__(self, name, source_filename, dest_filename, mount_point):
        self.name = name
        self.source_filename = source_filename
        self.dest_filename = dest_filename
        self.mount_point = mount_point


VHDS = [
    # Key = VHD location, Value = Mount point
    Vhd(name="Apps", source_filename="empty_apps.vhdx", dest_filename="apps.vhdx", mount_point=APPS_BASE_DIR),
    Vhd(name="Settings", source_filename="empty_settings.vhdx", dest_filename="settings.vhdx", mount_point=SETTINGS_CONFIG_PATH),
    Vhd(name="Var", source_filename="empty_var.vhdx", dest_filename="var.vhdx", mount_point=VAR_DIR),
]


FILE_TO_REQUEST_VHD_MOUNTING = os.path.join(INSTRUMENT_BASE_DIR, "ibex_vhd_deployment_mount_vhds.txt")
FILE_TO_REQUEST_VHD_DISMOUNTING = os.path.join(INSTRUMENT_BASE_DIR, "ibex_vhd_deployment_dismount_vhds.txt")
VHD_MOUNT_DISMOUNT_TIMEOUT = 300


REMOTE_VHD_SRC_DIR = os.path.join(INST_SHARE_AREA, "Kits$", "CompGroup", "chris")
REMOTE_VHD_DEST_DIR = os.path.join(INST_SHARE_AREA, "Kits$", "CompGroup", "ICP", "VHDS")
LOCAL_VHD_DIR = os.path.join("C:\\", "Instrument", "VHDS")


class VHDTasks(BaseTasks):
    """
    Tasks relating to creating or using VHDs.
    """

    @task("Copy VHDs to local area")
    def copy_vhds_to_local_area(self):
        if os.path.exists(LOCAL_VHD_DIR):
            try:
                shutil.rmtree(LOCAL_VHD_DIR)
            except (IOError, OSError):
                self.request_dismount_vhds()
                shutil.rmtree(LOCAL_VHD_DIR)

        os.mkdir(LOCAL_VHD_DIR)
        for vhd in VHDS:
            shutil.copyfile(os.path.join(REMOTE_VHD_SRC_DIR, vhd.source_filename),
                            os.path.join(LOCAL_VHD_DIR, vhd.source_filename))

    def _create_file_and_wait_for_it_to_be_deleted(self, filename, timeout):
        with open(filename, "w") as f:
            f.write("")

        print(f"Waiting for file at {filename} to be deleted...")
        for _ in range(timeout):
            if not os.path.exists(filename):
                break
            sleep(1)
        else:
            os.remove(filename)
            raise IOError(f"File at {filename} still existed after {timeout}s, check VHD scheduled task is running "
                          f"correctly ")

    @task("Request VHDs to be mounted")
    def request_mount_vhds(self):
        self._create_file_and_wait_for_it_to_be_deleted(FILE_TO_REQUEST_VHD_MOUNTING, VHD_MOUNT_DISMOUNT_TIMEOUT)

    @task("Request VHDs to be dismounted")
    def request_dismount_vhds(self):
        self._create_file_and_wait_for_it_to_be_deleted(FILE_TO_REQUEST_VHD_DISMOUNTING, VHD_MOUNT_DISMOUNT_TIMEOUT)

    @task("Mount VHDs")
    def mount_vhds(self):
        if not os.path.exists(FILE_TO_REQUEST_VHD_MOUNTING):
            return

        admin_commands = AdminCommandBuilder()

        admin_commands.add_command("sc", "stop MYSQL80", expected_return_val=None)

        for vhd in VHDS:
            driveletter_file = os.path.join(tempfile.gettempdir(), f"{vhd.name}_driveletter.txt")
            if os.path.exists(driveletter_file):
                os.remove(driveletter_file)

            if os.path.exists(vhd.mount_point):
                admin_commands.add_command("move",
                                           f'"{vhd.mount_point}" "{vhd.mount_point}_backup"',
                                           expected_return_val=None)

            # Mount the VHD and write it's assigned drive letter to a file.
            admin_commands.add_command(
                "powershell",
                r'-command "Hyper-V\Mount-VHD -path {vhd_file} -Passthru | Get-Disk | Get-Partition | Get-Volume | foreach {{ $_.DriveLetter }} | out-file -filepath {driveletter_file} -Encoding ASCII -NoNewline"'
                    .format(vhd_file=os.path.join(LOCAL_VHD_DIR, vhd.source_filename), name=vhd.name,
                            driveletter_file=driveletter_file))

            # Append :\\ to drive letter, e.g. E -> E:\\ (this is necessary so that directory junctions work correctly)
            admin_commands.add_command(
                "powershell",
                r'-command "echo :\\ | out-file -filepath {driveletter_file} -Encoding ASCII -Append -NoNewline"'
                    .format(driveletter_file=driveletter_file)
            )

            # Create a directory junction from the mount point to the disk's assigned drive letter
            admin_commands.add_command(
                "powershell",
                r'-command "&cmd /c mklink /J /D {mount_point} @(cat {driveletter_file})"'
                    .format(mount_point=vhd.mount_point, name=vhd.name, driveletter_file=driveletter_file))

        admin_commands.run_all()

        os.remove(FILE_TO_REQUEST_VHD_MOUNTING)

    @task("Dismount VHDs")
    def dismount_vhds(self):

        if not os.path.exists(FILE_TO_REQUEST_VHD_DISMOUNTING):
            return

        admin_commands = AdminCommandBuilder()

        for vhd in VHDS:
            # Dismount the VHD
            admin_commands.add_command(
                "powershell",
                r'-command "Hyper-V\Dismount-VHD {vhd_file}"'.format(
                    vhd_file=os.path.join(LOCAL_VHD_DIR, vhd.source_filename)),
                expected_return_val=None,
            )

            # Remove directory junction
            admin_commands.add_command(
                "cmd",
                r'/c f"rmdir {mount_point}"'.format(mount_point=vhd.mount_point),
                expected_return_val=None,
            )

            # Restore previous directories to where they were before mounting VHDS
            if os.path.exists(f"{vhd.mount_point}_backup"):
                admin_commands.add_command("move",
                                           f'"{vhd.mount_point}_backup" "{vhd.mount_point}"',
                                           expected_return_val=None)

        admin_commands.add_command("sc", "start MYSQL80", expected_return_val=None)
        admin_commands.run_all()

        os.remove(FILE_TO_REQUEST_VHD_DISMOUNTING)

    @task("Deploy VHDS")
    def deploy_vhds(self):

        build_folder = os.path.join(REMOTE_VHD_DEST_DIR, "Build{}".format(os.environ["BUILD_NUMBER"]))
        os.makedirs(build_folder)

        for vhd in VHDS:
            print(f"Deploying {vhd.source_filename} to '{build_folder}'")
            shutil.copyfile(os.path.join(LOCAL_VHD_DIR, vhd.source_filename),
                            os.path.join(build_folder, vhd.dest_filename))

        print("Cleaning up local artefacts...")
        shutil.rmtree(LOCAL_VHD_DIR)

    @task("Initialize var dir")
    def initialize_var_dir(self):
        """
        Creates the folder structure for the C:\instrument\var directory.
        """
        # config_env creates all the necessary directories for us
        RunProcess(working_dir=EPICS_PATH, executable_file="config_env.bat").run()