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
        version = open(f"{EPICS_PATH}/VERSION.txt").read().split()[0] 
        subprocess.call(f"cd {EPICS_PATH} && git remote add origin http://control-svcs.isis.cclrc.ac.uk/gitroot/releases/{version}/EPICS.git", shell=True)
        subprocess.call(f"cd {EPICS_PATH} && git add .", shell=True)
        subprocess.call(f"cd {EPICS_PATH} && git commit -m 'Initial deploy commit'", shell=True)
        subprocess.call(f"cd {EPICS_PATH} && git stash", shell=True)
        subprocess.call(f"cd {EPICS_PATH} && git checkout -b %COMPUTERNAME%", shell=True)
        subprocess.call(f"cd {EPICS_PATH} && git stash pop", shell=True)
        subprocess.call(f"cd {EPICS_PATH} && git push -u origin %COMPUTERNAME%", shell=True)
    