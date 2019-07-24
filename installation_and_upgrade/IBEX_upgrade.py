"""
Script to install IBEX to various machines
"""

import argparse
import os
import re
import sys

from ibex_install_utils.install_tasks import UpgradeInstrument
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
    parser = argparse.ArgumentParser(description='Upgrade the instrument.')

    parser.add_argument("--release_dir", dest="release_dir", default=None,
                        help="directory from which the client and server should be installed")
    parser.add_argument("--release_suffix", dest="release_suffix", default="",
                        help="Suffix for specifying non-standard releases "
                             "(such as those including hot fixes)")
    parser.add_argument("--server_build_prefix", default="EPICS", help="Prefix for build directory name")
    parser.add_argument("--server_dir", default=None, help="Directory from which IBEX server should be installed")
    parser.add_argument("--client_dir", default=None, help="Directory from which IBEX client should be installed")
    parser.add_argument("--client_e4_dir", default=None, help="Directory from which IBEX E4 client should be installed")
    parser.add_argument("--confirm_step", default=False, action="store_true",
                        help="Confirm each major action before performing it")
    parser.add_argument("--quiet", default=False, action="store_true",
                        help="Do not ask any questions just to the default.")
    parser.add_argument("--kits_icp_dir", default=None, help="Directory of kits/ICP")

    upgrade_types = ['training_update', 'instrument_install', 'instrument_test', 'instrument_deploy_pre_stop',
                     'instrument_deploy_main', 'instrument_deploy_post_start', 'install_latest_incr', 'install_latest',
                     'truncate_database', 'force_upgrade_mysql']
    parser.add_argument('deployment_type', choices=upgrade_types,
                        help="What upgrade should be performed. ("
                             "training_update: update a training machine', "
                             "install_latest_incr: install just the latest incremental build of the server, client and genie_python, "
                             "install_latest: install just the latest clean build of the server, client and genie_python, "
                             "instrument_install: full IBEX installation on a new instrument, "
                             "instrument_test: run through tests for IBEX client and server."
                             "instrument_deploy_pre_stop: instrument_deploy part before the stop of instrument,"
                             "instrument_deploy_main: instrument_deploy after stop but before starting it,"
                             "instrument_deploy_post_start: instrument_deploy part after the start of instrument,"
                             "truncate_database: backup and truncate the sql database on the instrument, "
                             "force_upgrade_mysql: upgrade mysql version to latest, ")

    args = parser.parse_args()
    client_e4_dir = args.client_e4_dir
    if args.release_dir is not None:
        current_release_dir = os.path.join(args.release_dir, _get_latest_release_path(args.release_dir))
        if args.release_suffix is not "":
            current_release_dir += "-{}".format(args.release_suffix)
        server_dir = os.path.join(current_release_dir, "EPICS")
        client_dir = os.path.join(current_release_dir, "Client")
    elif args.server_dir is not None and args.client_dir is not None:
        server_dir = args.server_dir
        client_dir = args.client_dir
    elif args.server_dir is not None or args.client_dir is not None:
        print("You must specify BOTH the server and client directories.")
        sys.exit(2)
    elif args.kits_icp_dir is not None:
        if args.deployment_type not in ['install_latest_incr','install_latest']:
            print("When specifying kits_icp_dir you choose the install latest deployment type.")
            sys.exit(2)
        if args.deployment_type == 'install_latest_incr':
            epics_build_dir = os.path.join(args.kits_icp_dir, "EPICS", args.server_build_prefix+"_win7_x64")
        else:
            epics_build_dir = os.path.join(args.kits_icp_dir, "EPICS", args.server_build_prefix+"_CLEAN_win7_x64")
        server_dir = _get_latest_directory_path(epics_build_dir, "BUILD-", "EPICS")

        client_build_dir = os.path.join(args.kits_icp_dir, "Client")
        client_dir = _get_latest_directory_path(client_build_dir, "BUILD")
        if client_e4_dir is None:
            client_build_dir = os.path.join(args.kits_icp_dir, "Client_E4")
            client_e4_dir = _get_latest_directory_path(client_build_dir, "BUILD")
    else:
        print("You must specify either the release directory or kits_icp_dir or "
              "BOTH the server and client directories.")
        sys.exit(2)

    prompt = UserPrompt(args.quiet, args.confirm_step)
    upgrade_instrument = UpgradeInstrument(prompt, server_dir, client_dir, client_e4_dir)

    try:
        if args.deployment_type == "training_update":
            upgrade_instrument.run_test_update()
        elif args.deployment_type in ['install_latest_incr', 'install_latest']:
            upgrade_instrument.remove_all_and_install_client_and_server()
        elif args.deployment_type == "instrument_install":
            upgrade_instrument.run_instrument_install()
        elif args.deployment_type == "instrument_deploy":
            upgrade_instrument.run_instrument_deploy()
        elif args.deployment_type == "instrument_deploy_pre_stop":
            upgrade_instrument.run_instrument_deploy_pre_stop()
        elif args.deployment_type == "instrument_deploy_main":
            upgrade_instrument.run_instrument_deploy_main()
        elif args.deployment_type == "instrument_deploy_post_start":
            upgrade_instrument.run_instrument_deploy_post_start()
        elif args.deployment_type == "instrument_test":
            upgrade_instrument.run_instrument_tests()
        elif args.deployment_type == "truncate_database":
            upgrade_instrument.run_truncate_database()
        elif args.deployment_type == "force_upgrade_mysql":
            upgrade_instrument.run_force_upgrade_mysql()

    except UserStop:
        print ("User stopped upgrade")
        sys.exit(2)
    except ErrorInTask as error_in_run_ex:
        print("Error in upgrade: {0}".format(error_in_run_ex.message))
        sys.exit(1)

    print ("Finished upgrade")
    sys.exit(0)
