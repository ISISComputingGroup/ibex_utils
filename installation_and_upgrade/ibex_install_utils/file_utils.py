"""
Filesystem utility classes
"""

import os
import shutil


class FileUtils(object):
    """
    Various utilities for interacting with the file system
    """

    @staticmethod
    def remove_tree(path):
        """
        Delete a file path if it exists
        Args:
            path: path to delete
        """
        empty_dir = r"\\isis\inst$\Kits$\CompGroup\ICP\empty_dir_for_robocopy"
        if os.path.isdir(path):
            os.system("robocopy \"{}\" \"{}\" /PURGE /NJH /NJS /NP /NFL /NDL /NS /NC /R:1 /LOG:NUL".
                      format(empty_dir, path))

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
