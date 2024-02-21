import subprocess

from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import SCRIPTS_BASE_DIR
from ibex_install_utils.user_prompt import UserPrompt

class UpdateScripts(BaseTasks):
    
    @task(f"Update scripts repo by merging master branch into instrument branch?")
    def update_scripts(self):
        
        try:
            subprocess.check_call(f"cd {SCRIPTS_BASE_DIR} && git checkout %COMPUTERNAME% || git checkout -b %COMPUTERNAME%", shell=True)
            print("Checked out to the instrument branch")
        except subprocess.CalledProcessError as e:
            print(f"Error checking out to instrument branch: {e}")

        try:
            subprocess.check_call(f"cd {SCRIPTS_BASE_DIR} && git fetch --all  && git merge master", shell=True)
            print("Fetching all changes and merging")
        except subprocess.CalledProcessError as e:
            print(f"Error Fetching all changes and merging: {e}")

        
        try:
            subprocess.check_call(f"cd {SCRIPTS_BASE_DIR} && git push -u origin %COMPUTERNAME%", shell=True)
            print("Pushing to branch")
        except subprocess.CalledProcessError as e:
            print(f"Error pushing to branch: {e}")
            
if __name__ == "__main__":
    prompt = UserPrompt(False,True)
    UpdateScripts(prompt, "", "", "", "", "").update_scripts()
