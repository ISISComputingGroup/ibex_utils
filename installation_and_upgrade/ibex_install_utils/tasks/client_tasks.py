import os
import subprocess

from installation_and_upgrade.ibex_install_utils.run_process import RunProcess
from installation_and_upgrade.ibex_install_utils.task import task
from installation_and_upgrade.ibex_install_utils.tasks import BaseTasks
from installation_and_upgrade.ibex_install_utils.tasks.common_paths import APPS_BASE_DIR, GUI_PATH_E4


class ClientTasks(BaseTasks):

    @task("Installing IBEX Client")
    def install_ibex_client(self):
        """
        Install the ibex client (which also installs genie python).

        """
        self._install_set_version_of_ibex_client(self._client_source_dir)

    @task("Installing IBEX Client")
    def install_e4_ibex_client(self):
        """
        Install the ibex client E4 version (which also installs genie python).

        """
        source_dir = self._client_e4_source_dir
        if source_dir is None:
            self.prompt.prompt_and_raise_if_not_yes("The E4 client path has not been set; continue with installation?")
        else:
            self._install_set_version_of_ibex_client(source_dir)

    def _install_set_version_of_ibex_client(self, source_dir):
        """
        Install a given version of the Ibex client.
        Args:
            source_dir: source directory for the client
        """
        self._file_utils.mkdir_recursive(APPS_BASE_DIR)

        RunProcess(source_dir, "install_client.bat", press_any_key=True).run()

    @task("Starting IBEX gui")
    def start_ibex_gui(self):
        """
        Start the IBEX GUI
        :return:
        """
        subprocess.Popen([os.path.join(GUI_PATH_E4, "ibex-client.exe")], cwd=GUI_PATH_E4)

    @task("Client release tests")
    def perform_client_tests(self):
        """
        Test that the client works
        """
        self.prompt.prompt_and_raise_if_not_yes(
            "Check that the version displayed in the client is as expected after the deployment")
        self.prompt.prompt_and_raise_if_not_yes(
            "Confirm that genie_python works from within the client and via genie_python.bat (this includes"
            "verifying that the 'g.' and 'inst.' prefixes work as expected)"
            "If the font cannot be seen in the genie_python.bat change default terminal colours to white on black.")
        self.prompt.prompt_and_raise_if_not_yes(
            "Verify that the current configuration is consistent with the system prior to upgrade")
        self.prompt.prompt_and_raise_if_not_yes(
            "Verify that all the links from the 'Weblinks' perspective still work (i.e. the address gets resolved)")
        self.prompt.prompt_and_raise_if_not_yes(
            "Verify that the dashboard gives the instrument name with no NDX prefix (if it does switch to the current instrument)")