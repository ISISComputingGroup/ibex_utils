import re
import subprocess

import git
from git import PathLike
from ibex_install_utils.exceptions import ErrorInTask
from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import EPICS_PATH
from ibex_install_utils.user_prompt import UserPrompt


class GitTasks(BaseTasks):
    @task(f"Show Git status in {EPICS_PATH}")
    def show_git_status(self) -> None:
        subprocess.call(f"cd /d {EPICS_PATH} && git status", shell=True)

    @task("Swap instrument git branch to release on CONTROL-SVCS")
    def checkout_to_release_branch(self) -> None:
        version_pattern = r"^\d+\.\d+\.\d+$"
        if self._server_source_dir.endswith("32"):
            remote_repo = "EPICS32.git"
        else:
            remote_repo = "EPICS.git"

        with open(f"{EPICS_PATH}/VERSION.txt") as file:
            version = file.read().split()[0]

        if re.match(version_pattern, version) is None:
            # assume nightly build so don't want to make new branch/checkout
            print(
                f"Version {version} is not a release version, skipping swapping to release branch"
            )
            return

        try:
            # assumes the alias 'origin' does not exist yet
            subprocess.check_call(
                f"cd /d {EPICS_PATH} && git remote add origin http://control-svcs.isis.cclrc.ac.uk/gitroot/releases/{version}/{remote_repo}",
                shell=True,
            )
            print("Added the remote")
        except subprocess.CalledProcessError as e:
            print(f"Error creating remote: {e}")

        try:
            subprocess.check_call(f"cd /d {EPICS_PATH} && git fetch", shell=True)
            print("Fetching from remote")
        except subprocess.CalledProcessError as e:
            print(f"Error fetching remote: {e}")

        try:
            # run a git status to rebuild index if needed
            subprocess.check_call(f"cd /d {EPICS_PATH} && git status", shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running git status: {e}")

        # this sets upstream tracking on all local branches not just current one
        try:
            subprocess.check_call(
                f"cd /d {EPICS_PATH} && FOR /F \"delims=* \" %i IN ('git branch') "
                "DO git branch --set-upstream-to=origin/%i %i",
                shell=True,
            )
            print("Set branch upstream tracking")
        except subprocess.CalledProcessError as e:
            print(f"Error setting branch upstream tracking: {e}")

        try:
            subprocess.check_call(f"cd /d {EPICS_PATH} && git pull", shell=True)
            print("Pulled current branch from remote")
        except subprocess.CalledProcessError as e:
            print(f"Error pulling from remote: {e}")

        try:
            # run a git status to rebuild index if needed
            subprocess.check_call(f"cd /d {EPICS_PATH} && git status", shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running git status: {e}")

        try:
            subprocess.check_call(
                f"cd /d {EPICS_PATH} && git checkout -b %COMPUTERNAME%", shell=True
            )
            print("Checked out to the new release branch")
            subprocess.check_call(
                f"cd /d {EPICS_PATH} && git push -u origin %COMPUTERNAME%", shell=True
            )
            print("Pushed to the remote")
        except subprocess.CalledProcessError as e:
            print(f"Error checking out to new release branch and push: {e}")
            print("Branch may previously exist either locally or remotely - intervention required")


def try_to_merge_master_into_repo(
    prompt: UserPrompt, repo_path: str | PathLike | None, pull_first: bool = False
) -> None:
    manual_prompt = (
        "Merge the master branch into the local branch."
        f"From {repo_path} run:\n"
        "    0. Clean up any in progress merge (e.g. git merge --abort)\n"
        "    1. git checkout master\n"
        "    2. git pull\n"
        "    3. git checkout [machine name]\n"
        "    4. git merge master\n"
        "    5. Resolve any merge conflicts\n"
        "    6. git push\n"
    )
    automatic_prompt = "Attempt automatic branch merge?"
    if prompt.confirm_step(automatic_prompt):
        try:
            repo = git.Repo(repo_path)
            if pull_first:
                repo.git.pull()
            if repo.active_branch.name != BaseTasks._get_machine_name():
                print(
                    f"Git branch, '{repo.active_branch}', is not the same as"
                    f" machine name ,'{BaseTasks._get_machine_name()}' "
                )
                raise ErrorInTask("Git branch is not the same as machine name")
            try:
                print(f"     fetch: {repo.git.fetch()}")
                print(f"     merge: {repo.git.merge('origin/master')}")
            except git.GitCommandError as e:
                # do gc and prune to remove issues with stale references
                # this does a pack that takes a while, hence not do every time
                print(f"Retrying git operations after a prune due to {e}")
                print(f"        gc: {repo.git.gc(prune='now')}")
                print(f"     prune: {repo.git.remote('prune', 'origin')}")
                print(f"     fetch: {repo.git.fetch()}")
                print(f"     merge: {repo.git.merge('origin/master')}")
        except git.GitCommandError as e:
            print(f"Error doing automatic merge, please perform the merge manually: {e}")
            prompt.prompt_and_raise_if_not_yes(manual_prompt)
    else:
        prompt.prompt_and_raise_if_not_yes(manual_prompt)
