"""
Script to install IBEX to various machines
"""

import argparse
import os
import sys

from ibex_install_utils.install_tasks import UpgradeInstrument
from ibex_install_utils.exceptions import UserStop, ErrorInTask
from ibex_install_utils.user_prompt import UserPrompt

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upgrade the instrument.')

    parser.add_argument("--release_dir", dest="release_dir", default=None,
                        help="directory from which the client and server should be installed")
    parser.add_argument("--server_dir", default=None, help="Directory from which IBEX server should be installed")
    parser.add_argument("--client_dir", default=None, help="Directory from which IBEX client should be installed")
    parser.add_argument("--confirm_step", default=False, action="store_true",
                        help="Confirm each major action before performing it")
    parser.add_argument("--quiet", default=False, action="store_true",
                        help="Do not ask any questions just to the default.")

    upgrade_types = ['training_update', 'demo_upgrade', 'instrument_update', 'instrument_deploy']
    parser.add_argument('deployment_type', choices=upgrade_types,
                        help="What upgrade should be performed")

    args = parser.parse_args()

    if (args.release_dir is None) and (args.server_dir is None or args.client_dir is None):
        print("You must specify either the release directory or BOTH the server and client directories.")
        sys.exit(2)

    if args.release_dir is None:
        server_dir = args.server_dir
        client_dir = args.client_dir
    else:
        server_dir = os.path.join(args.release_dir, "EPICS")
        client_dir = os.path.join(args.release_dir, "Client")

    prompt = UserPrompt(args.quiet, args.confirm_step)
    upgrade_instrument = UpgradeInstrument(prompt, server_dir, client_dir)

    try:
        if args.deployment_type == "training_update":
            upgrade_instrument.run_test_update()
        elif args.deployment_type == "demo_upgrade":
            upgrade_instrument.run_demo_upgrade()
        elif args.deployment_type == "instrument_update":
            upgrade_instrument.run_instrument_update()
        elif args.deployment_type == "instrument_deploy":
            upgrade_instrument.run_instrument_upgrade()

    except UserStop:
        print ("Stopping upgrade")
        sys.exit(0)
    except ErrorInTask as error_in_run_ex:
        print("Error in upgrade: {0}".format(error_in_run_ex.message))
        sys.exit(1)

    print ("Finished upgrade")
