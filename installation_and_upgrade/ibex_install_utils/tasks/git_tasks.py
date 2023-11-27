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
        subprocess.call(f"cd {EPICS_PATH} && git remote add release http://control-svcs.isis.cclrc.ac.uk/gitroot/releases/{version}/EPICS.git", shell=True)
        print("Added remote")
        subprocess.call(f"cd {EPICS_PATH} && git add .", shell=True)
        print("Added any changes")
        subprocess.call(f'cd {EPICS_PATH} && git commit -m "Initial deploy commit"', shell=True)
        print("Committed any changes")
        subprocess.call(f"cd {EPICS_PATH} && git stash", shell=True)
        print("Stashed any changes")
        subprocess.call(f"cd {EPICS_PATH} && git checkout -b %COMPUTERNAME%", shell=True)
        print("Checked out to the new branch")
        subprocess.call(f"cd {EPICS_PATH} && git stash pop", shell=True)
        print("Popped stash")
        subprocess.call(f"cd {EPICS_PATH} && git push -u release %COMPUTERNAME%", shell=True)
        print("Pushed to remote")
    