import os
import shutil
import shutil

from ibex_install_utils.user_prompt import UserPrompt
from ibex_install_utils.progress_bar import ProgressBar
from ibex_install_utils.file_utils import FileUtils
from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import BACKUP_DATA_DIR, BACKUP_DIR, EPICS_PATH, \
    PYTHON_PATH, PYTHON_3_PATH, EPICS_UTILS_PATH, GUI_PATH, STAGE_DELETED, SETTINGS_DIR, AUTOSAVE

COMMON_IGNORE_PATTERNS = ['*.*dmp', '*.stackdump',]

IGNORE_PATTERNS = {
    # tempted to add '*.pyc', '__pycache__' but then it is not an identical backup if renamed back
    EPICS_PATH: shutil.ignore_patterns(*COMMON_IGNORE_PATTERNS, '.git', 'jettywork'),
    PYTHON_PATH: shutil.ignore_patterns(*COMMON_IGNORE_PATTERNS, '.git'),
    PYTHON_3_PATH: shutil.ignore_patterns(*COMMON_IGNORE_PATTERNS, '.git'),
    GUI_PATH: shutil.ignore_patterns(*COMMON_IGNORE_PATTERNS),  # not having git might be problem with the scripts directory
    EPICS_UTILS_PATH: shutil.ignore_patterns(*COMMON_IGNORE_PATTERNS, '.git'),
    SETTINGS_DIR: shutil.ignore_patterns("labview modules", "$RECYCLE.BIN", "System Volume Information"),
}
"""
Dictionary {PATH: list of glob-style ignore patterns} with ignore pattern passed to shutil.copytree during backup
used to exclude directories from a running instrument that are either not useful
or e.g. may have too long a path or some other issues

"""

ALL_INSTALL_DIRECTORIES = (EPICS_PATH, PYTHON_PATH, PYTHON_3_PATH, GUI_PATH, EPICS_UTILS_PATH)
DIRECTORIES_TO_BACKUP = (*ALL_INSTALL_DIRECTORIES, SETTINGS_DIR, AUTOSAVE)

