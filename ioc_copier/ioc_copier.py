"""
Script to handle duplicating IOCs
"""

from shutil import copytree
import sys
import os
import re


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
        os.rename(os.path.join(root_folder, rename),
                  os.path.join(root_folder, rename.replace(f"IOC_{padded_start_copy}",
                                                           f"IOC_{padded_current_copy}")))
    if f"IOC-{padded_start_copy}" in rename:
        os.rename(os.path.join(root_folder, rename),
                  os.path.join(root_folder, rename.replace(f"IOC-{padded_start_copy}",
                                                           f"IOC-{padded_current_copy}")))
    if f"{ioc}_{padded_start_copy}" in rename:
        os.rename(os.path.join(root_folder, rename),
                  os.path.join(root_folder, rename.replace(f"{ioc}_{padded_start_copy}",
                                                           f"{ioc}_{padded_current_copy}")))


def replace_text(text_lines, ioc):
    """
    Function to handle replacing of text within files.
    Parameters:
        text_lines - the text from the file to process.
        start - the value to look for to remove.
        current - the value to replace start with.
    """
    for i in range(len(text_lines)):
        temp_text = re.sub(f"IOC_{start_copy}", f"IOC_{current_copy}", text_lines[i])
        text_lines[i] = temp_text
        temp_text = re.sub(f"IOC-{start_copy}", f"IOC-{current_copy}", text_lines[i])
        text_lines[i] = temp_text
        temp_text = re.sub(f"{ioc}_{start_copy}", f"{ioc}_{current_copy}", text_lines[i])
        text_lines[i] = temp_text
        temp_text = re.sub(f"RAMPFILELIST{start_copy}", f"RAMPFILELIST{current_copy}", text_lines[i])
        text_lines[i] = temp_text

        temp_text = re.sub(f"IOC_0{start_copy}", f"IOC_{padded_current_copy}", text_lines[i])
        text_lines[i] = temp_text
        temp_text = re.sub(f"IOC-0{start_copy}", f"IOC-{padded_current_copy}", text_lines[i])
        text_lines[i] = temp_text
        temp_text = re.sub(f"{ioc}_0{start_copy}", f"{ioc}_{padded_current_copy}", text_lines[i])
        text_lines[i] = temp_text
        temp_text = re.sub(f"RAMPFILELIST0{start_copy}", f"RAMPFILELIST{padded_current_copy}",
                           text_lines[i])
        text_lines[i] = temp_text


def help_check():
    """
    Function to handle printing help.
    """
    if "-h" in sys.argv:
        print("First Argument: <ioc-to-duplicate>")
        print("This should be the name of the ioc folder, the folders to "
              "actual duplicate will all contain this in their names.\n")
        print("Second Argument: <number-ioc-to-copy")
        print("This should be the last currently existing ioc number, "
              "e.g. 2. IOC-01 should not be copied in this way, as later"
              " iocs should reference some of its files rather than copy them.\n")
        print("Third Argument: <first-copy>")
        print("This should be the number of the first copy, i.e."
              " the first IOC made will be IOC-<first-copy>.\n")
        print("Fourth Argument: <max-number-ioc>")
        print("This should be the maximum number copied to.\n")
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
        print("Arguments should be <ioc-to-duplicate> <number-ioc-to-copy> "
              "<first-copy> <max-number-ioc>")
        print("use argument \"-h\" for more details.")
        sys.exit()
    elif len(sys.argv) > 5:
        print("Too many arguments")
        print("Arguments should be <ioc-to-duplicate> <number-ioc-to-copy> "
              "<first-copy> <max-number-ioc>")
        print("use argument \"-h\" for more details.")
        sys.exit()
    else:
        ioc = sys.argv[1]
        global start_copy
        start_copy= int(sys.argv[2])
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
        copytree(os.path.join(os.getcwd(), start_path), os.path.join(path))
    except FileExistsError:
        raise FileExistsError(f"Copy {padded_current_copy} already exists, please ensure that the initial copy "
                              f"argument is greater than the highest number IOC.") from None
    return path


def get_file_text(file, ioc, root):
    """
    function to get the text to write to a file.
    :param file: The file to get the initial text from.
    :param ioc: The Ioc name.
    :param root: The root folder.
    :return:
        The text from the file, with the IOC number updated to the current copy.
    """
    with open(os.path.join(root, file), "r") as file_pointer:
        text = file_pointer.readlines()
    replace_text(text, ioc)
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
    :param current_copy: The current ioc number.
    :param start_copy: The ioc number to copy
    :param padded_current_copy: The current ioc number with zero padding.
    :param padded_start_copy: The ioc number to copy with zero padding.
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
    :param padded_current_copy:  the current iteration of the ioc number, zero padded
    :param padded_start_copy: the ioc number to copy, zero padded.
    :param root:
    :param sub_folder:
    :return:
    """
    for folder in sub_folder:
        rename_files(root, folder, ioc, padded_start_copy, padded_current_copy)


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
        padded_start_copy = add_zero_padding(start_copy)
        padded_current_copy = add_zero_padding(current_copy)
        padded_current_copy = f"0{current_copy}" if len(f"{current_copy}") < 2 else current_copy
        path = copy_folder(file_format, ioc_name)
        for root, sub_folder, files in os.walk(path):
            file_walk(files, ioc, root)
            folder_walk(ioc, root, sub_folder)


def add_zero_padding(copy):
    return f"0{copy}" if len(f"{copy}") < 2 else copy


def main():
    """Main function, sets ioc-name, calls functions in order, and prints when done."""
    help_check()
    initial_copy, ioc, max_copy = handle_arguments()
    copy_loop(start_copy, initial_copy, max_copy, "{}App", ioc)
    os.chdir(os.path.join(os.getcwd(), "iocBoot"))
    copy_loop(start_copy, initial_copy, max_copy, "ioc{}", ioc)
    print(f"Please run a grep for {start_copy}. "
          f"There may be some things missed by ths such as axes on a motor, "
          f"as this file cannot just replace all iterations of {start_copy} "
          f"as doing so could break functionality.")

if __name__ == '__main__':
    main()
