import subprocess

from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import SCRIPTS_BASE_DIR

class UpdateScripts(BaseTasks):
    
    @task(f"Update scripts repo by merging master branch into instrument branch?")
    def update_scripts(self):
        try:
            subprocess.check_call(f"cd {SCRIPTS_BASE_DIR} && git checkout master", shell=True)
            print("Checking out master")
        except subprocess.CalledProcessError as e:
            print(f"Error checking out master branch: {e}")
        
        try:
            subprocess.check_call(f"cd {SCRIPTS_BASE_DIR} && git pull", shell=True)
            print("Fetched remote")
        except subprocess.CalledProcessError as e:
            print(f"Error fetching remote: {e}")

        try:
            subprocess.check_call(f"cd {SCRIPTS_BASE_DIR} && git checkout -b %COMPUTERNAME%", shell=True)
            print("Checked out to the instrument branch")
        except subprocess.CalledProcessError as e:
            print(f"Error checking out to new release branch and push: {e}")
            
        try: 
            subprocess.check_call(f"cd {SCRIPTS_BASE_DIR} && git merge master", shell=True)
            print(f"Merging master into instrument scripts branch")
        except subprocess.CalledProcessError as e:
            print(f"Error merging master: {e}")

        try:
            # run a git status to rebuild index if needed 
            subprocess.check_call(f"cd {SCRIPTS_BASE_DIR} && git status", shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running git status: {e}")
        
        