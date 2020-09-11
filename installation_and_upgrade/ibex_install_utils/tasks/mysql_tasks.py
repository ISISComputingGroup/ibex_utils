import os
import shutil
import subprocess
import zipfile
from time import sleep

from installation_and_upgrade.ibex_install_utils.admin_runner import AdminCommandBuilder
from installation_and_upgrade.ibex_install_utils.exceptions import ErrorInRun
from installation_and_upgrade.ibex_install_utils.run_process import RunProcess
from installation_and_upgrade.ibex_install_utils.task import task
from installation_and_upgrade.ibex_install_utils.tasks import BaseTasks
from installation_and_upgrade.ibex_install_utils.tasks.common_paths import APPS_BASE_DIR, INST_SHARE_AREA, VAR_DIR, STAGE_DELETED, EPICS_PATH
from installation_and_upgrade.ibex_install_utils.user_prompt import UserPrompt

try:
    from subprocess import DETACHED_PROCESS
except ImportError:
    # For Py2 compatibility, can be removed once we are on Py3.
    DETACHED_PROCESS = 0x00000008

try:
    from contextlib import closing
except ImportError:
    from contextlib2 import closing


MYSQL8_INSTALL_DIR = os.path.join(APPS_BASE_DIR, "MySQL")
MYSQL57_INSTALL_DIR = os.path.join("C:\\", "Program Files", "MySQL", "MySQL Server 5.7")
MYSQL_LATEST_VERSION = "8.0.19"
MYSQL_ZIP = os.path.join(INST_SHARE_AREA, "kits$", "CompGroup", "ICP", "MySQL",
                         f"mysql-{MYSQL_LATEST_VERSION}-winx64.zip")

MYSQL_FILES_DIR = os.path.join(VAR_DIR, "mysql")

SQLDUMP_FILE_TEMPLATE = "ibex_db_sqldump_{}.sql"

VCRUNTIME140 = os.path.join("C:\\", "Windows", "System32", "vcruntime140_1.dll")
VCRUNTIME140_INSTALLER = os.path.join(INST_SHARE_AREA, "kits$", "CompGroup", "ICP", "vcruntime140_installer",
                                      "vc_redist.x64.exe")

SYSTEM_SETUP_PATH = os.path.join(EPICS_PATH, "SystemSetup")

SMALLEST_PERMISSIBLE_MYSQL_DUMP_FILE_IN_BYTES = 100


