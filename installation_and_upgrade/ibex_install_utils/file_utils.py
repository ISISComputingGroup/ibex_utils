"""
Filesystem utility classes
"""

import os
import shutil

from ibex_install_utils.exceptions import UserStop


class FileUtils(object):
    """
    Various utilities for interacting with the file system
    """

    @staticmethod
    def remove_tree(path, use_robocopy=True):
        """
        Delete a file path if it exists
        Args:
            path: path to delete
            use_robocopy: use robocopy to delete the directory this allows us to remove particularly long paths
        """
        if use_robocopy:
            empty_dir = os.path.join(os.path.dirname(path), "empty_dir_for_robocopy")
            os.mkdir(empty_dir)
            if os.path.isdir(path):
                os.system("robocopy \"{}\" \"{}\" /PURGE /NJH /NJS /NP /NFL /NDL /NS /NC /R:1 /LOG:NUL".
                          format(empty_dir, path))
            os.rmdir(empty_dir)
            os.rmdir(path)
        else:
            shutil.rmtree(path)
        if os.path.exists(path):
            raise IOError('Path could not be deleted, please do this manually. Path: "{}"'.format(path))

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
    def move_dir(src, dst):
        """
        Moves a dir. Better to copy remove so we can handle permissions issues

        Args:
            src: Source directory
            dst: Destination directory
        """
        shutil.copytree(src, dst)
        FileUtils.remove_tree(src)

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
