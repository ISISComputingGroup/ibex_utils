import os
import socket
from datetime import date

from ibex_install_utils.ca_utils import CaWrapper
from ibex_install_utils.file_utils import FileUtils
from ibex_install_utils.tasks.common_paths import BACKUP_DIR, BACKUP_DATA_DIR


class BaseTasks(object):
    def __init__(self, user_prompt, server_source_dir, client_source_dir, client_e4_source_dir, genie_python3_dir,
                 file_utils=FileUtils()):
        """
        Initializer.
        Args:
            user_prompt (ibex_install_utils.user_prompt.UserPrompt): a object to allow prompting of the user
            server_source_dir: directory to install ibex server from
            client_source_dir: directory to install ibex client from
            client_e4_source_dir: directory to install ibex E4 client from
            genie_python3_dir: directory to install genie python from
            file_utils : collection of file utilities
        """
        self.prompt = user_prompt  # This is needed to allow @tasks to work
        self._server_source_dir = server_source_dir
        self._client_source_dir = client_source_dir
        self._client_e4_source_dir = client_e4_source_dir
        self._genie_python_3_source_dir = genie_python3_dir
        self._file_utils = file_utils

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
    def _get_backup_dir():
        """
        Returns: The backup dir, will create it if needed (both old and dir).
        Raises: IOError if the base dir doesn't exist
        """
        new_backup_dir = os.path.join(BACKUP_DIR, "ibex_backup_{}".format(BaseTasks._today_date_for_filenames()))

        if not os.path.exists(BACKUP_DATA_DIR):
            raise IOError("Base directory does not exist {} should be a provided linked dir".format(BACKUP_DATA_DIR))
        if not os.path.exists(BACKUP_DIR):
            os.mkdir(BACKUP_DIR)
        if not os.path.exists(new_backup_dir):
            os.mkdir(new_backup_dir)
        return new_backup_dir

