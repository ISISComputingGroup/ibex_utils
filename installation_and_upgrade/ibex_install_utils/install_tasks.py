"""Tasks associated with install"""

import os

from ibex_install_utils.file_utils import LABVIEW_DAE_DIR, FileUtils
from ibex_install_utils.tasks.backup_tasks import BackupTasks
from ibex_install_utils.tasks.client_tasks import ClientTasks
from ibex_install_utils.tasks.git_tasks import GitTasks
from ibex_install_utils.tasks.mysql_tasks import MysqlTasks
from ibex_install_utils.tasks.python_tasks import PythonTasks
from ibex_install_utils.tasks.server_tasks import ServerTasks
from ibex_install_utils.tasks.system_tasks import SystemTasks
from ibex_install_utils.tasks.vhd_tasks import VHDTasks
from ibex_install_utils.user_prompt import UserPrompt


class UpgradeInstrument:
    """Class to upgrade the instrument installation to the given version of IBEX."""

    def __init__(
        self,
        user_prompt: UserPrompt,
        server_source_dir: str,
        client_source_dir: str,
        genie_python3_dir: str,
        ibex_version: str,
        file_utils: FileUtils = FileUtils(),
    ) -> None:
        """Initializer.

        Args:
            user_prompt: a object to allow prompting of the user
            server_source_dir: directory to install ibex server from
            client_source_dir: directory to install ibex client from
            genie_python3_dir: directory to install genie_python 3 from
            ibex_version: version number of ibex that we are upgrading to
            file_utils : collection of file utilities
        """
        self._client_tasks = ClientTasks(
            user_prompt,
            server_source_dir,
            client_source_dir,
            genie_python3_dir,
            ibex_version,
            file_utils,
        )

        self._mysql_tasks = MysqlTasks(
            user_prompt,
            server_source_dir,
            client_source_dir,
            genie_python3_dir,
            ibex_version,
            file_utils,
        )

        self._python_tasks = PythonTasks(
            user_prompt,
            server_source_dir,
            client_source_dir,
            genie_python3_dir,
            ibex_version,
            file_utils,
        )

        self._server_tasks = ServerTasks(
            user_prompt,
            server_source_dir,
            client_source_dir,
            genie_python3_dir,
            ibex_version,
            file_utils,
        )

        self._system_tasks = SystemTasks(
            user_prompt,
            server_source_dir,
            client_source_dir,
            genie_python3_dir,
            ibex_version,
            file_utils,
        )

        self._vhd_tasks = VHDTasks(
            user_prompt,
            server_source_dir,
            client_source_dir,
            genie_python3_dir,
            ibex_version,
            file_utils,
        )

        self._backup_tasks = BackupTasks(
            user_prompt,
            server_source_dir,
            client_source_dir,
            genie_python3_dir,
            ibex_version,
            file_utils,
        )

        self._git_tasks = GitTasks(
            user_prompt,
            server_source_dir,
            client_source_dir,
            genie_python3_dir,
            ibex_version,
            file_utils,
        )

    @staticmethod
    def icp_in_labview_modules() -> bool:
        """Condition on which to install ICP_Binaries or

        :return: True if the ICP is installed in labview modules, False otherwise
        """
        return os.path.exists(LABVIEW_DAE_DIR)

    def run_test_update(self) -> None:
        """Run a complete test upgrade on the current system"""
        self._system_tasks.user_confirm_upgrade_type_on_machine("Training Machine")
        self._system_tasks.install_or_upgrade_git()
        self._backup_tasks.remove_old_ibex()
        self._system_tasks.clean_up_desktop_ibex_training_folder()
        self._server_tasks.remove_settings()
        self._server_tasks.install_settings()
        self._server_tasks.install_ibex_server()
        self._server_tasks.update_icp(self.icp_in_labview_modules())
        self._python_tasks.install_genie_python3()
        self._mysql_tasks.install_mysql()
        self._server_tasks.upgrade_instrument_configuration()
        self._server_tasks.install_wiring_tables()
        self._client_tasks.install_ibex_client()
        self._system_tasks.upgrade_notepad_pp()
        self._server_tasks.setup_log_rotation()
        self._server_tasks.update_journal_parser()

    def remove_all_and_install_client_and_server(self) -> None:
        """Either install or upgrade the ibex client and server"""
        self._system_tasks.confirm(
            "This script removes IBEX client and server and installs "
            "the latest build of both, and upgrade the "
            "config/schema without any extra steps. Proceed?"
        )

        self._system_tasks.user_confirm_upgrade_type_on_machine("Client/Server Machine")
        use_old_galil: bool = self._server_tasks.select_galil_driver()
        self._backup_tasks.remove_old_ibex()
        self._server_tasks.install_ibex_server(use_old_galil)
        self._server_tasks.update_icp(self.icp_in_labview_modules(), register_icp=False)
        self._python_tasks.install_genie_python3()
        self._client_tasks.install_ibex_client()
        self._server_tasks.upgrade_instrument_configuration()
        self._server_tasks.install_shared_scripts_repository()

    def run_instrument_tests(self) -> None:
        """Run through client and server tests once installation / deployment has completed."""
        self._client_tasks.perform_client_tests()
        self._server_tasks.perform_server_tests()
        self._system_tasks.inform_instrument_scientists()

    def run_instrument_install(self) -> None:
        """Do a first installation of IBEX on a new instrument."""
        self._system_tasks.confirm(
            "This script performs a first-time full installation of the IBEX server and client"
            " on a new instrument. Proceed?"
        )

        self._system_tasks.check_resources()
        self._system_tasks.install_or_upgrade_git()
        self._system_tasks.check_java_installation()

        self._system_tasks.restrict_ie()

        self._server_tasks.install_ibex_server()
        self._system_tasks.create_virtual_envs()
        self._server_tasks.update_icp(self.icp_in_labview_modules())
        self._python_tasks.install_genie_python3()
        self._mysql_tasks.install_mysql()
        self._client_tasks.install_ibex_client()
        self._git_tasks.checkout_to_release_branch()
        self._server_tasks.setup_config_repository()
        self._server_tasks.upgrade_instrument_configuration()
        self._system_tasks.configure_com_ports()
        self._server_tasks.setup_calibrations_repository()
        self._server_tasks.update_calibrations_repository()
        self._system_tasks.clear_or_reapply_hotfixes()
        self._server_tasks.install_wiring_tables()
        self._server_tasks.configure_motion()
        self._system_tasks.add_nagios_checks()
        self._system_tasks.update_instlist()
        self._system_tasks.update_kafka_topics()
        self._system_tasks.put_autostart_script_in_startup_area()
        self._python_tasks.update_script_definitions()
        self._server_tasks.setup_log_rotation()
        self._server_tasks.update_journal_parser()

    def run_update_icp(self) -> None:
        self._server_tasks.update_icp(self.icp_in_labview_modules())

    def save_motor_params(self) -> None:
        self._server_tasks.save_motor_parameters_to_file()

    def run_instrument_deploy(self) -> None:
        """Deploy a full IBEX upgrade on an existing instrument."""
        self._system_tasks.confirm(
            "This script performs a full upgrade of the IBEX server "
            "and client on an existing instrument. Proceed?"
        )
        self.run_instrument_deploy_pre_stop()
        self.run_instrument_deploy_main()
        self.run_instrument_deploy_post_start()

    def run_instrument_deploy_post_start(self) -> None:
        """Upgrade an instrument. Steps to do after ibex has been started.

        Current the server can not be started in this python script.
        """
        self._client_tasks.start_ibex_gui()
        self._client_tasks.perform_client_tests()
        self._server_tasks.perform_server_tests()
        self._server_tasks.run_config_checker()
        self._server_tasks.save_motor_blocks_blockserver_to_file()
        self._system_tasks.put_autostart_script_in_startup_area()
        self._system_tasks.inform_instrument_scientists()

    def run_instrument_deploy_main(self) -> None:
        """Upgrade an instrument. Steps to do after ibex has been stopped
        but before it is restarted.

        Current the server can not be started or stopped in this python script.
        """
        self._system_tasks.install_or_upgrade_git()
        self._system_tasks.check_java_installation()
        self._git_tasks.show_git_status()
        self._backup_tasks.backup_old_directories()
        self._backup_tasks.backup_checker()
        self._mysql_tasks.backup_database()
        self._mysql_tasks.truncate_database()
        self._server_tasks.install_ibex_server()
        self._system_tasks.create_virtual_envs()
        self._server_tasks.update_icp(self.icp_in_labview_modules())
        self._python_tasks.install_genie_python3()
        self._mysql_tasks.install_mysql()
        self._system_tasks.install_or_upgrade_vc_redist()

        self._client_tasks.install_ibex_client()
        self._git_tasks.checkout_to_release_branch()
        self._server_tasks.upgrade_instrument_configuration()
        self._server_tasks.update_calibrations_repository()
        self._system_tasks.clear_or_reapply_hotfixes()
        self._python_tasks.update_script_definitions()
        self._python_tasks.remove_instrument_script_githooks()
        self._server_tasks.setup_log_rotation()
        self._server_tasks.update_journal_parser()
        self._system_tasks.update_kafka_topics()

    def run_instrument_deploy_pre_stop(self) -> None:
        """Upgrade an instrument. Steps to do before ibex is stopped.

        Current the server can not be started or stopped in this python script.
        """
        self._system_tasks.user_confirm_upgrade_type_on_machine("Client/Server Machine")
        self._server_tasks.save_motor_blocks_blockserver_to_file()

    def run_truncate_database(self) -> None:
        """Backup and truncate databases only"""
        self._mysql_tasks.backup_database()
        self._mysql_tasks.truncate_database()

    def run_force_upgrade_mysql(self) -> None:
        """:key
        Do upgrade of mysql, with data dump.
        """
        self._mysql_tasks.install_mysql(force=True)

    def run_upgrade_mysql(self) -> None:
        """:key
        Do upgrade of mysql with no table recreate.
        """
        self._mysql_tasks.install_mysql(force=False)

    def run_update_calibrations_repository(self) -> None:
        """update_calibrations_repository"""
        self._server_tasks.update_calibrations_repository()

    def run_setup_log_rotation(self) -> None:
        """setup_log_rotation"""
        self._server_tasks.setup_log_rotation()

    def run_update_journal_parser(self) -> None:
        """update_journal_parser"""
        self._server_tasks.update_journal_parser()

    def run_developer_update(self) -> None:
        """Update all the developer tools to latest version"""
        self._mysql_tasks.install_mysql(force=False)
        self._system_tasks.check_java_installation()
        self._system_tasks.install_or_upgrade_git()
        self._system_tasks.update_kafka_topics()
        self._system_tasks.create_virtual_envs()
        self._system_tasks.update_rust()

    def run_vhd_creation(self) -> None:
        """Automated job which creates a set of VHDs containing all IBEX components.

        Note: this will run under jenkins, don't add interactive tasks to this list.
        """
        # To try to start from a clean state if we already have partially mounted VHDs
        self._vhd_tasks.request_dismount_vhds()

        self._vhd_tasks.copy_vhds_to_local_area()
        self._vhd_tasks.request_mount_vhds()
        try:
            self._server_tasks.install_ibex_server()
            self._python_tasks.install_genie_python3()
            self._mysql_tasks.install_mysql_for_vhd()
            self._client_tasks.install_ibex_client()
            self._server_tasks.setup_config_repository()

            # Some config upgrade steps require MySQL to be running
            # For the VHD build, we can always assume we have a MYSQL_PASSWORD env variable
            mysql_password = os.getenv("MYSQL_PASSWORD")
            if mysql_password is None:
                raise Exception("MYSQL_PASSWORD environment variable not set")
            with self._mysql_tasks.temporarily_run_mysql(mysql_password):
                self._server_tasks.upgrade_instrument_configuration()

            self._server_tasks.setup_calibrations_repository()
            self._server_tasks.update_calibrations_repository()
            self._vhd_tasks.initialize_var_dir()
        finally:
            self._vhd_tasks.request_dismount_vhds()

        self._vhd_tasks.deploy_vhds()

    def mount_vhds(self) -> None:
        """Task which actually mounts the VHDs (will be run as admin)"""
        self._vhd_tasks.mount_vhds()

    def dismount_vhds(self) -> None:
        """Task which actually dismounts the VHDs (will be run as admin)"""
        self._vhd_tasks.dismount_vhds()

    def request_dismount_vhds(self) -> None:
        """Standalone task to request VHDs to be dismounted"""
        self._vhd_tasks.request_dismount_vhds()

    def run_vhd_post_install(self) -> None:
        """This job is run by the MDT build system when it has built
        a windows image and mounted the VHDS
        It will tidy up and remaining jobs that were not possible when
        the vdh was created e.g. register mysql service
        """
        # self._server_tasks.update_icp(self.icp_in_labview_modules())
        self._mysql_tasks.configure_mysql_for_vhd_post_install()


