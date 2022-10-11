"""
Script to install IBEX to various machines
"""

import argparse
import os
import re
import sys
import semantic_version

from ibex_install_utils.install_tasks import UpgradeInstrument, UPGRADE_TYPES
from ibex_install_utils.exceptions import UserStop, ErrorInTask
from ibex_install_utils.user_prompt import UserPrompt
from ibex_install_utils.file_utils import get_latest_directory_path


def _get_latest_release_path(release_dir):
    regex = re.compile(r'^\d+\.\d+\.\d+$')

    releases = [name for name in os.listdir(release_dir) if os.path.isdir(os.path.join(release_dir, name))]
    releases = list(filter(regex.match, releases))
    releases = sorted(list(filter(regex.match, releases)), key=semantic_version.Version)

    if len(releases) == 0:
        print(f"Error: No releases found in '{release_dir}'")
        sys.exit(3)
    current_release = releases[-1]
    return os.path.join(release_dir, f"{current_release}")

def _get_latest_existing_dir_path(release_dir, component):
    regex = re.compile(r'^\d+\.\d+\.\d+$')

    releases = [name for name in os.listdir(release_dir) if os.path.isdir(os.path.join(release_dir, name))]
    releases = sorted(list(filter(regex.match, releases)), key=semantic_version.Version, reverse=True)

    if len(releases) == 0:
        print(f"Error: No releases found in '{release_dir}'")
        sys.exit(3)

    for release in releases:
        dir_path = os.path.join(release_dir, release, component)
        if os.path.isdir(dir_path):
            return dir_path

    print(f"Error: No {component} directory found in {release_dir}.")
    sys.exit(3)

# Key is name, value is directory.
DIRECTORIES = {
    "EPICS": "",
    "Client": "",
    "genie_python_3": ""
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upgrade the instrument.',
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--release_dir", dest="release_dir", default=None,
                        help="directory from which the client and server should be installed")
    parser.add_argument("--release_suffix", dest="release_suffix", default="",
                        help="Suffix for specifying non-standard releases "
                             "(such as those including hot fixes)")
    parser.add_argument("--server_build_prefix", default="EPICS", help="Prefix for build directory name")
    parser.add_argument("--server_dir", default=None, help="Directory from which IBEX server should be installed")
    parser.add_argument("--client_dir", default=None, help="Directory from which IBEX client should be installed")
    parser.add_argument("--genie_python3_dir", default=None,
                        help="Directory from which genie_python_3 should be installed")
    parser.add_argument("--confirm_step", default=False, action="store_true",
                        help="Confirm each major action before performing it")
    parser.add_argument("--quiet", default=False, action="store_true",
                        help="Do not ask any questions just to the default.")
    parser.add_argument("--kits_icp_dir", default=None, help="Directory of kits/ICP")
    parser.add_argument("--server_arch", default="x64", choices=["x64", "x86"], help="Server build architecture.")

    deployment_types = [f"{choice}: {deployment_types}"
                        for choice, (_, deployment_types) in UPGRADE_TYPES.items()]
    parser.add_argument('deployment_type', choices=UPGRADE_TYPES.keys(),
                        help="What upgrade should be performed. ( {})"
                        .format(", \n".join(deployment_types)))

    args = parser.parse_args()
    current_client_version = None
    if args.release_dir is not None:
        current_release_dir = os.path.join(args.release_dir, _get_latest_release_path(args.release_dir))
        current_client_version = _get_latest_release_path(args.release_dir).split("\\")[-1]
        if args.release_suffix != "":
            current_release_dir += f"-{args.release_suffix}"

        server_32bit_suffix = "32" if args.server_arch == "x86" else ""
        DIRECTORIES["EPICS"] = os.path.join(current_release_dir, "EPICS" + server_32bit_suffix)
        DIRECTORIES["Client"] = os.path.join(current_release_dir, "Client")
        DIRECTORIES["genie_python_3"] = os.path.join(current_release_dir, "genie_python_3")

        partial_release = False
        for key in DIRECTORIES:
            if not os.path.isdir(DIRECTORIES[key]):
                partial_release = True
                if key == "EPICS":
                    print(f"Warning: {key + server_32bit_suffix} is missing from release.")
                    DIRECTORIES[key] = _get_latest_existing_dir_path(args.release_dir, key + server_32bit_suffix)
                else:
                    print(f"Warning: {key} is missing from release.")
                    DIRECTORIES[key] = _get_latest_existing_dir_path(args.release_dir, key)

        if partial_release:
            try:
                missing_prompt = UserPrompt(False, True)
                server_version = DIRECTORIES["EPICS"].split('\\')[-2]
                current_client_version = DIRECTORIES["Client"].split('\\')[-2]
                genie_python_version = DIRECTORIES["genie_python_3"].split('\\')[-2]
                missing_prompt.prompt_and_raise_if_not_yes(f"Would you like to use Server version: {server_version}, "
                                                           f"Client version: {current_client_version}, "
                                                           f"and Genie Python version: {genie_python_version}?")
            except UserStop:
                print("To specify the directory you want use --server_dir, --client_dir, and --genie_python3_dir "
                      "when running the IBEX_upgrade.py script.")
                sys.exit(2)

    elif args.kits_icp_dir is not None:
        if args.deployment_type == 'install_latest_incr':
            epics_build_dir = os.path.join(args.kits_icp_dir, "EPICS", args.server_build_prefix+"_win7_x64")
        else:
            epics_build_dir = os.path.join(args.kits_icp_dir, "EPICS", args.server_build_prefix+"_CLEAN_win7_x64")

        try:
            DIRECTORIES["EPICS"] = get_latest_directory_path(epics_build_dir, "BUILD-", "EPICS")

            client_build_dir = os.path.join(args.kits_icp_dir, "Client_E4")
            DIRECTORIES["Client"] = get_latest_directory_path(client_build_dir, "BUILD")

            genie_python3_build_dir = os.path.join(args.kits_icp_dir, "genie_python_3")
            DIRECTORIES["genie_python_3"] = get_latest_directory_path(genie_python3_build_dir, "BUILD-")
        except IOError as e:
            print(e)
            sys.exit(3)

    elif args.server_dir is not None and args.client_dir is not None and args.genie_python3_dir is not None:
        DIRECTORIES["EPICS"] = args.server_dir
        DIRECTORIES["Client"] = args.client_dir
        DIRECTORIES["genie_python_3"] = args.genie_python3_dir
    else:
        print("You must specify either the release directory or kits_icp_dir or "
              "ALL of the server, client and genie python 3 directories.")
        sys.exit(2)

    try:
        prompt = UserPrompt(args.quiet, args.confirm_step)
        upgrade_instrument = UpgradeInstrument(prompt, DIRECTORIES["EPICS"], DIRECTORIES["Client"], DIRECTORIES["genie_python_3"],
                                               current_client_version)
        upgrade_function = UPGRADE_TYPES[args.deployment_type][0]
        upgrade_function(upgrade_instrument)

    except UserStop:
        print("User stopped upgrade")
        sys.exit(2)
    except ErrorInTask as error_in_run_ex:
        print(f"Error in upgrade: {error_in_run_ex}")
        sys.exit(1)

    print("Finished upgrade")
    sys.exit(0)
