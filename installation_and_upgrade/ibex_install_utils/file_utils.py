"""
Filesystem utility classes
"""

import os
import shutil
import time
from ibex_install_utils.exceptions import UserStop
from ibex_install_utils.run_process import RunProcess

LABVIEW_DAE_DIR = os.path.join("C:\\", "LabVIEW modules", "DAE")


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


class FileUtils:
    """
    Various utilities for interacting with the file system
    """

    @staticmethod
    def remove_tree(path, prompt, use_robocopy=True, retries=10):
        """
        Delete a file path if it exists
        Args:
            path: path to delete
            prompt (ibex_install_utils.user_prompt.UserPrompt): prompt object to communicate with user
            use_robocopy: use robocopy to delete the directory this allows us to remove particularly long paths
            retries: maximum number of attempts to delete file path
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
                            RunProcess(working_dir=os.curdir, executable_file="robocopy", executable_directory="", prog_args=args).run()
                        except:
                            pass
                    os.rmdir(empty_dir)
                    os.rmdir(path)
                else:
                    shutil.rmtree(path)
            except (IOError, OSError, WindowsError):
                pass

            if os.path.exists(path):
                print(f"Deletion of {path} failed, will retry in 5 seconds")
                # Sleep for a few seconds in case e.g. antivirus has a lock on a file we're trying to delete
                time.sleep(5)
            else:
                break
        else:
            if os.path.exists(path):
                prompt.prompt_and_raise_if_not_yes(f'Error when deleting "{path}". Please do this manually')

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
        shutil.copytree(src, dst)
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
