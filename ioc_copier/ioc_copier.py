"""
Script to handle duplicating IOCs
"""

import os
import re
import sys
from shutil import copytree, ignore_patterns

global START_COPY
global current_copy
global padded_start_copy
global padded_current_copy
global asub_record


def rename_files(root_folder, rename, ioc):
    """
    Function to handle renaming of files.
    Parameters:
        root_folder - The root folder path for use in os.path.join.
        rename - the path of the file or folder to rename.
        padded_start_copy - the padded starting number, e.g. 01, 11 etc.
        padded_current_copy - the padded version of the current ioc number.
    """
    if f"IOC_{padded_start_copy}" in rename:
        os.rename(
            os.path.join(root_folder, rename),
            os.path.join(
                root_folder,
                rename.replace(f"IOC_{padded_start_copy}", f"IOC_{padded_current_copy}"),
            ),
        )
    if f"IOC-{padded_start_copy}" in rename:
        os.rename(
            os.path.join(root_folder, rename),
            os.path.join(
                root_folder,
                rename.replace(f"IOC-{padded_start_copy}", f"IOC-{padded_current_copy}"),
            ),
        )
    if f"{ioc}_{padded_start_copy}" in rename:
        os.rename(
            os.path.join(root_folder, rename),
            os.path.join(
                root_folder,
                rename.replace(f"{ioc}_{padded_start_copy}", f"{ioc}_{padded_current_copy}"),
            ),
        )


def replace_text(text_lines, ioc, skip=None):
    """
    Function to handle replacing of text within files.
    Parameters:
        text_lines - the text from the file to process.
        start - the value to look for to remove.
        current - the value to replace start with.
    return:
        The new text to be placed in the file.
    """
    if skip is None:
        skip = []
    return [
        replace_line(ioc, line) if index not in skip else line
        for index, line in enumerate(text_lines)
    ]


def replace_line(ioc, line):
    """
    Function to replace a single line in a file.
    param ioc: The name of the ioc.
    param line: The line of text to replace.
    return:
        Tne new line of text.
    """
    global asub_record
    if "record(aSub" in line and not asub_record:
        print(
            "DB contains aSubRecord, this has been duplicated, but may need a more thorough check."
        )
        asub_record = True
    temp_text = re.sub(f"IOC_{START_COPY}", f"IOC_{current_copy}", line)
    line = temp_text
    temp_text = re.sub(f"IOC-{START_COPY}", f"IOC-{current_copy}", line)
    line = temp_text
    temp_text = re.sub(f"{ioc}_{START_COPY}", f"{ioc}_{current_copy}", line)
    line = temp_text
    temp_text = re.sub(f"RAMPFILELIST{START_COPY}", f"RAMPFILELIST{current_copy}", line)
    line = temp_text
    temp_text = re.sub(f"IOC_0{START_COPY}", f"IOC_{padded_current_copy}", line)
    line = temp_text
    temp_text = re.sub(f"IOC-0{START_COPY}", f"IOC-{padded_current_copy}", line)
    line = temp_text
    temp_text = re.sub(f"{ioc}_0{START_COPY}", f"{ioc}_{padded_current_copy}", line)
    line = temp_text
    temp_text = re.sub(f"RAMPFILELIST0{START_COPY}", f"RAMPFILELIST{padded_current_copy}", line)
    line = temp_text
    return line


def help_check():
    """
    Function to handle printing help.
    """
    if "-h" in sys.argv:
        print("First Argument: <ioc-to-duplicate>")
        print(
            "This should be the name of the ioc folder, the folders to "
            "actual duplicate will all contain this in their names.\n"
        )
        print("Second Argument: <number-ioc-to-copy")
        print(
            "This should be the last currently existing ioc number, "
            "e.g. 2. If copying IOC-01 please test extremely thoroughly as there may be edge cases the script"
            "cannot account for.\n"
        )
        print("Third Argument: <first-copy>")
        print(
            "This should be the number of the first copy, i.e."
            " the first IOC made will be IOC-<first-copy>.\n"
        )
        print("Fourth Argument: <max-number-ioc>")
        print("This should be the maximum number copied to.\n")
        print("Make sure to run this file from an epics terminal so that make clean can run.\n")
        sys.exit()


