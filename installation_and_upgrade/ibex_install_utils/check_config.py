import os
import tempfile
import subprocess

from git.repo import Repo
from genie_python import genie as g

from ibex_install_utils.user_prompt import UserPrompt


PYTHON = os.path.join("C:\\", "Instrument", "Apps", "Python3", "genie_python.bat")
CONFIG_CHECKER_REPO = "https://github.com/ISISComputingGroup/InstrumentChecker.git"
CONFIGS_REPO = "http://spudulike@control-svcs.isis.cclrc.ac.uk/gitroot/instconfigs/inst.git"
GUI_REPO = "https://github.com/ISISComputingGroup/ibex_gui.git"
CONFIGS_DIR = "configs"
GUI_DIR = "gui"
TEST_REPORTS_DIR = "test-reports"


def check_config():
    """
    Sets up the Configuration Check repository and runs the tests for the current instrument.
    """
    prompt = UserPrompt(automatic=False, confirm_steps=True)

    if not prompt.confirm_step("Configuration checker"):
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        Repo.clone_from(CONFIG_CHECKER_REPO, tmpdir)
        Repo.clone_from(CONFIGS_REPO, os.path.join(tmpdir, CONFIGS_DIR))
        Repo.clone_from(GUI_REPO, os.path.join(tmpdir, GUI_DIR))

        args = [PYTHON, "-u", "run_tests.py",
                "--configs_repo_path", CONFIGS_DIR,
                "--gui_repo_path", GUI_DIR,
                "--reports_path", TEST_REPORTS_DIR,
                "--instruments", g.adv.get_instrument()]

        while True:
            result = subprocess.run(args, cwd=tmpdir)

            if result.returncode == 0:
                break
            
            if not prompt.confirm_step("Re-run configuration checker"):
                break