class BackupTasks(BaseTasks):
    """
    The tasks dealing with backing up current install, removing current install and moving old backups to the shares.

    """
    FAILED_BACKUP_DIRS_TO_IGNORE = [ r'c:\instrument\apps\python' ]
    """
    lowercase names of directories we are not worried about if they do
    not exist for example Python which has been Python3 for some time

    """
    progress_bar = ProgressBar()
    """To indicate tasks' progress"""

    @task("Backup old directories")
    def backup_old_directories(self):
        """
        Backup old directories.

        """
        if os.path.exists(BACKUP_DATA_DIR):
            if not os.path.exists(BACKUP_DIR):
                os.mkdir(BACKUP_DIR)      

            # Move the folders
            for path in DIRECTORIES_TO_BACKUP:
                if path in os.getcwd():
                    self.prompt.prompt_and_raise_if_not_yes(
                        f"You appear to be trying to delete the folder, {path}, containing the current working directory {os.getcwd()}. "
                        f"Please do this manually to be on the safe side")
                else:
                    self._backup_dir(path, ignore=IGNORE_PATTERNS.get(path), copy=True)

            self._move_old_backups_to_share()
        else:
            self.prompt.prompt_and_raise_if_not_yes(
                f"Unable to find data directory '{BACKUP_DATA_DIR}'. Please backup the current installation of IBEX "
                f"manually")
            
    @task("Verify backup") 
    def backup_checker(self):
        """
        Verify backup. This function checks if the backup has been sucessful by checking for a
        VERSION.txt file within the backup folders for EPICS, PYTHON, GUI.

        """
        for path in (EPICS_PATH, PYTHON_3_PATH, GUI_PATH):
            path_to_backup = self._path_to_backup(path)
            if not os.path.exists(os.path.join(path_to_backup, "VERSION.txt")):
                self.prompt.prompt_and_raise_if_not_yes(f"Error found with backup. Backup failed at '{path_to_backup}'. Please backup manually.")
        
        for path in (SETTINGS_DIR, AUTOSAVE, EPICS_UTILS_PATH):
            if not os.path.exists(self._path_to_backup(path)):
                self.prompt.prompt_and_raise_if_not_yes(f"Error found with backup. '{path}' did not back up properly. Please backup manually.")
    
    @task("Removing old version of IBEX")
    def remove_old_ibex(self):
        """
        Removes older versions of IBEX server, client, genie_python and epics utils.

        """
        for path in ALL_INSTALL_DIRECTORIES:
            self._file_utils.remove_tree(path[0], self.prompt, leave_top_if_link=True)

    def _path_to_backup(self, path):
        """Returns backup path for the given path"""
        return os.path.join(self._get_backup_dir(), os.path.basename(path))
    
    def _check_backup_space(self, src, ignore=None):
        # Checks if there is enough space to move dir at src into the backup directory
        # (all in bytes)
        _, _, free = shutil.disk_usage(BACKUP_DIR)
        backup_size, number_of_files = FileUtils.get_size_and_number_of_files(src, ignore=ignore)
        while backup_size > free:
            needed_space = round((backup_size - free) / (1024 ** 3), 2)
            self.prompt.prompt_and_raise_if_not_yes(f"You don't have enough space to backup. Free up {needed_space} GB at {BACKUP_DIR}")
            _, _, free = shutil.disk_usage(BACKUP_DIR)

        return backup_size, number_of_files

    def _backup_dir(self, src, copy=True, ignore=None):
        """Move a directory to the backup area.

        If the optional copy flag is true, the directory in `src` will be kept;
        if it is false, the directory at `src` will be moved to the backup area.

        The optional ignore argument is a callable. If given, it
        is passed onto the `shutil.copytree` function for its optional ignore argument.
        
        Args:
            src: path of the directory to be backed up
            copy: Whether or not to keep dir at original place
            ignore: A callable like `shutil.ignore_patterns`
        
        """
        try:
            # Optimistic start
            print(f"\nPreparing to back up {src} ...")

            _, number_of_files = self._check_backup_space(src, ignore=ignore)
            self.progress_bar.reset(total=number_of_files)

            dst = self._path_to_backup(src)

            print("Attempting to " + ("copy" if copy else "move") + f" {src} to {dst}")

            def copy_function(src, dst):
                """Just a copy or move operation that also updates the progress bar."""
                if copy:
                    shutil.copy2(src, dst)
                else:
                    shutil.move(src, dst)

                self.progress_bar.progress += 1
                self.progress_bar.print()

            # Actual backup step
            shutil.copytree(
                FileUtils.winapi_path(src),
                FileUtils.winapi_path(dst),
                ignore=ignore,
                copy_function=copy_function)
        
        except FileNotFoundError:
            # Source file is not present
            if src.lower() in self.FAILED_BACKUP_DIRS_TO_IGNORE:
                print(f"Skipping {src} backup as not present has been marked as OK.")
            else:
                self.prompt.prompt_and_raise_if_not_yes(
                    f"You appear to backing up {src}, but it doesn't exist on this machine. Please manually check your installation first.")
        
        except FileExistsError:
            # Destination directory already exists
            self.prompt.prompt_and_raise_if_not_yes(
                f"Backup dir {dst} already exists. Please backup this app manually.")
        
        except PermissionError:
            # User has no permission to modify file system
            self.prompt.prompt_and_raise_if_not_yes(
                f"You have no permission to backup {dst}. Please backup this app manually.")
        
        except shutil.Error as exc:
            # Custom errors occured in shutil.copytree
            errors = exc.args[0]
            for error in errors:
                _, _, msg = error
                print(msg)

        except:
            # All other errors
            self.prompt.prompt_and_raise_if_not_yes(
                f"Something went wrong while backing up {src}. Please backup this app manually.")

        else:
            # Finished successfully
            print(f"Successfully backed up to {dst}.")

    #? Moving other backups to stage deleted could be a task on its own
    def _move_old_backups_to_share(self):
        """
        Move all but the newest backup to the shares.

        """
        current_backups = [os.path.join(BACKUP_DIR, d) for d in os.listdir(BACKUP_DIR)
                            if os.path.isdir(os.path.join(BACKUP_DIR, d)) and d.startswith("ibex_backup")]
        if len(current_backups) > 0:
            all_but_newest_backup = sorted(current_backups, key=os.path.getmtime)[:-1]
            backups_to_move = all_but_newest_backup
        else:
            backups_to_move = []

        for d in backups_to_move:
            backup = STAGE_DELETED + '\\' + self._get_machine_name() + '\\' + os.path.basename(d)
            print(f"Moving backup {d} to {backup}")
            self._file_utils.move_dir(d, backup, self.prompt)

if __name__ == "__main__":
    """For running task standalone
    Must be called with pythonpath set to `<exact path on your pc>/installation_and_upgrade`
    as that is the root of this module and all our imports work that way.

    This effectively means to call `set PYTHONPATH=. && python ibex_install_utils/tasks/backup_tasks.py`
    from the installation_and_upgrade directory in terminal.
    """
    print("Running backup task standalone.")

    #! Copying older backups to share will likely fail on developer machines
    prompt = UserPrompt(False, True)
    task = BackupTasks(prompt, '', '', '', '')

    task.backup_old_directories()
    task.backup_checker()
    task.remove_old_ibex()