def handle_arguments():
    """
    Function to handle arguments of ioc_copier.py.
    Returns:
        ioc - The name of the ioc to run, folders to copy will be of the form,
              <ioc>-IOC-01App and ioc<ioc>-IOC-01.
        start_copy - The folder to copy (avoid IOC1 as other IOCs usually reference
                     this rather than copying it directly).
        initial_copy - The first copy.
        max_copy - The final copy.
    """
    if len(sys.argv) < 5:
        print("Not enough arguments")
        print(
            "Arguments should be <ioc-to-duplicate> <number-ioc-to-copy> "
            "<first-copy> <max-number-ioc>"
        )
        print('use argument "-h" for more details.')
        sys.exit()
    elif len(sys.argv) > 5:
        print("Too many arguments")
        print(
            "Arguments should be <ioc-to-duplicate> <number-ioc-to-copy> "
            "<first-copy> <max-number-ioc>"
        )
        print('use argument "-h" for more details.')
        sys.exit()
    else:
        ioc = sys.argv[1]
        global START_COPY
        START_COPY = int(sys.argv[2])
        initial_copy = int(sys.argv[3])
        max_copy = int(sys.argv[4])
    return initial_copy, ioc, max_copy


def copy_folder(file_format, ioc_name):
    """
    Function to handle copying folder before replacing text and names.
    Parameters:
        file_format - The format to use for the folder name, either ending in app
                      or starting with ioc. in the form of an fstring.
        ioc_name - name of the ioc.
    Returns:
        The path of the new folder.
    """
    start_path = file_format.format(f"{ioc_name}-{padded_start_copy}")
    path = os.path.join(os.getcwd(), file_format.format(f"{ioc_name}-{padded_current_copy}"))
    try:
        copytree(
            os.path.join(os.getcwd(), start_path),
            os.path.join(path),
            ignore=ignore_patterns("st-*.cmd", "build.mak", "*.db", "*.substitutions", "*.req"),
        )
    except FileExistsError:
        raise FileExistsError(
            f"Copy {padded_current_copy} already exists, please ensure that the initial copy "
            f"argument is greater than the highest number IOC."
        ) from None
    return path


def generate_config(ioc):
    """
    Generate the config if copying ioc 01 as it should just reference ioc 01s config rather than duplicating it.
    :param ioc: the ioc name
    :return: the text lines of the config.
    """
    return [
        '<?xml version="1.0" ?>\n',
        '<ioc_config xmlns="http://epics.isis.rl.ac.uk/schema/ioc_config/1.0" ',
        'xmlns:xi="http://www.w3.org/2001/XInclude">\n',
        f'<xi:include href="../ioc{ioc}-IOC-01/config.xml"  />\n',
        "\n",
        "</ioc_config>",
    ]


def remove_db_plus(text):
    """
    delete DB += lines from a makefile
    :param text: the line to check whether to comment
    :return: the line to delete if it is a DB+= line
    """
    text = [line for line in text if not re.match(r"(DB \+= )(?=.*\.db)", line)]
    return text


def get_file_text(file, ioc, root):
    """
    function to get the text to write to a file.
    :param file: The file to get the initial text from.
    :param ioc: The Ioc name.
    :param root: The root folder.
    :return:
        The text from the file, with the IOC number updated to the current copy.
    """
    path = os.path.join(root, file)
    with open(path, "r") as file_pointer:
        text = file_pointer.readlines()
    skip = []
    if START_COPY == 1:
        if file == "st.cmd":
            skip = [
                x for x, val in enumerate(text) if f"< iocBoot/ioc{ioc}-IOC-01/st-common.cmd" in val
            ]
        elif file == "config.xml":
            return generate_config(ioc)
        elif path.endswith(r"App\Db\Makefile"):
            text = remove_db_plus(text)

    # Last one handled on starts other than 1 to avoid breaking commenting.
    if path.endswith(r"App\src\Makefile"):
        skip = [x for x, val in enumerate(text) if "build.mak " in val or "/src/build.mak" in val]
    text = replace_text(text, ioc, skip)
    return text


