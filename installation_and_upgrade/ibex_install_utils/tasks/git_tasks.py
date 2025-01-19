import re
import subprocess

from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import EPICS_PATH


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
