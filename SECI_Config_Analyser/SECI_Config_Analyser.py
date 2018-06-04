"""
Script to analyse SECI configurations and components and output results to file
"""

from Directory_Operations import ReadConfigFiles
import argparse
from os import system

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Analyse the SECI configuration files of specified instrument and output results to file')

    parser.add_argument('--instrument', '-i',
                        type=str,
                        default=None,
                        help='instrument to be analysed')

    parser.add_argument('--output_file', '-o',
                        type=str,
                        default=None,
                        help='file to write the results to')

    parser.add_argument('--adminaccount', '-a',
                        type=str,
                        default=None,
                        help='admin account name')

    parser.add_argument('--adminpassword', '-p',
                        type=str,
                        default=None,
                        help='admin account password')

    args = parser.parse_args()

    if args.instrument is None:
        parser.print_help()

    if args.output_file is None:
        args.output_file = '{}_-_VIs_from_SECI_configs.txt'.format(args.instrument.upper())

    # open reference to appropriate network drive with supplied credentials

    system("net use \\\\ndx{}\c$ {} /user:ndx{}\\{}".format(args.instrument,args.adminpassword,args.instrument,args.adminaccount))

    # create instance of 'ReadConfigFiles' as 'filelist' and supply directory to be read

    filelist = ReadConfigFiles("//ndx{}/c$/Program Files (x86)/STFC ISIS Facility/SECI/Configurations/".format(args.instrument))

    # delete reference to network drive

    system("net use \\\\ndx{}\c$ /delete".format(args.instrument))

    xml_data = filelist.analyse_config_files()

    # concatenate each element in list with newline character, then print whole string

    with open(args.output_file, 'w') as outputfile:

        outputfile.write("SECI configuration analysis for {}:\n".format(args.instrument.upper()))

        for item in xml_data:

            outputfile.write('\n'.join(x for x in item))
            outputfile.write("\nNumber of VIs: {}\n".format(str(len(item))))
