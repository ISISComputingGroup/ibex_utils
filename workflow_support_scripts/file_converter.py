import os
import argparse

from configs import FileTypes
from typing import Tuple

import convert_curve_files
import convert_temp_calib_files

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_arguments() -> Tuple[str, str]:
    """
    Get the input and output folders from the command line
    :return: input_folder, output_folder
    """
    parser = argparse.ArgumentParser(description='Get the input and output folder')
    parser.add_argument('-i', "--input", dest="input_folder", type=str, help='The input folder', required=True)
    parser.add_argument('-o', "--output", dest="output_folder", type=str, help='The output folder', required=True)
    parser.add_argument('-hl', "--header_lines", dest="num_of_header_lines", type=int, help='The number of header lines to strip', required=False, default=1)
    args = parser.parse_args()
    return os.path.join(dir_path, args.input_folder), os.path.join(dir_path, args.output_folder), args.num_of_header_lines


class FileConverter:
    """
    Convert RHFE sensor data into the correct format for ISIS
    """

    def __init__(self, input_dir: str, output_dir: str):
        """
        Initialise the class
        :param input_dir (str): The input directory
        :param output_dir (str): The output directory
        """
        self.input_dir = input_dir
        self.output_dir = output_dir

    def exit_if_input_dir_not_exist(self) -> None:
        """
        Check the input directory exists and exit if it does not
        :return None
        """
        if not self.check_dir_exists("input"):
            exit(f"Input folder {self.input_dir} does not exist")

    def check_dir_exists(self, input_output_dir) -> bool:
        """
        Get the input directory if it exists
        :return input_dir (str): The input directory
        """
        exists = False
        if input_output_dir == "input":
            if os.path.exists(self.input_dir):
                exists = True
        if input_output_dir == "output":
            if os.path.exists(self.output_dir):
                exists = True
        return exists

    @staticmethod
    def file_overwrite_check() -> bool:
        """
        Check if the output file exists and if it should be overwritten
        :return overwrite (bool): If the file should be overwritten
        """
        overwrite = False
        if input("This will overwrite the output folder, continue? Y/N ").lower()[0] == "y":
            overwrite = True
        return overwrite

    def set_up_output_dir(self) -> None:
        """
        Set up the output directory
        :return None
        """
        # Check if the path exists
        output_path_exists = self.check_dir_exists("output")
        if output_path_exists:
            # Check is overwrite is okay
            can_overwrite = self.file_overwrite_check()
            # If output path and overwrite is okay overwrite files in output path
            if can_overwrite:
                for root, _, files in os.walk(self.output_dir):
                    for output_file in files:
                        os.remove(os.path.join(root, output_file))
            # If output path exists but overwrite is not okay exit
            elif not can_overwrite:
                exit(
                    f"Output folder {self.output_dir} has not been"
                    f" overwritten and calibration files have not been converted."
                )
        # If output path does not exist create it
        elif not output_path_exists:
            print(f"Create directory {self.output_dir}")
            os.mkdir(self.output_dir)
        else:
            raise Exception("Unhandled case")

    @staticmethod
    def convert_file(root, original_file_name) -> None:
        """
        Convert RHFE sensor data into the correct format for ISIS
        :param original_file_name: The original file name
        :return None
        """
        # If the file is in .curve format
        if original_file_name.endswith(FileTypes.ORIGINAL_CURVE_FILE_EXTENSION):
            convert_curve_files.convert(original_file_name, output_folder, root)
        # If the file is in .dat format
        if original_file_name.endswith(FileTypes.ORIGINAL_DAT_FILE_EXTENSION):
            convert_temp_calib_files.convert(original_file_name, output_folder, root, num_of_header_lines)

    def convert_all_files(self) -> None:
        """
        Convert all files in the input directory
        :return None
        """
        for root, _, files in os.walk(self.input_dir):
            for original_file_name in files:
                self.convert_file(root, original_file_name)


if __name__ == "__main__":
    # Get the input and output folders from the command line
    input_folder, output_folder, num_of_header_lines = get_arguments()
    # Create Instance of FileConverter
    file_converter = FileConverter(input_folder, output_folder)
    # Check input folder exists
    file_converter.check_dir_exists("input")
    # Set up the output folder
    file_converter.set_up_output_dir()
    # Go through all folders in input_folder to find the file to convert
    file_converter.convert_all_files()
    print(
        "Finished converting, please check files and then copy and commit to the correct repo "
        "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Calibration-Files"
    )
