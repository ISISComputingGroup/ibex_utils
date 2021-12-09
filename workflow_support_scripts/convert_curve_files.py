"""
Convert RHFE sensor data into the correct format for ISIS
"""

import os
from io import open
from configs import FileTypes, ISISCalibration

dir_path = os.path.dirname(os.path.realpath(__file__))


def convert(original_file_name, output_folder, root):
    """ Converts .curve calibration files to .txt files, adds a header and writes them to the output file """
    print(f"Found curve file {original_file_name}")
    output_file_name = "{}{}".format(
        original_file_name.strip(FileTypes.ORIGINAL_CURVE_FILE_EXTENSION), FileTypes.OUTPUT_FILE_EXTENSION
    )
    with open(os.path.join(root, original_file_name), mode='r', encoding='utf-8') as original_file, \
            open(os.path.join(output_folder, output_file_name), mode='w+', encoding='utf-8') as output_file:
        # Iterate over header block dictionary
        for header_title, header_block in ISISCalibration.isis_calibration_rhfe.items():
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
