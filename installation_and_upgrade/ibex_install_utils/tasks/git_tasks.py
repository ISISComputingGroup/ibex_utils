import subprocess

from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import EPICS_PATH
from genie_python import genie as g

class GitTasks(BaseTasks):

    @task(f"Show Git status in {EPICS_PATH}")
    def show_git_status(self):
        subprocess.call(f"cd {EPICS_PATH} && git status", shell=True)

    @task(f"Swap instrument git branch to release on CONTROL-SVCS")
    def checkout_to_release_branch(self):
        subprocess.call(f"cd {EPICS_PATH}", shell=True)
        version = open(f"{EPICS_PATH}/VERSION.txt").read().split()[0] 
        subprocess.call(f"git remote add origin http://control-svcs.isis.cclrc.ac.uk/gitroot/releases/{version}/EPICS.git", shell=True)
        inst_name = g.my_pv_prefix.split(":")[1]
        subprocess.call(f"git checkout -b {inst_name}", shell=True)
        subprocess.call(f"git push -u origin {inst_name}", shell=True)
    