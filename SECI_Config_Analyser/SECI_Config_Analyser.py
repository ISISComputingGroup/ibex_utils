"""
Script to analyse SECI configurations and components and output results to file
"""

import argparse
from os import system

from Directory_Operations import ReadConfigFiles

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyse the SECI configuration files of specified instrument and output results to file"
    )

    parser.add_argument(
        "--instrument", "-i", type=str, default=None, help="instrument to be analysed"
    )

    parser.add_argument(
        "--output_file", "-o", type=str, default=None, help="file to write the results to"
    )

    parser.add_argument(
        "--adminaccount",
        "-a",
        type=str,
        default=None,
        help=r"admin account name (without host i.e. NOT \\NDXxxx\xxx, just xxx",
    )

    parser.add_argument(
        "--adminpassword", "-p", type=str, default=None, help="admin account password"
    )

    args = parser.parse_args()

    if args.instrument is None:
        parser.print_help()

    if args.output_file is None:
        args.output_file = f"{args.instrument.upper()}_-_VIs_from_SECI_configs.txt"

    # open reference to appropriate network drive with supplied credentials

    print("Connecting to remote directory...")
    system(
        f"net use \\\\ndx{args.instrument}\\c$ /user:ndx{args.instrument}\\{args.adminaccount} {args.adminpassword}"
    )

    # create instance of 'ReadConfigFiles' as 'filelist' and supply directory to be read

    print("Reading configuration files...")
    filelist = ReadConfigFiles(
        f"//ndx{args.instrument}/c$/Program Files (x86)/STFC ISIS Facility/SECI/Configurations/"
    )

    print("Analysing files...")
    xml_data = filelist.analyse_config_files()

    # delete reference to network drive

    print("Removing network connection...")
    system(f"net use \\\\ndx{args.instrument}\\c$ /delete")

    # concatenate each element in list with newline character, then print whole string

    print("Writing output file...")
    with open(args.output_file, "w") as outputfile:
        outputfile.write(f"SECI configuration analysis for {args.instrument.upper()}:\n\n")

        for item in xml_data:
            outputfile.write("\n".join(x for x in item))
            outputfile.write(f"\nNumber of VIs in configuration/component: {str(len(item))}\n\n")
