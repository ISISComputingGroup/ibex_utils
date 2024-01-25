"""
Filesystem utility classes
"""

import binascii
import os
import shutil
import tempfile
import time
import zlib
from ibex_install_utils.exceptions import UserStop
from ibex_install_utils.run_process import RunProcess

LABVIEW_DAE_DIR = os.path.join("C:\\", "LabVIEW modules", "DAE")

def _winapi_path(dos_path):
    path = os.path.abspath(dos_path)
    long_path_identifier = "\\\\?\\"
    if path.startswith(long_path_identifier):
        win_path = path
    elif path.startswith("\\\\"):
        win_path = long_path_identifier + "UNC\\" + path[2:]
    else:
        win_path = long_path_identifier + path
    return win_path

def get_latest_directory_path(build_dir, build_prefix, directory_above_build_num=None, ):
    latest_build_path = os.path.join(build_dir, "LATEST_BUILD.txt")
    build_num = None
    for line in open(latest_build_path):
        build_num = line.strip()
    if build_num is None or build_num == "":
        raise IOError(f"Latest build num unknown. Cannot read it from '{latest_build_path}'")
    if directory_above_build_num is None:
        return os.path.join(build_dir, f"{build_prefix}{build_num}")
    return os.path.join(build_dir, f"{build_prefix}{build_num}", directory_above_build_num)

def _get_dir_size(path="."):
    total = 0
    with os.scandir(_winapi_path(path)) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += _get_dir_size(entry.path)
    return total

def get_size(path='.'):
    wpath = _winapi_path(path)
    if os.path.isfile(wpath):
        return os.path.getsize(wpath)
    elif os.path.isdir(wpath):
        return _get_dir_size(wpath)

