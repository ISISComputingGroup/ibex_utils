"""
Filesystem utility classes
"""

import os
import shutil
import stat
from time import sleep

from ibex_install_utils.exceptions import ErrorWithFile


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

        Returns:

        Raises ErrorWithFile: if it can not delete a file

        """
        def on_error_make_read_write(func, current_path, exc_info):
            """
            If there is an error then make file read write and try again
            Args:
                func: function it was in
                current_path: path it had troubles with
                exc_info: exception information

            Returns:

            """
            if exc_info[0] is WindowsError:
                try:
                    try:
                        # try remove second time (doesn't always work first time)
                        if func == os.rmdir:
                            sleep(0.1)
                            os.rmdir(current_path)
                            return
                    except WindowsError:
                        pass

                    os.chmod(current_path, stat.S_IRWXU)
                    os.remove(current_path)
                    return
                except Exception:
                    pass
            raise ErrorWithFile(
                "Failed to delete file {file} from epics because: {error}".format(file=current_path,
                                                                                  error=str(exc_info)))

        if os.path.isdir(path):
            shutil.rmtree(path, onerror=on_error_make_read_write)

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