# All possible upgrade tasks
UPGRADE_TYPES = {
    "training_update": (UpgradeInstrument.run_test_update, "update a training machine"),
    "instrument_install": (
        UpgradeInstrument.run_instrument_install,
        "full IBEX installation on a new instrument",
    ),
    "instrument_test": (
        UpgradeInstrument.run_instrument_tests,
        "run through tests for IBEX client and server.",
    ),
    "instrument_deploy_pre_stop": (
        UpgradeInstrument.run_instrument_deploy_pre_stop,
        "instrument_deploy part before the stop of instrument",
    ),
    "instrument_deploy_main": (
        UpgradeInstrument.run_instrument_deploy_main,
        "instrument_deploy after stop but before starting it,",
    ),
    "instrument_deploy_post_start": (
        UpgradeInstrument.run_instrument_deploy_post_start,
        "instrument_deploy part after the start of instrument",
    ),
    "install_latest_incr": (
        UpgradeInstrument.remove_all_and_install_client_and_server,
        "install just the latest incremental build of the server, client and genie_python",
    ),
    "install_latest": (
        UpgradeInstrument.remove_all_and_install_client_and_server,
        "install just the latest clean build of the server, client and genie_python",
    ),
    "truncate_database": (
        UpgradeInstrument.run_truncate_database,
        "backup and truncate the sql database on the instrument",
    ),
    "update_icp": (
        UpgradeInstrument.run_update_icp,
        "update isisicp on the instrument",
    ),
    "force_upgrade_mysql": (
        UpgradeInstrument.run_force_upgrade_mysql,
        "upgrade mysql version to latest and recreate tables",
    ),
    "upgrade_mysql": (
        UpgradeInstrument.run_upgrade_mysql,
        "upgrade mysql version to latest but do not recreate tables",
    ),
    "update_calibrations_repository": (
        UpgradeInstrument.run_update_calibrations_repository,
        "update calibrations repository",
    ),
    "setup_log_rotation": (
        UpgradeInstrument.run_setup_log_rotation,
        "setup log rotation",
    ),
    "update_journal_parser": (
        UpgradeInstrument.run_update_journal_parser,
        "update journal parser",
    ),
    "developer_update": (UpgradeInstrument.run_developer_update, "install latest developer tools"),
    "create_vhds": (
        UpgradeInstrument.run_vhd_creation,
        "create a set of VHDS containing the latest IBEX release",
    ),
    "mount_vhds": (UpgradeInstrument.mount_vhds, "task to mount VHDs if needed"),
    "dismount_vhds": (UpgradeInstrument.dismount_vhds, "task to dismount VHDs if needed"),
    "request_dismount_vhds": (
        UpgradeInstrument.request_dismount_vhds,
        "task to request a dismount of VHDs if needed",
    ),
    "run_vhd_post_install": (
        UpgradeInstrument.run_vhd_post_install,
        "Run final task on system after VHD has been mounted locally",
    ),
    "save_motor_params": (UpgradeInstrument.save_motor_params, "Save motor parameters to csv file"),
}
