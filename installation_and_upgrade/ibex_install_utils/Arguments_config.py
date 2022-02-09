"""
Arguments for IBEX_upgrade.py
"""

import argparse

ARGUMENT_PARSER = {
    "description": "Upgrade the instrument.",
    "formatter_class": argparse.RawTextHelpFormatter
}

ARGUMENTS = [
    {
        "name_or_flags": "--release_dir",
        "dest": "release_dir",
        "default": None,
        "help": "directory from which the client and server should be installed"
    },
    {
        "name_or_flags": "--release_suffix",
        "dest": "release_suffix",
        "default": "",
        "help": "Suffix for specifying non-standard releases (such as those including hot fixes)"
    },
    {
        "name_or_flags": "--server_build_prefix",
        "default": "EPICS",
        "help": "Prefix for build directory name"
    },
    {
        "name_or_flags": "--server_dir",
        "default": None,
        "help": "Directory from which IBEX server should be installed"
    },
    {
        "name_or_flags": "--client_dir",
        "default": None,
        "help": "Directory from which IBEX client should be installed"
    },
    {
        "name_or_flags": "--client_e4_dir",
        "default": None,
        "help": "Directory from which IBEX E4 client should be installed"
    },
    {
        "name_or_flags": "--genie_python3_dir",
        "default": None,
        "help": "Directory from which genie_python_3 should be installed"
    },
    {
        "name_or_flags": "--confirm_step",
        "default": False,
        "action": "store_true",
        "help": "Confirm each major action before performing it"
    },
    {
        "name_or_flags": "--quiet",
        "default": False,
        "action": "store_true",
        "help": "Do not ask any questions just to the default."
    },
    {
        "name_or_flags": "--kits_icp_dir",
        "default": None,
        "help": "Directory of kits/ICP"
    }
]