def write_file_text(file, root, text):
    """
    function to write to a file.
    :param file: The file to write to.
    :param root: The root folder.
    :param text: The text to write to the file.
    """
    with open(os.path.join(root, file), "w") as file_pointer:
        file_pointer.seek(0)
        file_pointer.writelines(text)
        file_pointer.truncate()


def file_walk(files, ioc, root):
    """
    Function to walk through each file retrieved by os.walk and call necessary functions.
    :param files: The list of files to walk through.
    :param ioc: The ioc name.
    :param root: The root folder.
    :return:
    """
    for file in files:
        if "exe" not in file and "obj" not in file and "pdb" not in file:
            text = get_file_text(file, ioc, root)
            write_file_text(file, root, text)
            rename_files(root, file, ioc)


def folder_walk(ioc, root, sub_folder):
    """
    Function to walk through folders and rename them.
    :param ioc: The ioc name.
    :param root:
    :param sub_folder:
    :return:
    """
    for folder in sub_folder:
        rename_files(root, folder, ioc)


def copy_loop(initial_copy, max_copy, file_format, ioc):
    """
    Main loop to handle copy and renaming of files
    Parameters:
        start_copy - The folder to copy (avoid IOC1 as other IOCs usually
                     reference this rather than copying it directly).
        initial_copy - The first copy.
        max_copy - The final copy.
        file_format - The format to use for the folder name, either ending
                      in app or starting with ioc. in the form of an fstring.
        ioc_name - The name of the ioc to run, folders to copy will be of the form,
                   <ioc>-IOC-01App and ioc<ioc>-IOC-01.
    """
    ioc_name = f"{ioc}-IOC"
    global current_copy
    global padded_start_copy
    global padded_current_copy
    for current_copy in range(initial_copy, max_copy + 1):
        padded_start_copy = add_zero_padding(START_COPY)
        padded_current_copy = add_zero_padding(current_copy)
        padded_current_copy = f"0{current_copy}" if len(f"{current_copy}") < 2 else current_copy
        path = copy_folder(file_format, ioc_name)
        for root, sub_folder, files in os.walk(path):
            file_walk(files, ioc, root)
            folder_walk(ioc, root, sub_folder)


def add_zero_padding(copy):
    """
    Function to add zero padding to the copy number if nessecary.
    :param copy: The copy number to add zero padding to.
    :return:
        The copy, with zero padding added if it has less than 2 digits.
    """
    return f"0{copy}" if len(f"{copy}") < 2 else copy


def check_valid_ioc_to_copy(ioc):
    """
    Check that duplicating this IOC is valid
    :param ioc: The ioc name.
    """
    if not os.path.exists(os.path.join("iocBoot", f"ioc{ioc}-IOC-01", "st-common.cmd")):
        print(
            "No valid st-common.cmd found, this IOC does not appear to be designed in a way that allows duplicates."
        )
        sys.exit()
    else:
        with open(os.path.join("iocBoot", f"ioc{ioc}-IOC-01", "st-common.cmd")) as file_pointer:
            text = file_pointer.read()
            if "\nseq " in text:
                print(
                    "IOC Appears to contain sequencer commands, duplication should be done manually."
                )
                sys.exit()


def main():
    """Main function, sets ioc-name, calls functions in order, and prints when done."""
    help_check()
    global asub_record
    asub_record = False
    initial_copy, ioc, max_copy = handle_arguments()
    check_valid_ioc_to_copy(ioc)
    print("Cleaning directory.")
    os.system("git clean -fqdX")
    print("Clean done, duplicating ioc.")
    copy_loop(initial_copy, max_copy, "{}App", ioc)
    os.chdir(os.path.join(os.getcwd(), "iocBoot"))
    copy_loop(initial_copy, max_copy, "ioc{}", ioc)
    print(
        f"Please run a grep for {START_COPY}. "
        f"There may be some things missed by ths such as axes on a motor, "
        f"as this file cannot just replace all iterations of {START_COPY} "
        f"as doing so could break functionality."
    )
    print("Once you are satisfied with duplication remember to run make.")


if __name__ == "__main__":
    main()