class MysqlTasks(BaseTasks):
    """
    Tasks relating to installing or maintaining an installation of MySQL on a machine.
    """
    def _get_mysql_dir(self):
        """
        Returns the mysql 8 default install directory if it exists, else 5.7.

        """
        if os.path.exists(MYSQL8_INSTALL_DIR):
            mysql_bin_dir = os.path.join(MYSQL8_INSTALL_DIR, "bin")
        else:
            mysql_bin_dir = os.path.join(MYSQL57_INSTALL_DIR, "bin")

        return mysql_bin_dir

    @task("Truncate database")
    def truncate_database(self):
        """
        Truncate the message log, sample and alarms tables
        """
        try:
            mysql_bin_dir = self._get_mysql_dir()

            sql_command = "truncate table msg_log.message;truncate table archive.sample;truncate table alarm.pv"

            RunProcess(MYSQL_FILES_DIR, "mysql.exe", executable_directory=mysql_bin_dir,
                       prog_args=["-u", "root", "-p",
                                  "--execute", sql_command],
                       capture_pipes=False).run()

        except ErrorInRun as ex:
            self.prompt.prompt_and_raise_if_not_yes(
                f"Unable to run mysql command, please truncate the database manually. "
                f"Error is {ex.message}")

    def _configure_mysql(self):
        """
        Copy mysql settings and run the MySQL configuration script
        """
        my_ini_file = os.path.join(EPICS_PATH, "systemsetup", "my.ini")
        try:
            shutil.copy(my_ini_file, MYSQL8_INSTALL_DIR)
        except (OSError, IOError) as e:
            self.prompt.prompt_and_raise_if_not_yes(f"Couldn't copy my.ini from {my_ini_file} to {MYSQL8_INSTALL_DIR}"
                                                    f" because {e}. Please do this manually confirm when complete."
                                                    )

        # Restart to pick up new my.ini
        admin_commands = AdminCommandBuilder()
        admin_commands.add_command("sc", "stop MYSQL80", expected_return_val=None)
        # Sleep to wait for service to stop so we can restart it.
        admin_commands.add_command("ping", "-n 10 127.0.0.1 >nul", expected_return_val=None)
        admin_commands.add_command("sc", "start MYSQL80", expected_return_val=None)
        admin_commands.run_all()

    def _remove_old_versions_of_mysql8(self, clean_install):
        if clean_install:
            self.prompt.prompt_and_raise_if_not_yes("Warning: this will erase all data held in the MySQL database. "
                                                    "Are you sure you want to continue?")

        admin_commands = AdminCommandBuilder()
        admin_commands.add_command("sc", "stop MYSQL80", expected_return_val=None)
        admin_commands.add_command("sc", "delete MYSQL80", expected_return_val=None)
        admin_commands.run_all()

        sleep(5)  # Time for service to stop

        if os.path.exists(MYSQL8_INSTALL_DIR):
            shutil.rmtree(MYSQL8_INSTALL_DIR)

        if clean_install:
            self._remove_old_mysql_data_dir()

    def _remove_old_mysql_data_dir(self):
        if os.path.exists(MYSQL_FILES_DIR):
            shutil.rmtree(MYSQL_FILES_DIR)

    def _create_mysql_binaries(self):
        os.makedirs(MYSQL8_INSTALL_DIR)

        mysql_unzip_temp = os.path.join(APPS_BASE_DIR, "temp-mysql-unzip")

        with closing(zipfile.ZipFile(MYSQL_ZIP)) as f:
            f.extractall(mysql_unzip_temp)

        mysql_unzip_temp_release = os.path.join(mysql_unzip_temp, "mysql-{}-winx64".format(MYSQL_LATEST_VERSION))
        for item in os.listdir(mysql_unzip_temp_release):
            shutil.move(os.path.join(mysql_unzip_temp_release, item), MYSQL8_INSTALL_DIR)

        shutil.rmtree(mysql_unzip_temp)

    def _initialize_mysql_data_area_for_vhd(self):
        os.makedirs(os.path.join(MYSQL_FILES_DIR, "data"))

        RunProcess(
            working_dir=os.path.join(MYSQL8_INSTALL_DIR, "bin"),
            executable_file="mysqld.exe",
            executable_directory=os.path.join(MYSQL8_INSTALL_DIR, "bin"),
            prog_args=[
                '--datadir={}'.format(os.path.join(MYSQL_FILES_DIR, "data")),
                '--initialize-insecure',
                '--console',
                '--log-error-verbosity=3'
            ]
        ).run()

    def _setup_database_users_and_tables(self, vhd_install=True):
        mysqld = os.path.join(MYSQL8_INSTALL_DIR, "bin", "mysqld.exe")

        sql_password = self.prompt.prompt("Enter the MySQL root password:", UserPrompt.ANY,
                                          os.getenv("MYSQL_PASSWORD", "environment variable not set"),
                                          show_automatic_answer=False)

        if vhd_install:  # Service won't have been started yet
            # spawn service in background
            subprocess.Popen(mysqld, creationflags=DETACHED_PROCESS)

            sleep(5)  # Chance for the service to spawn

        RunProcess(
            executable_directory=os.path.join(MYSQL8_INSTALL_DIR, "bin"),
            working_dir=os.path.join(MYSQL8_INSTALL_DIR, "bin"),
            executable_file="mysql.exe",
            prog_args=[
                '-u',
                'root',
                '-e',
                f'ALTER USER \'root\'@\'localhost\' IDENTIFIED WITH mysql_native_password BY \'{sql_password}\';FLUSH '
                f'privileges; '
                    ,

            ],
            log_command_args=False,  # To make sure password doesn't appear in jenkins log.
        ).run()

        RunProcess(
            working_dir=SYSTEM_SETUP_PATH,
            executable_directory=SYSTEM_SETUP_PATH,
            executable_file="config_mysql.bat",
            prog_args=[sql_password],
            log_command_args=False,  # To make sure password doesn't appear in jenkins log.
        ).run()

        if vhd_install:
            # For VHD install only, stop mysql when done
            RunProcess(
                executable_directory=os.path.join(MYSQL8_INSTALL_DIR, "bin"),
                working_dir=os.path.join(MYSQL8_INSTALL_DIR, "bin"),
                executable_file="mysqladmin.exe",
                prog_args=[
                    "-u",
                    "root",
                    "--password={}".format(sql_password),
                    "shutdown",
                ],
                log_command_args=False,  # To make sure password doesn't appear in jenkins log.
            ).run()

    def _install_latest_mysql8(self, clean_install):
        """
        Install the latest mysql. If this is a clean install remove old data directories first and create a new
        database
        Args:
            clean_install: True to destroy and recreate data directories
        """
        self._create_mysql_binaries()

        mysqld = os.path.join(MYSQL8_INSTALL_DIR, "bin", "mysqld.exe")

        admin_commands = AdminCommandBuilder()
        if clean_install:
            os.makedirs(MYSQL_FILES_DIR)

            admin_commands.add_command(mysqld, '--datadir="{}" --initialize-insecure --console --log-error-verbosity=3'
                                       .format(os.path.join(MYSQL_FILES_DIR, "data")))

        # Wait for initialize since admin runner can't wait for completion.
        # Maybe we can detect completion another way?
        admin_commands.add_command(mysqld, '--install MYSQL80 --datadir="{}"'
                                   .format(os.path.join(MYSQL_FILES_DIR, "data")))

        admin_commands.add_command("sc", "start MYSQL80", expected_return_val=None)
        admin_commands.add_command("sc", "config MYSQL80 start= auto")
        admin_commands.add_command("sc",
                                   "failure MYSQL80 reset= 900 actions= restart/10000/restart/30000/restart/60000")
        admin_commands.add_command("sc", "failureflag MYSQL80 1")
        admin_commands.add_command("netsh", "advfirewall firewall delete rule name=mysqld.exe",
                                   None)  # remove old firewall rules
        admin_commands.add_command("netsh", "advfirewall firewall delete rule name=MYSQL8",
                                   None)  # remove old firewall rules
        admin_commands.add_command("netsh", r"advfirewall firewall add rule name=MYSQL8 dir=in action=allow "
                                            r"program=C:\Instrument\Apps\MySQL\Bin\mysqld.exe enable=yes")

        admin_commands.run_all()

        sleep(5)  # Time for service to start

        if clean_install:
            self._setup_database_users_and_tables(vhd_install=False)

    @task("Install latest MySQL for VHD deployment")
    def install_mysql_for_vhd(self):
        """
        Installs MySQL for the VHD creation build.

        Ensure we start from a clean slate. We are creating VHDs so we can assume that no files should exist in
        C:\instrument\apps\mysql or c:\instrument\var\mysql and delete them if they do exist. This facilitates
        developer testing/resuming the script if it failed halfway through
        """
        for path in [MYSQL_FILES_DIR, MYSQL8_INSTALL_DIR]:
            if os.path.exists(path):
                shutil.rmtree(path)

        self._create_mysql_binaries()
        self._initialize_mysql_data_area_for_vhd()

        my_ini_file = os.path.join(EPICS_PATH, "systemsetup", "my.ini")
        try:
            shutil.copy(my_ini_file, MYSQL8_INSTALL_DIR)
        except (OSError, IOError) as e:
            self.prompt.prompt_and_raise_if_not_yes("Couldn't copy my.ini from {} to {} because {}. "
                                                    "Please do this manually confirm when complete."
                                                    .format(my_ini_file, MYSQL8_INSTALL_DIR, e))

        self._setup_database_users_and_tables(vhd_install=True)

    def _install_vcruntime140(self):
        if not os.path.exists(VCRUNTIME140):
            self.prompt.prompt_and_raise_if_not_yes(
                "MySQL server 8 requires microsoft visual C++ runtime to be installed.\r\n"
                "Install it from {} and confirm when complete".format(VCRUNTIME140_INSTALLER))

    @task("Install latest MySQL")
    def install_mysql(self, force=False):
        """
        Install mysql and the ibex database schemas
        Args:
            force: True delete old data and update
        """
        backup_data = False
        clean_install = True
        if os.path.exists(os.path.join(MYSQL57_INSTALL_DIR, "bin", "mysql.exe")):
            self._backup_data()
            backup_data = True
            self.prompt.prompt_and_raise_if_not_yes("MySQL 5.7 detected. Please use the MySQL installer application"
                                                    "to remove MySQL 5.7. When it asks you whether to remove data"
                                                    "directories, answer yes. Type 'Y' when complete.")

        mysql_8_exe = os.path.join(MYSQL8_INSTALL_DIR, "bin", "mysql.exe")

        if os.path.exists(mysql_8_exe):
            version = subprocess.check_output("{} --version".format(mysql_8_exe))
            if MYSQL_LATEST_VERSION in version and not force:
                answer = self.prompt.prompt("MySQL already appears to be on the latest version ({}) - would you like to"
                                            " force a reinstall anyway? [Y/N]".format(MYSQL_LATEST_VERSION),
                                            possibles=["Y", "N"], default="N")
                if answer == "Y":
                    force = True
                else:
                    return
            clean_install = force
            self._remove_old_versions_of_mysql8(clean_install=clean_install)

        self._install_vcruntime140()
        self._install_latest_mysql8(clean_install=clean_install)
        self._configure_mysql()
        if backup_data:
            self._reload_backup_data()

    @task("Backup database")
    def backup_database(self):
        """
        Backup the database
        """
        result_file = os.path.join(self._get_backup_dir(),
                                   SQLDUMP_FILE_TEMPLATE.format(BaseTasks._today_date_for_filenames()))

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

    def _backup_data(self):
        """
        Backup the data for transfer. This dumps just the data not the schema.
        """
        result_file = os.path.join(self._get_backup_dir(),
                                   SQLDUMP_FILE_TEMPLATE.format(BaseTasks._today_date_for_filenames()))

        mysql_bin_dir = self._get_mysql_dir()
        dump_command = ["-u", "root", "-p", "--single-transaction",
                        "--result-file={}".format(result_file), "--no-create-db", "--no-create-info", "--skip-triggers",
                        "--databases", "alarm", "archive", "exp_data", "iocdb", "journal", "msg_log"]
        RunProcess(MYSQL_FILES_DIR, "mysqldump.exe", executable_directory=mysql_bin_dir,
                   prog_args=dump_command,
                   capture_pipes=False).run()

        if os.path.getsize(result_file) < SMALLEST_PERMISSIBLE_MYSQL_DUMP_FILE_IN_BYTES:
            self.prompt.prompt_and_raise_if_not_yes(
                "Dump file '{}' seems to be small is it correct? ".format(result_file))

    def _reload_backup_data(self):
        """
        Reload backup the data
        """
        result_file = os.path.join(self._get_backup_dir(),
                                   SQLDUMP_FILE_TEMPLATE.format(BaseTasks._today_date_for_filenames()))

        mysql_bin_dir = self._get_mysql_dir()
        read_dump_command = ["-u", "root", "-p", "--force"]
        RunProcess(MYSQL_FILES_DIR, "mysql.exe", executable_directory=mysql_bin_dir,
                   prog_args=read_dump_command,
                   capture_pipes=False, std_in=open(result_file)).run()
        self.prompt.prompt_and_raise_if_not_yes(
            "Check that there are only 16 errors from mysql. These are 1062 error fail to insert primary key. "
            "These are for constants added by the creation script, e.g. archive severity.")
