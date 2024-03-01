import subprocess

from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import EPICS_PATH, SETTINGS_CONFIG_PATH
from ibex_install_utils.exceptions import ErrorInRun, ErrorInTask
from ibex_install_utils.user_prompt import UserPrompt
from genie_python import genie as g
import re
import git
import os

class GitTasks(BaseTasks):

    @task(f"Show Git status in {EPICS_PATH}")
    def show_git_status(self):
        subprocess.call(f"cd {EPICS_PATH} && git status", shell=True)

    @task(f"Swap instrument git branch to release on CONTROL-SVCS")
    def checkout_to_release_branch(self):
        version_pattern = r'^\d+\.\d+\.\d+$'
        if self._server_source_dir.endswith('32'):
            remote_repo = "EPICS32.git"
        else:
            remote_repo = "EPICS.git"

        with open(f"{EPICS_PATH}/VERSION.txt") as file:
            version = file.read().split()[0]

        if re.match(version_pattern, version) is None:
            # assume nightly build so don't want to make new branch/checkout
            print(f"Version {version} is not a release version, skipping swapping to release branch")
            return
        
        try:
            # assumes the alias 'origin' does not exist yet
            subprocess.check_call(f"cd {EPICS_PATH} && git remote add origin http://control-svcs.isis.cclrc.ac.uk/gitroot/releases/{version}/{remote_repo}", shell=True)
            print("Added the remote")
        except subprocess.CalledProcessError as e:
            print(f"Error creating remote: {e}")
        
        try:
            subprocess.check_call(f"cd {EPICS_PATH} && git fetch", shell=True)
            print("Fetched remote")
        except subprocess.CalledProcessError as e:
            print(f"Error fetching remote: {e}")
        
        try:
            # run a git status to rebuild index if needed 
            subprocess.check_call(f"cd {EPICS_PATH} && git status", shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running git status: {e}")

        try:
            subprocess.check_call(f"cd {EPICS_PATH} && git checkout -b %COMPUTERNAME%", shell=True)
            print("Checked out to the new release branch")
            subprocess.check_call(f"cd {EPICS_PATH} && git push -u origin %COMPUTERNAME%", shell=True)
            print("Pushed to the remote")
        except subprocess.CalledProcessError as e:
            print(f"Error checking out to new release branch and push: {e}")
            print(f"Branch may previously exist either locally or remotely - intervention required")

# something for the future in case creting new beranch fails - maybe one exists we want to use?
#            try:
#                subprocess.check_call(f"cd {EPICS_PATH} && git checkout %COMPUTERNAME%", shell=True)
#                print("Switched to existing release branch")
#            except subprocess.CalledProcessError as e:
#                print(f"Error switching to existing release branch and push: {e}")
    
    #Method to check that the machine name matches a git branch
    def inst_name_matches_branch():
        repo = git.Repo(
            os.path.join(SETTINGS_CONFIG_PATH, BaseTasks._get_machine_name())
        )
        if repo.active_branch.name != BaseTasks._get_machine_name():
            print(
                f"Git branch, '{repo.active_branch}', is not the same as machine name ,'{BaseTasks._get_machine_name()}' "
            )
            raise ErrorInTask("Git branch is not the same as machine name")

    @task(f"Attempt automatic merge of one branch into another")
    def automatic_merge_of_git_remote(self, branch_to_merge_from, branch_to_merge_to, dir):
        f"""
        Attempt an automatic merge of one branch {branch_to_merge_from} to another, {branch_to_merge_to} in {dir}
        """
        manual_prompt = (
            "Merge the master configurations branch into the instrument configuration. "
            "From C:\Instrument\Settings\config\[machine name] run:\n"
            "    0. Clean up any in progress merge (e.g. git merge --abort)\n"
            "    1. git checkout master\n"
            "    2. git pull\n"
            "    3. git checkout [machine name]\n"
            "    4. git merge master\n"
            "    5. Resolve any merge conflicts\n"
            "    6. git push\n"
        )
            
        automatic_prompt = "Attempt automatic merge?"
        repo = git.Repo(dir)
        if self.prompt.confirm_step(automatic_prompt):     
            try:
                try:
                    print(f"     fetch: {repo.git.fetch()}")
                    print(f"     merge: {repo.git.merge(f'{branch_to_merge_from}')}")
                except git.GitCommandError as e:
                    # do gc and prune to remove issues with stale references
                    # this does a pack that takes a while, hence not do every time
                    print(f"Retrying git operations after a prune due to {e}")
                    print(f"        gc: {repo.git.gc(prune='now')}")
                    print(f"     prune: {repo.git.remote('prune', 'origin')}")
                    print(f"     fetch: {repo.git.fetch()}")
                    print(f"     merge: {repo.git.merge(f'{branch_to_merge_from}')}")
                    # no longer push let the instrument do that on start up if needed
            except git.GitCommandError as e:
                print(
                    f"Error doing automatic merge, please perform the merge manually: {e}"
                )
            self.prompt.prompt_and_raise_if_not_yes(manual_prompt)
        else:
            self.prompt.prompt_and_raise_if_not_yes(manual_prompt)

if __name__ == "__main__":
    """For running task standalone
    Must be called with pythonpath set to `<exact path on your pc>/installation_and_upgrade`
    as that is the root of this module and all our imports work that way.

    This effectively means to call `set PYTHONPATH=. && python ibex_install_utils/tasks/backup_tasks.py`
    from the installation_and_upgrade directory in terminal.
    """
    print("")

    #! Copying older backups to share will likely fail on developer machines
    prompt = UserPrompt(False, True)
    
    git_instance = GitTasks(prompt,'','','','')
    git_instance.automatic_merge_of_git_remote("branch1", "branch2", "C:/test")
