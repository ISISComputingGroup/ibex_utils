"""
Convert .dat files into the correct format for ISIS
"""

import os
from io import open

import utility
from configs import FileTypes

dir_path = os.path.dirname(os.path.realpath(__file__))


def convert(original_file_name, output_folder, root, num_of_header_lines=1):
    """
    Converts .dat calibration files to .txt files and writes them to the output file
    :param original_file_name (str): The name of the file to be converted
    :param output_folder (str): The output folder
    :param root (str): The root of the file name
    :return: None
    """
    output_file_name = utility.format_output_file_name(original_file_name, FileTypes.ORIGINAL_DAT_FILE_EXTENSION, FileTypes.OUTPUT_FILE_EXTENSION)
    with open(os.path.join(root, original_file_name), mode='r', encoding='utf-8') as original_file, \
            open(os.path.join(output_folder, output_file_name), mode='w+', encoding='utf-8') as output_file:
        # Strip first 3 lines from file
        utility.strip_header(num_of_header_lines, original_file)
        # Go through rest of lines and add correct format to output file
        utility.format_output_file(original_file, output_file, 0, 1)
