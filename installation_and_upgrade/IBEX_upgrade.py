"""
Script to install IBEX to various machines
"""
# pylint: disable=import-error
import argparse
from ast import arguments
import os
import re
import sys
from typing import Tuple
import semantic_version

from ibex_install_utils.Arguments_config import ARGUMENT_PARSER, ARGUMENTS
from ibex_install_utils.install_tasks import UpgradeInstrument, UPGRADE_TYPES
from ibex_install_utils.exceptions import UserStop, ErrorInTask
from ibex_install_utils.user_prompt import UserPrompt
from ibex_install_utils.file_utils import get_latest_directory_path


def _get_latest_release_path(release_dir) -> str:
    """
    Get the latest release path
    Args:
        release_dir: directory to search for releases
    Returns:
        latest_release_path
    """
    regex = re.compile(r'^\d+\.\d+\.\d+$')

    release_path = os.listdir(release_dir)
    releases = [name for name in release_path if os.path.isdir(os.path.join(release_dir, name))]
    releases = list(filter(regex.match, releases))
    releases = sorted(list(filter(regex.match, releases)), key=semantic_version.Version)

    if len(releases) == 0:
        print(f"Error: No releases found in '{release_dir}'")
        sys.exit(3)
    current_release = releases[-1]
    return os.path.join(release_dir, f"{current_release}")

def add_deployment_type_to_parser(argument_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:  # pylint: disable=line-too-long
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

def add_arguments_to_parser_from_arguments(argument_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:  # pylint: disable=line-too-long
    """
    Add arguments to the argument parser
    Args:
        argument_parser: argument parser to add arguments to
    Returns:
        argument_parser
    """
    for argument in ARGUMENTS:
        flag_argument = argument.pop("name_or_flags")
        argument_parser.add_argument(flag_argument, **argument)

    return argument_parser

def check_directory_selected(args_server_dir: str, args_client_dir: str, args_genie_python3_dir: str, args_client_e4_dir: str) -> bool:
    argument_checklist = [args_server_dir,
        args_client_dir,
        args_genie_python3_dir,
        args_client_e4_dir]

    all_directories_populated = all(argument_checklist)
    return all_directories_populated

def set_args_to_latest(current_release_directory: str) -> Tuple[str, str, str, str, str, str]:
    """
    Set the arguments to the latest release
    Args:
        current_release_directory: current release directory
    Returns:
        server_directory, client_directory, client_e4_directory, genie_python3_directory
    """
    server_directory = os.path.join(current_release_directory, "EPICS")
    client_directory = os.path.join(current_release_directory, "Client")
    client_e4_directory = client_directory
    genie_python3_directory = os.path.join(current_release_directory, "genie_python_3")

    return server_directory, client_directory, client_e4_directory, genie_python3_directory

def set_release_directory_to_latest(arguments: argparse.Namespace) -> Tuple[str, str, str, str, str]:  # pylint: disable=line-too-long
    """
    Set the release directory to the latest release
    Args:
        release_dir: directory to search for releases
    Returns:
        (release_directory, client_version, server_directory, client_directory, 
        client_e4_directory, genie_python3_directory)
    """
    release_directory = os.path.join(arguments.release_dir,
        _get_latest_release_path(args.release_dir))
    client_version = _get_latest_release_path(arguments.release_dir).split("\\")[-1]

    if arguments.release_suffix != "":
        release_directory += f"-{arguments.release_suffix}"

    arg_dirs = set_args_to_latest(release_directory)
    server_directory, client_directory, client_e4_directory, genie_python3_directory = arg_dirs

    return (client_version, 
        server_directory,
        client_directory,
        client_e4_directory,
        genie_python3_directory)

def set_epics_build_dir_using_kits_icp(arguments: argparse.Namespace) -> str:
    """
    Set the epics build directory to the kits ICP directory
    Args:
        arguments: arguments
    Returns:
        epics_build_directory
    """
    if arguments.deployment_type == 'install_latest_incr':
        epics_build_directory = os.path.join(arguments.kits_icp_dir,
            "EPICS", arguments.server_build_prefix+"_win7_x64")
    else:
        epics_build_directory = os.path.join(arguments.kits_icp_dir,
            "EPICS",
            arguments.server_build_prefix+"_CLEAN_win7_x64")
    return epics_build_directory

def set_directory_using_kits_icp(arguments: argparse.Namespace, directory_name: str, directory_type: str, icp: bool, build_directory=None) -> str:  # pylint: disable=line-too-long
    """
    Set the directory to the kits ICP directory to latest release
    Args:
        arguments: arguments
        directory_name: directory name
        directory_type: directory type
        icp: kits ICP directory
        build_directory: build directory
    Returns:
        directory
    """
    if icp:
        build_directory =  os.path.join(arguments.kits_icp_dir, f"{directory_name}")
        lastest_directory_path = get_latest_directory_path(build_directory, f"{directory_type}")
        return build_directory, lastest_directory_path

    if build_directory:
        lastest_directory_path = get_latest_directory_path(epics_build_dir,
            f"{directory_name}",
            f"{directory_type}")
        return lastest_directory_path
    return None

if __name__ == "__main__":
    # A parser to parse the command line arguments
    parser = argparse.ArgumentParser(**ARGUMENT_PARSER)
    parser = add_arguments_to_parser_from_arguments(parser) # Add Arguments
    parser = add_deployment_type_to_parser(parser) # Add deployment type from UPGRADE_TYPES

    args = parser.parse_args()
    client_e4_dir = args.client_e4_dir
    current_client_version = None  # pylint: disable=invalid-name
    # If the release directory is not specified, use the latest release
    if args.release_dir is not None:
        rel_dir = set_release_directory_to_latest(args) # Set release directories to latest release
        current_client_version, server_dir, client_dir, client_e4_dir, genie_python3_dir = rel_dir

    elif args.kits_icp_dir is not None:
        # If kits_icp_dir is specified, epics_build_dir is set
        epics_build_dir = set_epics_build_dir_using_kits_icp(args)
        # Try initialising the server and client directories to latest release using kits_icp_dir
        try:
            server_dir = set_directory_using_kits_icp(args,
                "BUILD-",
                "EPICS",
                True,
                epics_build_dir)

            client_build_dir, client_dir = set_directory_using_kits_icp(args,
                "Client",
                "BUILD",
                False)

            client_e4_build_dir, client_e4_dir = set_directory_using_kits_icp(args,
                "Client_E4",
                "BUILD",
                False)

            genie_python3_build_dir, genie_python3_dir = set_directory_using_kits_icp(args,
                "genie_python_3",
                "BUILD-",
                False)

        except IOError as error:
            print(error)
            sys.exit(3)

    # Instantiate All server, client and genie_python3 directory paths if present

    elif check_directory_selected(args.server_dir, args.client_dir, args.genie_python3_dir,\
        args.client_e4_dir) is True:

        server_dir = args.server_dir
        client_dir = args.client_dir
        client_e4_dir = args.client_e4_dir
        genie_python3_dir = args.genie_python3_dir
       
    else:
        print("You must specify either the release directory or kits_icp_dir or "
              "ALL of the server, client, client e4 and genie python 3 directories.")
        sys.exit(2)
    try:
        prompt = UserPrompt(args.quiet, args.confirm_step)
        upgrade_instrument = UpgradeInstrument(prompt,
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
