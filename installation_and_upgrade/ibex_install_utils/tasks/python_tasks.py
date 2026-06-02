import os

from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import INSTRUMENT_BASE_DIR


class PythonTasks(BaseTasks):
    """
    Tasks relating to installing or maintaining an installation of genie_python.
    """

    @task("Update script generator script definitions")
    def update_script_definitions(self) -> None:
        """
        Prompt the user to update the script definitions used by the script generator.
        """
        if os.path.exists("C:\\ScriptGeneratorConfigs") or os.path.exists("C:\\ScriptDefinitions"):
            print(
                "Update the script definitions for the script generator"
                " (likely in C:\\ScriptDefinitions or C:\\ScriptGeneratorConfigs)."
                + "Check with the scientists that it is ok to do this."
                + "You can do it by git pull, you may need to merge changes made on the instrument."
            )

    @task("Remove instrument scripts githooks")
    def remove_instrument_script_githooks(self) -> None:
        """
        Remove the githooks in the instrument scripts dierectory
        """
        hook_path = os.path.join(INSTRUMENT_BASE_DIR, "scripts", ".git", "hooks", "commit-msg")
        if os.path.exists(hook_path):
            try:
                os.remove(hook_path)
            except Exception as e:
                print(f"Unable to remove {hook_path}: {e}")
