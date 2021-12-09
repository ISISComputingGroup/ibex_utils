"""
Convert RHFE sensor data into the correct format for ISIS
"""

import os
from io import open
from configs import FileTypes

dir_path = os.path.dirname(os.path.realpath(__file__))


def convert(original_file_name, output_folder, root):
    """ Converts .dat calibration files to .txt files and writes them to the output file """
    print(f"Found dat file {original_file_name}")
    output_file_name = "{}{}".format(
        original_file_name.strip(FileTypes.ORIGINAL_DAT_FILE_EXTENSION), FileTypes.OUTPUT_FILE_EXTENSION
    )
    with open(os.path.join(root, original_file_name), mode='r', encoding='utf-8') as original_file, \
            open(os.path.join(output_folder, output_file_name), mode='w+', encoding='utf-8') as output_file:
        # Strip first 3 lines from file
        for x in range(3):
            next(original_file)
        # Go through rest of lines and add correct format to output file
        for original_line in original_file:
            original_line = original_line
            values = original_line.split()
            output_file.write(f"{values[0]},{values[1]}\n")