class FileUtils:
    """
    Various utilities for interacting with the file system
    """

    @staticmethod
    def is_junction(path: str) -> bool:
        """
        is path a junction
            Args:
                path: path to check
        """
        try:
            return bool(os.readlink(path))
        except OSError:
            return False

    @staticmethod
    def remove_tree(path, prompt, use_robocopy=True, retries=10, leave_top_if_link=False):
        """
        Delete a file path if it exists
        Args:
            path: path to delete
            prompt (ibex_install_utils.user_prompt.UserPrompt): prompt object to communicate with user
            use_robocopy: use robocopy to delete the directory this allows us to remove particularly long paths
            retries: maximum number of attempts to delete file path
            leave_top_if_link: if top level directory is a link, remove directory contents but do not remove link
        """
        for _ in range(retries):
            try:
                if use_robocopy:
                    empty_dir = os.path.join(os.path.dirname(path), "empty_dir_for_robocopy")
                    if os.path.exists(empty_dir):
                        os.rmdir(empty_dir) # in case left over from previous aborted run
                    os.mkdir(empty_dir)
                    if not os.path.exists(empty_dir):
                        prompt.prompt_and_raise_if_not_yes(f'Error creating empty dir for robocopy "{empty_dir}". '
                                                           f'Please do this manually')
                    if os.path.isdir(path):
                        args = [f"{empty_dir}", f"{path}", "/PURGE", "/NJH", "/NJS", "/NP", "/NFL", "/NDL", "/NS", "/NC", "/R:1", "/LOG:NUL"]
                        try:
                            RunProcess(working_dir=os.curdir, executable_file="robocopy", executable_directory="", prog_args=args, expected_return_codes=[0,1,2]).run()
                        except:
                            pass
                    os.rmdir(empty_dir)
                    if leave_top_if_link and FileUtils.is_junction(path):
                        pass
                    else:
                        os.rmdir(path)
                else:
                    shutil.rmtree(path)
            except (IOError, OSError, WindowsError):
                pass

            if os.path.exists(path):
                if leave_top_if_link and FileUtils.is_junction(path) and len(os.listdir(path)) == 0:
                    break
                else:
                    print(f"Deletion of {path} failed, will retry in 5 seconds")
                    # Sleep for a few seconds in case e.g. antivirus has a lock on a file we're trying to delete
                    time.sleep(5)
            else:
                break
        else:
            if os.path.exists(path):
                prompt.prompt_and_raise_if_not_yes(f'Error when deleting "{path}". Please do this manually')

    @staticmethod
    def robocopy_move(src, dst, prompt, retries=10):
        for _ in range(retries):
            try:
                args = [f"{src}", f"{dst}","/E", "/MOV", "/PURGE", "/XJ", "/R:2", "/LOG:NUL", "/NFL", "/NDL", "/NP", "/MT:32"]
                RunProcess(working_dir=os.curdir, executable_file="robocopy", executable_directory="", prog_args=args, expected_return_codes=[0, 1]).run()
            except Exception as e:
                print("Error copying files with robocopy: " + str(e))

            if os.path.exists(dst):
                break
            else:
                print(f"Copy of {src} to {dst} failed, will retry in 5 seconds")
                # Sleep for a few seconds in case e.g. antivirus has a lock on a file we're trying to delete
                time.sleep(5)

    @staticmethod
    def winapi_path(dos_path):
        return _winapi_path(dos_path)

    def mkdir_recursive(self, path):
        """
        Make a directory and all its ancestors
        Args:
            path: path of directory

        Returns:

        """
        sub_path = os.path.dirname(path)
        if not os.path.exists(sub_path):
            self.mkdir_recursive(sub_path)
        if not os.path.exists(path):
            os.mkdir(path)

    @staticmethod
    def move_dir(src, dst, prompt):
        """
        Moves a dir. Better to copy remove so we can handle permissions issues

        Args:
            src: Source directory
            dst: Destination directory
            prompt (ibex_install_utils.user_prompt.UserPrompt): prompt object to communicate with user
        """
        FileUtils.robocopy_move(src, dst, prompt)
        FileUtils.remove_tree(src, prompt)

    @staticmethod
    def move_file(source, destination, prompt):
        """
        Move a file from the source to destination
        Args:
            source: source path
            destination: destination path
            prompt: use this prompt to ask if the move is not sucessful
        """
        while True:
            try:
                shutil.move(source, destination)
                break
            except shutil.Error as ex:
                prompt_message = f"Unable to move '{source}' to '{destination}': {str(ex)}\n Try again?"
                if prompt.prompt(prompt_message, possibles=["Y", "N"], default="N") != "Y":
                    raise UserStop
                
    @staticmethod
    def get_latest_directory_path(build_dir, build_prefix, directory_above_build_num=None, ):
        latest_build_path = os.path.join(build_dir, "LATEST_BUILD.txt")
        build_num = None
        for line in open(latest_build_path):
            build_num = line.strip()
        if build_num is None or build_num == "":
            raise IOError(f"Latest build num unknown. Cannot read it from '{latest_build_path}'")
        if directory_above_build_num is None:
            return os.path.join(build_dir, f"{build_prefix}{build_num}")
        return os.path.join(build_dir, f"{build_prefix}{build_num}", directory_above_build_num)

    @staticmethod
    def _get_dir_size(path="."):
        total = 0
        with os.scandir(winapi_path(path)) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += FileUtils._get_dir_size(entry.path)
        return total
    
    @staticmethod
    def get_size_and_number_of_files(path='.', ignore=None):
        # use copytree to get size of directory
        size_of_dir = 0
        number_of_files = 0

        def total_up_size(src, dst):
            nonlocal size_of_dir
            nonlocal number_of_files
            number_of_files += 1
            size_of_dir += os.path.getsize(src)
        
        temp_dir = tempfile.gettempdir()
        backup_temp_dir = os.path.join(temp_dir, "copy_tree_temp_dir")
        shutil.copytree(winapi_path(path), winapi_path(backup_temp_dir), ignore=ignore, copy_function=total_up_size, dirs_exist_ok=True)
        return size_of_dir, number_of_files

                
    @staticmethod
    def dehex_and_decompress(value):
        """Decompresses the inputted string, assuming it is in hex encoding.

        Args:
            value (bytes): The string to be decompressed, encoded in hex

        Returns:
            bytes : A decompressed version of the inputted string
        """
        assert type(value) == bytes, \
            "Non-bytes argument passed to dehex_and_decompress, maybe Python 2/3 compatibility issue\n" \
            "Argument was type {} with value {}".format(value.__class__.__name__, value)
        return zlib.decompress(binascii.unhexlify(value))
