"""
Convert .curve files into the correct format for ISIS
"""

import os
from io import open

import utility
from configs import FileTypes, ISISCalibration

dir_path = os.path.dirname(os.path.realpath(__file__))


def convert(original_file_name, output_folder, root) -> None:
    """
    Converts .curve calibration files to .txt files, adds a header and writes them to the output file
    :param original_file_name (str): The name of the original file
    :param output_folder (str): The output folder
    :param root (str): The root name of the output file
    :return: None
    """
    output_file_name = utility.format_output_file_name(
        original_file_name, FileTypes.ORIGINAL_CURVE_FILE_EXTENSION, FileTypes.OUTPUT_FILE_EXTENSION
    )
    with open(
        os.path.join(root, original_file_name), mode="r", encoding="utf-8"
    ) as original_file, open(
        os.path.join(output_folder, output_file_name), mode="w+", encoding="utf-8"
    ) as output_file:
        generate_header(output_file)
        # Strip first 6 lines from file
        utility.strip_header(6, original_file)
        output_file.write("# }\n")
        # Go through rest of lines and add correct format to output file
        utility.format_output_file(original_file, output_file, 1, 0)


def generate_header(output_file) -> None:
    """
    Generate a header in ISIS Calibration File Format
    :param output_file (file): The output file
    :return: None
    """
    # Iterate over header block dictionary
    for header_title, header_block in ISISCalibration.isis_calibration_rhfe.items():
        output_file.write(f"# {header_title}\n" + "# {\n")
        # Again iterate over the nested dictionary
        for entry, calib_value in header_block.items():
            output_file.write(f'#   "{entry}" : "{calib_value}"\n')
