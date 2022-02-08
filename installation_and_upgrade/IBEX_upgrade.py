"""
Script to install IBEX to various machines
"""
# pylint: disable=import-error
import argparse
import os
import re
import sys
from tkinter import Y
from typing import Tuple
import semantic_version

from ibex_install_utils.Arguments_config import ARGUMENT_PARSER, ARGUMENTS
from ibex_install_utils.install_tasks import UpgradeInstrument, UPGRADE_TYPES
from ibex_install_utils.exceptions import UserStop, ErrorInTask
from ibex_install_utils.user_prompt import UserPrompt
from ibex_install_utils.file_utils import get_latest_directory_path


def _get_latest_release_path(release_dir) -> str:
    regex = re.compile(r'^\d+\.\d+\.\d+$')

    releases = [name for name in os.listdir(release_dir) if os.path.isdir(os.path.join(release_dir, name))]
    releases = list(filter(regex.match, releases))
    releases = sorted(list(filter(regex.match, releases)), key=semantic_version.Version)

    if len(releases) == 0:
        print(f"Error: No releases found in '{release_dir}'")
        sys.exit(3)
    current_release = releases[-1]
    return os.path.join(release_dir, f"{current_release}")

def add_deployment_type_to_parser(argument_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Add deployment type to the argument parser
    Args:
        argument_parser: argument parser to add arguments to
    Returns:
        argument_parser
    """
    deployment_types = [f"{choice}: {deployment_types}"
                        for choice, (_, deployment_types) in UPGRADE_TYPES.items()]
    argument_parser.add_argument('deployment_type', 
    choices=UPGRADE_TYPES.keys(),
    help="What upgrade should be performed. ( {})".format(", \n".join(deployment_types)))

    return argument_parser

def add_arguments_to_parser_from_ARGUMENTS(argument_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Add arguments to the argument parser
    Args:
        argument_parser: argument parser to add arguments to
    """
    for argument in ARGUMENTS:
        argument_parser.add_argument(**argument)

    return argument_parser

def instantiate_arguments_from_list(args_server_dir: str, args_client_dir: str, args_genie_python3_dir: str, args_client_e4_dir: str) -> Tuple[str, str, str, str]:
    """
    Instantiate arguments from a list
    Args:
        args_list: list of arguments
    Returns:
        args_server_dir, args_client_dir, args_genie_python3_dir, args_client_e4_dir
    """
    argument_checklist = [args_server_dir, args_client_dir, args_genie_python3_dir, args_client_e4_dir]
    if all(argument_checklist):
        return args_server_dir, args_client_dir, args_genie_python3_dir, args_client_e4_dir
    else:
        print("You must specify either the release directory or kits_icp_dir or "
              "ALL of the server, client, client e4 and genie python 3 directories.")
        sys.exit(2)

def set_release_directory_to_latest(args: argparse.Namespace) -> Tuple[str, str, str, str]:
    """
    Set the release directory to the latest release
    Args:
        release_dir: directory to search for releases
    Returns:
        (current_release_dir, current_client_version, server_dir, client_dir, client_e4_dir, genie_python3_dir)
    """
    current_release_dir = os.path.join(args.release_dir, _get_latest_release_path(args.release_dir))
    current_client_version = _get_latest_release_path(args.release_dir).split("\\")[-1]
    if args.release_suffix != "":
        current_release_dir += f"-{args.release_suffix}"
    server_dir = os.path.join(current_release_dir, "EPICS")
    client_dir = os.path.join(current_release_dir, "Client")
    client_e4_dir = client_dir
    genie_python3_dir = os.path.join(current_release_dir, "genie_python_3")
    return (current_release_dir, current_client_version, server_dir, client_dir, client_e4_dir, genie_python3_dir)

def set_args_to_latest(current_release_dir: str) -> Tuple[str, str, str, str, str, str]:
    """
    Set the arguments to the latest release
    Args:
        current_release_dir: current release directory
    Returns:
        server_dir, client_dir, client_e4_dir, genie_python3_dir
    """
    server_dir = os.path.join(current_release_dir, "EPICS")
    client_dir = os.path.join(current_release_dir, "Client")
    client_e4_dir = client_dir
    genie_python3_dir = os.path.join(current_release_dir, "genie_python_3")

    return server_dir, client_dir, client_e4_dir, genie_python3_dir

def set_epics_build_dir_using_kits_ICP(args: argparse.Namespace) -> str:
    """
    Set the epics build directory to the kits ICP directory
    Args:
        kits_icp_dir: kits ICP directory
    """
    if args.deployment_type == 'install_latest_incr':
        epics_build_dir = os.path.join(args.kits_icp_dir, "EPICS", args.server_build_prefix+"_win7_x64")
    else:
        epics_build_dir = os.path.join(args.kits_icp_dir, "EPICS", args.server_build_prefix+"_CLEAN_win7_x64")
    return epics_build_dir

def set_directory_using_kits_icp(args: argparse.Namespace, directory_name: str, directory_type: str, ICP: bool, build_directory=None) -> str:
    """
    Set the directory to the kits ICP directory to latest release
    Args:
        directory_name: directory name
        directory_type: directory type
        ICP: kits ICP directory
        build_directory: build directory
    Returns:
        directory
    """
    if ICP:
        build_directory =  os.path.join(args.kits_icp_dir, f"{directory_name}")
        lastest_directory_path = get_latest_directory_path(build_directory, f"{directory_type}")
        return build_directory, lastest_directory_path
    else:
        if build_directory:
            lastest_directory_path = get_latest_directory_path(epics_build_dir, f"{directory_name}", f"{directory_type}")
            return lastest_directory_path
        else:
            return None

if __name__ == "__main__":
    # A parser to parse the command line arguments
    parser = argparse.ArgumentParser(**ARGUMENT_PARSER)
    parser = add_arguments_to_parser_from_ARGUMENTS(parser) # Add Arguments
    parser = add_deployment_type_to_parser(parser) # Add deployment type from UPGRADE_TYPES

    args = parser.parse_args()
    client_e4_dir = args.client_e4_dir
    current_client_version = None
    # If the release directory is not specified, use the latest release
    if args.release_dir is not None:
        current_release_dir, current_client_version = set_release_directory_to_latest(args)
        if args.release_suffix != "":
            current_release_dir += f"-{args.release_suffix}"
        server_dir, client_dir, client_e4_dir, genie_python3_dir = set_args_to_latest(current_release_dir)

    elif args.kits_icp_dir is not None:
        # If kits_icp_dir is specified, epics_build_dir is set
        epics_build_dir = set_epics_build_dir_using_kits_ICP(args)
        # Try initialising the server and client directories to latest release using kits_icp_dir
        try:
            server_dir = set_directory_using_kits_icp(args, "BUILD-", "EPICS", True, epics_build_dir)
            client_build_dir, client_dir = set_directory_using_kits_icp(args, "Client", "BUILD")
            client_e4_build_dir, client_e4_dir = set_directory_using_kits_icp(args, "Client_E4", "BUILD")
            genie_python3_build_dir, genie_python3_dir = set_directory_using_kits_icp(args, "genie_python_3", "BUILD-")
        except IOError as e:
            print(e)
            sys.exit(3)

    # Instantiate All server, client and genie_python3 directory paths if present
    server_dir, client_dir, genie_python3_dir, client_e4_dir = instantiate_arguments_from_list(
        args.server_dir, 
        args.client_dir, 
        args.genie_python3_dir, 
        args.client_e4_dir)
    try:
        prompt = UserPrompt(args.quiet, args.confirm_step)
        upgrade_instrument = UpgradeInstrument(prompt, server_dir, client_dir, client_e4_dir, genie_python3_dir,
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