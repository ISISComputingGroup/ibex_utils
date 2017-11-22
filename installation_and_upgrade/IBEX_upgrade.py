"""
Script to install IBEX to various machines
"""

import argparse
import os
import sys

from ibex_install_utils.install_tasks import UpgradeInstrument
from ibex_install_utils.exceptions import UserStop, ErrorInTask
from ibex_install_utils.user_prompt import UserPrompt


def _get_latest_directory_path(build_dir, directory_above_build_num):
    latest_build_path = os.path.join(build_dir, "LATEST_BUILD.txt")
    build_num = None
    for line in open(latest_build_path):
        build_num = line.strip()
    if build_num is None or build_num == "":
        print("Latest build num unknown. Cannot read it from '{0}'".format(latest_build_path))
        sys.exit(3)
    return os.path.join(build_dir, "BUILD-{}".format(build_num), directory_above_build_num)


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
    parser.add_argument("--kits_icp_dir", default=None, help="Directory of kits/ICP")

    parser.add_argument('deployment_type', choices=['training_update', 'instrument_update', 'install_latest'],
                        help="What upgrade should be performed")

    args = parser.parse_args()

    if args.release_dir is not None:
        server_dir = os.path.join(args.release_dir, "EPICS")
        client_dir = os.path.join(args.release_dir, "Client")
    elif args.server_dir is not None and args.client_dir is not None:
        server_dir = args.server_dir
        client_dir = args.client_dir
    elif args.server_dir is not None or args.client_dir is not None:
        print("You must specify BOTH the server and client directories.")
        sys.exit(2)
    elif args.kits_icp_dir is not None:
        if args.deployment_type != 'install_latest':
            print("When specifying kits_icp_dir you choose the install latest deployment type.")
            sys.exit(2)
        epics_build_dir = os.path.join(args.kits_icp_dir, "EPICS", "EPICS_win7_x64")
        server_dir = _get_latest_directory_path(epics_build_dir, "EPICS")

        client_build_dir = os.path.join(args.kits_icp_dir, "Client")
        client_dir = _get_latest_directory_path(client_build_dir, "Client")
    else:
        print("You must specify either the release directory or kits_icp_dir or "
              "BOTH the server and client directories.")
        sys.exit(2)

    prompt = UserPrompt(args.quiet, args.confirm_step)
    upgrade_instrument = UpgradeInstrument(prompt, server_dir, client_dir)

    try:
        if args.deployment_type == "training_update":
            upgrade_instrument.run_test_update()
        elif args.deployment_type == "install_latest":
            upgrade_instrument.remove_all_and_install_client_and_server()
        elif args.deployment_type == "instrument_update":
            upgrade_instrument.run_instrument_update()

    except UserStop:
        print ("Stopping upgrade")
        sys.exit(0)
    except ErrorInTask as error_in_run_ex:
        print("Error in upgrade: {0}".format(error_in_run_ex.message))
        sys.exit(1)

    print ("Finished upgrade")
