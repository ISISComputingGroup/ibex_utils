"""
Convert RHFE sensor data into the correct format for ISIS
"""

import os
from io import open
import argparse
from datetime import date
import json

dir_path = os.path.dirname(os.path.realpath(__file__))

ORIGINAL_FILE_EXTENSION = ".curve"
OUTPUT_FILE_EXTENSION = ".txt"
isis_calibration = {"ISIS calibration": {"sensor_type": "RhFe",
                                         "format_version": "1",
                                         "conversion_date": date.today(),
                                         "column1_name": "Temp",
                                         "column1_units": "K",
                                         "column2_name": "Measurement",
                                         "column2_units": "Ohms"}
                    }


def get_input_output_folders():
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

    # Go through all folders in input_folder to find curve file
    for root, _, files in os.walk(input_folder):
        # Find curve file in folder
        for original_file_name in files:
            if original_file_name.endswith(ORIGINAL_FILE_EXTENSION):
                print(f"Found curve file {original_file_name}")
                output_file_name = "{}{}".format(
                    original_file_name.strip(ORIGINAL_FILE_EXTENSION), OUTPUT_FILE_EXTENSION
                )
                with open(os.path.join(root, original_file_name), mode='r', encoding='utf-8') as original_file, \
                        open(os.path.join(output_folder, output_file_name), mode='w+', encoding='utf-8') as output_file:
                    # Iterate over header block dictionary
                    for header_title, header_block in isis_calibration.items():
                        output_file.write(f'# {header_title}\n' + '# {\n')
                        # Again iterate over the nested dictionary
                        for entry, calib_value in header_block.items():
                            output_file.write(f'#   "{entry}" : "{calib_value}"\n')
                    # Strip first 6 lines from file
                    for x in range(6):
                        next(original_file)
                    output_file.write("# }\n")
                    # Go through rest of lines and add correct format to output file
                    for original_line in original_file:
                        original_line = original_line
                        values = original_line.split()
                        # Swap temp/resistance columns to match the calibration file format
                        output_file.write(f"{values[1]},{values[0]}\n")

                # We've found the dat file so don't need to look at any others in the directory
                break
        else:
            print(f"Could not find {ORIGINAL_FILE_EXTENSION} file in {root}")

    print(
        "Finished converting, please check files and then copy and commit to the correct repo "
        "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Calibration-Files"
    )
