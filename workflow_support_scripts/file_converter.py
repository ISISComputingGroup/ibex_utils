"""
Convert RHFE sensor data into the correct format for ISIS
"""

import os
import argparse
import convert_curve_files
import convert_temp_calib_files
from configs import FileTypes
from typing import Tuple

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_input_output_folders() -> Tuple[str, str]:
    """
    Get the input and output folders from the command line
    :return: input_folder, output_folder
    """
    parser = argparse.ArgumentParser(description='Get the input and output folder')
    parser.add_argument('-i', "--input", dest="input_folder", type=str, help='The input folder', required=True)
    parser.add_argument('-o', "--output", dest="output_folder", type=str, help='The output folder', required=True)
    args = parser.parse_args()
    return os.path.join(dir_path, args.input_folder), os.path.join(dir_path, args.output_folder)


if __name__ == "__main__":

    input_folder, output_folder = get_input_output_folders()

    # Check the input folder
    if not os.path.exists(input_folder):
        exit(f"Input folder {input_folder} does not exist")

    # Set up the output folder
    if os.path.exists(output_folder):
        if input("This will overwrite the output folder, continue? Y/N ").lower()[0] == "y":
            for root, _, files in os.walk(output_folder):
                for output_file in files:
                    os.remove(os.path.join(root, output_file))
        else:
            exit(
                f"Output folder {output_folder} has not been"
                f" overwritten and calibration files have not been converted."
            )
    else:
        print(f"Create directory {output_folder}")
        os.mkdir(output_folder)

    # Go through all folders in input_folder to find the file to convert
    for root, _, files in os.walk(input_folder):
        # Find the file in folder
        for original_file_name in files:
            # If the file is in .curve format
            if original_file_name.endswith(FileTypes.ORIGINAL_CURVE_FILE_EXTENSION):
                convert_curve_files.convert(original_file_name, output_folder, root)
            # If the file is in .dat format
            if original_file_name.endswith(FileTypes.ORIGINAL_DAT_FILE_EXTENSION):
                convert_temp_calib_files.convert(original_file_name, output_folder, root)
        # We've found the dat file so don't need to look at any others in the directory
        break
    else:
        print(f"Could not find the file to convert in {root}")

    print(
        "Finished converting, please check files and then copy and commit to the correct repo "
        "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Calibration-Files"
    )
