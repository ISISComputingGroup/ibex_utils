"""
Utility functions to convert files to correct format for ISIS
"""


def strip_header(lines_to_strip, original_file) -> None:
    """
    Strip unnecessary header information from the original file
    :param lines_to_strip: Number of lines to strip, depends on the format of the original file
    :param original_file: The file to strip header from
    :return: None
    """
    for x in range(lines_to_strip):
        next(original_file)


def format_output_file(original_file, output_file, first_column, second_column) -> None:
    """
    Format the output file according to ISIS Calibration File Format
    :param original_file: The file to convert from
    :param output_file: The file to convert to
    :param first_column: The first column in the output_file
    :param second_column: The second column in the output_file
    :return: None
    """
    # Go through rest of lines and add correct format to output file
    for original_line in original_file:
        original_line = original_line
        values = original_line.split()
        # You may need to swap first and second column depending on the format of the original file
        output_file.write(f"{values[first_column]},{values[second_column]}\n")


def format_output_file_name(original_file_name, original_file_type, output_file_type):
    """
    Format the name of the output file
    :param original_file_name: The original file name
    :param original_file_type: The original file's type
    :param output_file_type: The output file's type
    :return: output_file_name
    """
    print(f"Found original file {original_file_name}")
    output_file_name = "{}{}".format(
        original_file_name.strip(original_file_type), output_file_type
    )
    return output_file_name
