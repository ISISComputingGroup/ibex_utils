"""
Script to install IBEX to a machine which has had VHDs mounted
"""
import sys
import traceback

from ibex_install_utils.install_tasks import UpgradeInstrument
from ibex_install_utils.exceptions import UserStop, ErrorInTask
from ibex_install_utils.user_prompt import UserPrompt


if __name__ == "__main__":
    try:
        prompt = UserPrompt(automatic=True, confirm_steps=False)
        upgrade_instrument = UpgradeInstrument(prompt, None, None, None, None, None)
        upgrade_instrument.windows_10_vhd_deploy()
    except UserStop:
        print("User stopped upgrade")
        sys.exit(2)
    except ErrorInTask as error_in_run_ex:
        traceback.print_exc()
        sys.exit(1)

    print("Finished upgrade")
    sys.exit(0)
