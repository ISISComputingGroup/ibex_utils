import os
import socket
from datetime import date

from ibex_install_utils.ca_utils import CaWrapper
from ibex_install_utils.file_utils import FileUtils
from ibex_install_utils.tasks.common_paths import BACKUP_DATA_DIR, BACKUP_DIR


class BaseTasks:
    _backup_dir = None

    def __init__(self, user_prompt, server_source_dir, client_source_dir, genie_python3_dir,
                 ibex_version, file_utils=FileUtils()):
        """
        Initializer.
        Args:
            user_prompt (ibex_install_utils.user_prompt.UserPrompt): a object to allow prompting of the user
            server_source_dir: directory to install ibex server from
            client_source_dir: directory to install ibex client from
            genie_python3_dir: directory to install genie python from
            file_utils : collection of file utilities
            ibex_version : the version of ibex being installed
        """
        self.prompt = user_prompt  # This is needed to allow @tasks to work
        self._server_source_dir = server_source_dir
        self._client_source_dir = client_source_dir
        self._genie_python_3_source_dir = genie_python3_dir
        self._file_utils = file_utils
        self._ibex_version = ibex_version

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
        return BaseTasks._get_machine_name().replace("NDX", "")

    @staticmethod
    def _today_date_for_filenames():
        return date.today().strftime("%Y_%m_%d")

    @staticmethod 
    def _generate_backup_dir_name():
        return f"ibex_backup_{BaseTasks._today_date_for_filenames()}"

    @staticmethod
    def _get_backup_dir():
        """
        The backup directory contains the date of backup, if this script is
        running over multiple days this will return the date this method was first called.
        
        Returns: The backup dir, will create it if needed (both old and dir).
        Raises: IOError if the base dir doesn't exist
        """
        # Return cached backup directory if there is one
        if BaseTasks._backup_dir is not None:
            return BaseTasks._backup_dir
        
        new_backup_dir = os.path.join(BACKUP_DIR, BaseTasks._generate_backup_dir_name())

        if not os.path.exists(BACKUP_DATA_DIR):
            # data dir is a linked directory on real instrument machines so can't just simply be created with mkdir
            raise IOError(f"Base directory does not exist {BACKUP_DATA_DIR} should be a provided linked dir")
        
        os.makedirs(new_backup_dir, exist_ok=True)

        # cache backup dir name (useful when backup happens over multiple days)
        # it will always refer to the date when backup was started
        BaseTasks._backup_dir = new_backup_dir
        return new_backup_dir

