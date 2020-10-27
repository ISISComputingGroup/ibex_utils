"""
Convert RHFE sensor data into the correct format for ISIS
"""

import os
from io import open
import glob
import argparse

dir_path = os.path.dirname(os.path.realpath(__file__))

ORIGINAL_FILE_EXTENSION = ".dat"
OUTPUT_FILE_EXTENSION = ".txt"

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
        exit("Input folder {} does not exist".format(input_folder))

    # Set up the output folder
    if os.path.exists(output_folder):
        if input("This will overwrite the output folder, continue? Y/N").lower()[0] == "y":
            for root, _, files in os.walk(output_folder):
                for output_file in files:
                    os.remove(root+"\\"+output_file)
        else:
            exit("Output folder {} has not been overwritten and calibration files have not been converted.".format(output_folder))
    else:
        print("Create directory {}".format(output_folder))
        os.mkdir(output_folder)

    # Go through all folders in input_folder to find dat file
    for root, _, files in os.walk(input_folder):
        # Find dat file in folder
        for original_file_name in files:
            if original_file_name.endswith(ORIGINAL_FILE_EXTENSION):
                print("Found dat file {}".format(original_file_name))
                output_file_name = "{}{}".format(original_file_name.strip(ORIGINAL_FILE_EXTENSION),OUTPUT_FILE_EXTENSION)
                with open(root+"\\"+original_file_name, mode='r', encoding='utf-8') as original_file,\
                    open(output_folder+"\\"+output_file_name, mode='w+', encoding='utf-8') as output_file:
                    # Strip first 3 lines from file
                    for x in range(3):
                        next(original_file)
                    # Go through rest of lines and add correct format to output file
                    for original_line in original_file:
                        original_line = original_line
                        values = original_line.split()
                        output_file.write("{},{}\n".format(values[0], values[1]))
                # We've found the dat file so don't need to look at any others in the directory
                break
        else:
            print("Could not find {} file in {}".format(ORIGINAL_FILE_EXTENSION, root))
            

    print("Finished converting, please check files and then copy and commit to the correct repo https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Calibration-Files")
