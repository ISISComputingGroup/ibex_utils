import os

from ibex_install_utils.run_process import RunProcess
from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import APPS_BASE_DIR


class PythonTasks(BaseTasks):
    """
    Tasks relating to installing or maintaining an installation of genie_python.
    """
    @task("Installing Genie Python 3")
    def install_genie_python3(self):
        """
        Install ibex server.
        """
        self._file_utils.mkdir_recursive(APPS_BASE_DIR)
        RunProcess(self._genie_python_3_source_dir, "genie_python_install.bat").run()

    @task("Update script generator script definitions")
    def update_script_definitions(self):
        """
        Update (or at least ask the user to update) the script definitions used by the script generator.
        """
        if os.path.exists("C:\\ScriptGeneratorConfigs") or os.path.exists("C:\\ScriptDefinitions"):
            self.prompt.prompt("Update the script definitions for the script generator (likely in C:\\ScriptDefinitions or C:\\ScriptGeneratorConfigs)." + \
                "Check with the scientists that it is ok to do this." + \
                "You can do it by git pull, you may need to merge changes made on the instrument.")