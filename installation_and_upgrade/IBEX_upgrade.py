"""
Script to install IBEX to various machines
"""
# pylint: disable=import-error
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

    releases = [name for name in os.listdir(release_dir) if os.path.isdir(os.path.join(release_dir, name))]  # pylint: disable=line-too-long
    releases = list(filter(regex.match, releases))
    releases = sorted(list(filter(regex.match, releases)), key=semantic_version.Version)

    if len(releases) == 0:
        print(f"Error: No releases found in '{release_dir}'")
        sys.exit(3)
    current_release = releases[-1]
    return os.path.join(release_dir, f"{current_release}")

def get_client_version(release_dir):
    """
    Get the latest release directory
    Args:
        release_dir: directory to search for releases
    Returns:
        the latest release directory
    """
    current_client_version = _get_latest_release_path(args.release_dir).split("\\")[-1]
    return current_client_version

def get_latest_release_directory_if_dir(release_dir):
    """
    Get the latest release directory
    Args:
        release_dir: directory to search for releases
    Returns:
        the latest release directory
    """
    current_release_dir = os.path.join(args.release_dir, _get_latest_release_path(args.release_dir))  # pylint: disable=line-too-long
    
    return current_release_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upgrade the instrument.',
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--release_dir", dest="release_dir", default=None,
                        help="directory from which the client and server should be installed")

    parser.add_argument("--release_suffix", dest="release_suffix", default="",
                        help="Suffix for specifying non-standard releases "
                             "(such as those including hot fixes)")

    parser.add_argument("--server_build_prefix", default="EPICS",
    help="Prefix for build directory name")

    parser.add_argument("--server_dir", default=None,
    help="Directory from which IBEX server should be installed")

    parser.add_argument("--client_dir", default=None,
    help="Directory from which IBEX client should be installed")

    parser.add_argument("--client_e4_dir", default=None,
    help="Directory from which IBEX E4 client should be installed")

    parser.add_argument("--genie_python3_dir", default=None,
                        help="Directory from which genie_python_3 should be installed")

    parser.add_argument("--confirm_step", default=False, action="store_true",
                        help="Confirm each major action before performing it")

    parser.add_argument("--quiet", default=False, action="store_true",
                        help="Do not ask any questions just to the default.")

    parser.add_argument("--kits_icp_dir", default=None, help="Directory of kits/ICP")

    deployment_types = [f"{choice}: {deployment_types}"
                        for choice, (_, deployment_types) in UPGRADE_TYPES.items()]
    parser.add_argument('deployment_type', choices=UPGRADE_TYPES.keys(),
                        help="What upgrade should be performed. ( {})"
                        .format(", \n".join(deployment_types)))

    args = parser.parse_args()
    client_e4_dir = args.client_e4_dir # The client e4 directory
    current_client_version = None # The current client version

    # Get the latest release directory, client, client_e4 and genie python versions.
    if args.release_dir is not None:
        current_release_dir = get_latest_release_directory_if_dir(args.release_dir)
        current_client_version = get_client_version(args.release_dir)
        # if the release suffix is not empty, then append it to the current release directory
        if args.release_suffix != "":
            current_release_dir += f"-{args.release_suffix}"
        server_dir = os.path.join(current_release_dir, "EPICS")
        client_dir = os.path.join(current_release_dir, "Client")
        client_e4_dir = client_dir
        genie_python3_dir = os.path.join(current_release_dir, "genie_python_3")

    # Else, if the ICP directory is specified, then use the latest release
    elif args.kits_icp_dir is not None:
        # If the deployment is equal to the latest release, set the epics build directory to the latest release
        if args.deployment_type == 'install_latest_incr':
            epics_build_dir = os.path.join(args.kits_icp_dir, "EPICS", args.server_build_prefix+"_win7_x64")  # pylint: disable=line-too-long
        else: # Else, set the epics build directory to the latest release.
            epics_build_dir = os.path.join(args.kits_icp_dir, "EPICS", args.server_build_prefix+"_CLEAN_win7_x64")  # pylint: disable=line-too-long

        # Try getting the latest release directory 
        try:
            server_dir = get_latest_directory_path(epics_build_dir, "BUILD-", "EPICS")

            client_build_dir = os.path.join(args.kits_icp_dir, "Client")
            client_dir = get_latest_directory_path(client_build_dir, "BUILD")

            client_e4_build_dir = os.path.join(args.kits_icp_dir, "Client_E4")
            client_e4_dir = get_latest_directory_path(client_e4_build_dir, "BUILD")

            genie_python3_build_dir = os.path.join(args.kits_icp_dir, "genie_python_3")
            genie_python3_dir = get_latest_directory_path(genie_python3_build_dir, "BUILD-")
        except IOError as error:
            print(error)
            sys.exit(3)

    # Elif the server directory, client, genie_python_3, and client_e4 directories are specified, then use them.
    elif args.server_dir is not None and args.client_dir is not None and \
        args.genie_python3_dir is not None and args.client_e4_dir is not None:
        server_dir = args.server_dir
        client_dir = args.client_dir
        client_e4_dir = args.client_e4_dir
        genie_python3_dir = args.genie_python3_dir
    else:
        print("You must specify either the release directory or kits_icp_dir or "
              "ALL of the server, client, client e4 and genie python 3 directories.")
        sys.exit(2)

    # Try to upgrade the client.
    try:
        prompt = UserPrompt(args.quiet, args.confirm_step)
        upgrade_instrument = UpgradeInstrument(
            prompt,
            server_dir,
            client_dir,
            client_e4_dir,
            genie_python3_dir,
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
