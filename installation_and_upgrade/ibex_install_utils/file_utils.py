"""
Filesystem utility classes
"""

import os
import time
import shutil

from ibex_install_utils.exceptions import UserStop


class FileUtils(object):
    """
    Various utilities for interacting with the file system
    """

    @staticmethod
    def remove_tree(path, prompt, use_robocopy=True):
        """
        Delete a file path if it exists
        Args:
            path: path to delete
            prompt (ibex_install_utils.user_prompt.UserPrompt): prompt object to communicate with user
            use_robocopy: use robocopy to delete the directory this allows us to remove particularly long paths
        """

        try:
            if use_robocopy:
                empty_dir = os.path.join(os.path.dirname(path), "empty_dir_for_robocopy")
                if os.path.exists(empty_dir):
                    os.rmdir(empty_dir) # in case left over from previous aborted run
                os.mkdir(empty_dir)
                if not os.path.exists(empty_dir):
                    prompt.prompt_and_raise_if_not_yes('Error creating empty dir for robocopy "{}". '
                                                       'Please do this manually'.format(empty_dir))
                retry_time = 30
                for _ in range(2):
                    if os.path.isdir(path):
                        try:
                            os.system("robocopy \"{}\" \"{}\" /PURGE /NOCOPY /NJH /NJS /MT /NP /NFL /NDL /NS /NC /R:2 "
                                      "/LOG:NUL".format(empty_dir, path))
                            os.rmdir(path)
                        except (IOError, OSError, WindowsError):
                            print("remove_tree: retrying delete in {} seconds".format(retry_time))
                            time.sleep(retry_time)
                os.rmdir(empty_dir)
            else:
                shutil.rmtree(path)
        except (IOError, OSError, WindowsError):
            pass
        if os.path.exists(path):
            prompt.prompt_and_raise_if_not_yes('Error when deleting "{}". Please do this manually'.format(path))

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
                prompt_message = "Unable to move '{}' to '{}': {}\n Try again?".format(source, destination, str(ex))
                if prompt.prompt(prompt_message, possibles=["Y", "N"], default="N") != "Y":
                    raise UserStop
