"""
Convert .dat files into the correct format for ISIS
"""

import os

from io import open
from configs import FileTypes

import utility

dir_path = os.path.dirname(os.path.realpath(__file__))


def convert(original_file_name, output_folder, root):
    """
    Converts .dat calibration files to .txt files and writes them to the output file
    :param original_file_name: The original file name
    :param output_folder: The output foldr
    :param root: The root directory of the file
    :return: None
    """
    output_file_name = utility.format_output_file_name(original_file_name, FileTypes.ORIGINAL_DAT_FILE_EXTENSION, FileTypes.OUTPUT_FILE_EXTENSION)
    with open(os.path.join(root, original_file_name), mode='r', encoding='utf-8') as original_file, \
            open(os.path.join(output_folder, output_file_name), mode='w+', encoding='utf-8') as output_file:
        # Strip first 3 lines from file
        utility.strip_header(3, original_file)
        # Go through rest of lines and add correct format to output file
        utility.format_output_file(original_file, output_file, 0, 1)
