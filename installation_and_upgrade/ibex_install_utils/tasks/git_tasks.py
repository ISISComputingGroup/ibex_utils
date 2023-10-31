import subprocess

from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import EPICS_PATH

class GitTasks(BaseTasks):

    @task(f"Show Git status in {EPICS_PATH}")
    def show_git_status(self):
        subprocess.call(f"cd {EPICS_PATH} && git status", shell=True)
    