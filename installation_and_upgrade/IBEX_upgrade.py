"""
Script to install IBEX to various machines
"""

import argparse
import os
import re
import sys

from ibex_install_utils.install_tasks import UpgradeInstrument, UPGRADE_TYPES
from ibex_install_utils.exceptions import UserStop, ErrorInTask
from ibex_install_utils.user_prompt import UserPrompt


def _get_latest_directory_path(build_dir, build_prefix, directory_above_build_num=None, ):
    latest_build_path = os.path.join(build_dir, "LATEST_BUILD.txt")
    build_num = None
    for line in open(latest_build_path):
        build_num = line.strip()
    if build_num is None or build_num == "":
        print("Latest build num unknown. Cannot read it from '{0}'".format(latest_build_path))
        sys.exit(3)
    if directory_above_build_num is None:
        return os.path.join(build_dir, "{}{}".format(build_prefix, build_num))
    return os.path.join(build_dir, "{}{}".format(build_prefix, build_num), directory_above_build_num)


def _get_latest_release_path(release_dir):
    regex = re.compile(r'^\d\.\d\.\d$')

    releases = [name for name in os.listdir(release_dir) if os.path.isdir(os.path.join(release_dir, name))]
    releases = filter(regex.match, releases)

    if len(releases) == 0:
        print("Error: No releases found in '{0}'".format(release_dir))
        sys.exit(3)
    current_release = max(releases)
    return os.path.join(release_dir, "{}".format(current_release))


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
    parser.add_argument("--client_e4_dir", default=None, help="Directory from which IBEX E4 client should be installed")
    parser.add_argument("--genie_python3_dir", default=None,
                        help="Directory from which genie_python_3 should be installed")
    parser.add_argument("--script_generator_source_dir", default=None,
                        help="Directory from which script generator should be installed")
    parser.add_argument("--confirm_step", default=False, action="store_true",
                        help="Confirm each major action before performing it")
    parser.add_argument("--quiet", default=False, action="store_true",
                        help="Do not ask any questions just to the default.")
    parser.add_argument("--kits_icp_dir", default=None, help="Directory of kits/ICP")

    deployment_types = ["{}: {}".format(choice, deployment_types)
                        for choice, (_, deployment_types) in UPGRADE_TYPES.items()]
    parser.add_argument('deployment_type', choices=UPGRADE_TYPES.keys(),
                        help="What upgrade should be performed. ( {})".format(", \n".join(deployment_types)))

    args = parser.parse_args()
    client_e4_dir = args.client_e4_dir
    if args.release_dir is not None:
        current_release_dir = os.path.join(args.release_dir, _get_latest_release_path(args.release_dir))
        if args.release_suffix is not "":
            current_release_dir += "-{}".format(args.release_suffix)
        server_dir = os.path.join(current_release_dir, "EPICS")
        client_dir = os.path.join(current_release_dir, "Client")
        genie_python3_dir = os.path.join(current_release_dir, "genie_python_3")

        print("The script generator build is not yet in release so it gets the latest build!!")
        # Should be: script_generator_source_dir = os.path.join(current_release_dir, "script_generator")
        script_generator_build_dir = os.path.join(os.path.join(current_release_dir, os.pardir, os.pardir), "script_generator")
        script_generator_source_dir = _get_latest_directory_path(script_generator_build_dir, "BUILD")
    elif args.kits_icp_dir is not None:
        if args.deployment_type == 'install_latest_incr':
            epics_build_dir = os.path.join(args.kits_icp_dir, "EPICS", args.server_build_prefix+"_win7_x64")
        else:
            epics_build_dir = os.path.join(args.kits_icp_dir, "EPICS", args.server_build_prefix+"_CLEAN_win7_x64")
        server_dir = _get_latest_directory_path(epics_build_dir, "BUILD-", "EPICS")

        client_build_dir = os.path.join(args.kits_icp_dir, "Client")
        client_dir = _get_latest_directory_path(client_build_dir, "BUILD")

        client_e4_build_dir = os.path.join(args.kits_icp_dir, "Client_E4")
        client_e4_dir = _get_latest_directory_path(client_e4_build_dir, "BUILD")

        genie_python3_build_dir = os.path.join(args.kits_icp_dir, "genie_python_3")
        genie_python3_dir = _get_latest_directory_path(genie_python3_build_dir, "BUILD-")

        script_generator_build_dir = os.path.join(args.kits_icp_dir, "script_generator")
        script_generator_source_dir = _get_latest_directory_path(script_generator_build_dir, "BUILD")

    elif args.server_dir is not None and args.client_dir is not None and args.genie_python3_dir is not None and \
            args.client_e4_dir is not None and args.script_generator_source_dir is not None:
        server_dir = args.server_dir
        client_dir = args.client_dir
        client_e4_dir = args.client_e4_dir
        genie_python3_dir = args.genie_python3_dir
        script_generator_source_dir = args.script_generator_source_dir
    else:
        print("You must specify either the release directory or kits_icp_dir or "
              "ALL of the server, client, client e4, genie python 3 and script generator directories.")
        sys.exit(2)

    try:
        prompt = UserPrompt(args.quiet, args.confirm_step)
        upgrade_instrument = UpgradeInstrument(prompt, server_dir, client_dir, client_e4_dir, genie_python3_dir,
                                               script_generator_source_dir)
        upgrade_function = UPGRADE_TYPES[args.deployment_type][0]
        upgrade_function(upgrade_instrument)

    except UserStop:
        print("User stopped upgrade")
        sys.exit(2)
    except ErrorInTask as error_in_run_ex:
        print("Error in upgrade: {0}".format(error_in_run_ex.message))
        sys.exit(1)

    print("Finished upgrade")
    sys.exit(0)
