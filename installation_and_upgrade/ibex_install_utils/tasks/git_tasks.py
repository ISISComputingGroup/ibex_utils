import re
import subprocess

from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import EPICS_PATH


class GitTasks(BaseTasks):
    @task(f"Show Git status in {EPICS_PATH}")
    def show_git_status(self):
        subprocess.call(f"cd {EPICS_PATH} && git status", shell=True)

    @task("Swap instrument git branch to release on CONTROL-SVCS")
    def checkout_to_release_branch(self):
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
                f"cd {EPICS_PATH} && git remote add origin http://control-svcs.isis.cclrc.ac.uk/gitroot/releases/{version}/{remote_repo}",
                shell=True,
            )
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
            subprocess.check_call(
                f"cd {EPICS_PATH} && git push -u origin %COMPUTERNAME%", shell=True
            )
            print("Pushed to the remote")
        except subprocess.CalledProcessError as e:
            print(f"Error checking out to new release branch and push: {e}")
            print("Branch may previously exist either locally or remotely - intervention required")


# something for the future in case creting new beranch fails - maybe one exists we want to use?
#            try:
#                subprocess.check_call(f"cd {EPICS_PATH} && git checkout %COMPUTERNAME%", shell=True)
#                print("Switched to existing release branch")
#            except subprocess.CalledProcessError as e:
#                print(f"Error switching to existing release branch and push: {e}")
