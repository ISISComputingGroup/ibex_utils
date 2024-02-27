import os
import shutil
import shutil
import sys
import zipfile

from ibex_install_utils.progress_bar import ProgressBar
from ibex_install_utils.file_utils import FileUtils
from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import BACKUP_DATA_DIR, BACKUP_DIR, EPICS_PATH, \
    PYTHON_PATH, PYTHON_3_PATH, EPICS_UTILS_PATH, GUI_PATH, STAGE_DELETED, SETTINGS_DIR, AUTOSAVE

COMMON_IGNORE_PATTERNS = ['*.*dmp', '*.stackdump',]

## dictionary {PATH: ignore} with ignore pattern passed to shutil.copytree during backup
## used to exclude directories from a running instrument that are either not useful
## or e.g. may have too long a path or some other issues
IGNORE_PATTERNS = {
    # tempted to add '*.pyc', '__pycache__' but then it is not an identical backup if renamed back
    EPICS_PATH: shutil.ignore_patterns(*COMMON_IGNORE_PATTERNS, '.git', 'jettywork'),
    PYTHON_PATH: shutil.ignore_patterns(*COMMON_IGNORE_PATTERNS, '.git'),
    PYTHON_3_PATH: shutil.ignore_patterns(*COMMON_IGNORE_PATTERNS, '.git'),
    GUI_PATH: shutil.ignore_patterns(*COMMON_IGNORE_PATTERNS),  # not having git might be problem with the scripts directory
    EPICS_UTILS_PATH: shutil.ignore_patterns(*COMMON_IGNORE_PATTERNS, '.git'),
    SETTINGS_DIR: shutil.ignore_patterns("labview modules", "$RECYCLE.BIN", "System Volume Information"),
}

ALL_INSTALL_DIRECTORIES = (EPICS_PATH, PYTHON_PATH, PYTHON_3_PATH, GUI_PATH, EPICS_UTILS_PATH)
DIRECTORIES_TO_BACKUP = (*ALL_INSTALL_DIRECTORIES, SETTINGS_DIR, AUTOSAVE)

class BackupTasks(BaseTasks):
    # lowercase names of directories we are not worried about if they do
    # not exist for example Python which has been Python3 for some time
    FAILED_BACKUP_DIRS_TO_IGNORE = [ r'c:\instrument\apps\python' ]

    progress_bar = ProgressBar()

    def zip_file(self, filename, zipname):

        all_files = []
        for root, dirs, files in os.walk(filename):
            for file in files:
                all_files.append(os.path.join(root, file))
        
        i = 1
        with zipfile.ZipFile(zipname + ".zip", 'w', zipfile.ZIP_DEFLATED, strict_timestamps=False) as zipf:
            for root, dirs, files in os.walk(filename):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=os.path.join(root, file).replace(filename, ''))
                    self.update_progress_bar(i, len(all_files))
                    i = i + 1
                    
    def backup_files(self, src, dst, copy=False, ignore=None):
        current_file_index = 0

        def copy_function(src, dst):
            nonlocal current_file_index

            if copy:
                operation = shutil.copy2
            else:
                operation = shutil.move

            try:
                operation(FileUtils.winapi_path(src), FileUtils.winapi_path(dst))
            except PermissionError as e:
                print(f"PermissionError: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

            current_file_index += 1
            self.progress_bar.progress = current_file_index
            self.progress_bar.print()

        shutil.copytree(FileUtils.winapi_path(src), FileUtils.winapi_path(dst), ignore=ignore, copy_function=copy_function, dirs_exist_ok=True)
    
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
        backup_dir = os.path.join(self._get_backup_dir(), os.path.basename(src))
        if src in os.getcwd():
            self.prompt.prompt_and_raise_if_not_yes(
                f"You appear to be trying to delete the folder, {src}, containing the current working directory {os.getcwd()}. "
                f"Please do this manually to be on the safe side")
            return
        if os.path.exists(backup_dir):
            self.prompt.prompt_and_raise_if_not_yes(
                f"Backup dir {backup_dir} already exists. Please backup this app manually")
            return
        if os.path.exists(src):
            _, number_of_files = self._check_backup_space(src, ignore=ignore)

            self.progress_bar.total = number_of_files

            print(("Copying" if copy else "Moving") + f" {src} to {backup_dir}")
            self.backup_files(src, backup_dir, copy=copy, ignore=ignore)
                
        else: # if src can't be found on the machine
            if src.lower() in self.FAILED_BACKUP_DIRS_TO_IGNORE:
                print(f"Skipping {src} backup as not present has been marked as OK")
            else:
                self.prompt.prompt_and_raise_if_not_yes(f"You appear to backing up {src}, but it doesn't exist on this machine. Please manually check your installation first.")

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
                self._backup_dir(path, ignore=IGNORE_PATTERNS.get(path), copy=True)

            self._move_old_backups_to_share()
        else:
            self.prompt.prompt_and_raise_if_not_yes(
                f"Unable to find data directory '{BACKUP_DATA_DIR}'. Please backup the current installation of IBEX "
                f"manually")

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

    def _path_to_backup(self, path):
        """Returns backup path for the given path"""
        return os.path.join(self._get_backup_dir(), os.path.basename(path))
    
    @task("Removing old version of IBEX")
    def remove_old_ibex(self):
        """
        Removes older versions of IBEX server, client, genie_python and epics utils.

        """
        for path in ALL_INSTALL_DIRECTORIES:
            self._file_utils.remove_tree(path[0], self.prompt, leave_top_if_link=True)
