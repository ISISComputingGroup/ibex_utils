import subprocess

from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.git_tasks import GitTasks
from ibex_install_utils.tasks.common_paths import SCRIPTS_BASE_DIR
from ibex_install_utils.user_prompt import UserPrompt

class UpdateScripts(BaseTasks):
    
    @task(f"Update scripts repo by merging master branch into instrument branch?")
    def update_scripts(self):
        try:
            subprocess.check_call(f"cd /d {SCRIPTS_BASE_DIR}", shell=True)
            git_instance = GitTasks(self.prompt,'','','','')
            git_instance.automatic_merge_of_git_remote("origin/master", f"%COMPUTERNAME%", SCRIPTS_BASE_DIR)
        except subprocess.CalledProcessError as e:
            print(f"{e}")

if __name__ == "__main__":
    prompt = UserPrompt(True,False)
    UpdateScripts(prompt, "", "", "", "", "").update_scripts()



