import os
import shutil
import shutil
import sys
import zipfile

from ibex_install_utils.file_utils import FileUtils
from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import INSTRUMENT_BASE_DIR, BACKUP_DATA_DIR, BACKUP_DIR, EPICS_PATH, \
    PYTHON_PATH, PYTHON_3_PATH, EPICS_UTILS_PATH, GUI_PATH, STAGE_DELETED


## tuple (PATH,ignore) with ignore pattern passed to shutil.copytree during backup
## used to exclude directories from a running instrument that are either not useful
## or e.g. may have too long a path or some other issues
ALL_INSTALL_DIRECTORIES = (
  # tempted to add '*.pyc', '__pycache__' but then it is not an identical backup if renamed back
  (EPICS_PATH, shutil.ignore_patterns('jettywork', '*.*dmp', '*.stackdump')),
  (PYTHON_PATH, shutil.ignore_patterns('*.*dmp', '*.stackdump')),
  (PYTHON_3_PATH, shutil.ignore_patterns('*.*dmp', '*.stackdump')),
  (GUI_PATH, shutil.ignore_patterns('*.*dmp', '*.stackdump')),
  (EPICS_UTILS_PATH, shutil.ignore_patterns('*.*dmp', '*.stackdump'))
)

class BackupTasks(BaseTasks):
    # lowercase names of directories we are not worried about if they do
    # not exist for example Python which has been Python3 for some time
    FAILED_BACKUP_DIRS_TO_IGNORE = [ r'c:\instrument\apps\python' ]

    def update_progress_bar(self,progress, total, width=20):
        if total !=0:
            percent = (progress/total) 
            arrow = '=' * int(round(width * percent))
            spaces = ' ' * (width - len(arrow))
            sys.stdout.write(f'\rProgress: [{arrow + spaces}] {int(percent * 100)}% ({progress}/{total})')
            if progress == total:
                sys.stdout.write('\n')
            sys.stdout.flush()


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
                    
    def backup_files(self, src, dst, copy=False, ignore=None, number_of_files=0):
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
            self.update_progress_bar(current_file_index, number_of_files)

        shutil.copytree(FileUtils.winapi_path(src), FileUtils.winapi_path(dst), ignore=ignore,
                        copy_function=copy_function, dirs_exist_ok=True)
    

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
            backup_size, number_of_files = self._check_backup_space(src, ignore=ignore)

            if copy:
                print(f"Copying {src} to {backup_dir}")
                self.backup_files(src, backup_dir, copy=True, ignore=ignore, number_of_files=number_of_files)
            else:
                print(f"Moving {src} to {backup_dir}")
                self.backup_files(src, backup_dir, ignore=ignore, number_of_files=number_of_files)
                
        else: # if src can't be found on the machine
            if src.lower() in self.FAILED_BACKUP_DIRS_TO_IGNORE:
                print(f"Skipping {src} backup as not present has been marked as OK")
            else:
                self.prompt.prompt_and_raise_if_not_yes(f"You appear to backing up {src}, but it doesn't exist on this machine. Please manually check your installation first.")

    @task("Backup old directories")
    def backup_old_directories(self):
        """
        Backup old directories
        """
        if os.path.exists(BACKUP_DATA_DIR):
            if not os.path.exists(BACKUP_DIR):
                os.mkdir(BACKUP_DIR)      

            # Move the folders
            for path in ALL_INSTALL_DIRECTORIES:
                self._backup_dir(path[0], ignore=path[1], copy=True)

            # Backup settings and autosave
            self._backup_dir(os.path.join(INSTRUMENT_BASE_DIR, "Settings"), ignore=shutil.ignore_patterns("labview modules",
                                                                                     "$RECYCLE.BIN", "System Volume Information"))
            self._backup_dir(os.path.join(INSTRUMENT_BASE_DIR, "var", "Autosave"))

             # Move all but the newest backup
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
        else:
            self.prompt.prompt_and_raise_if_not_yes(
                f"Unable to find data directory '{BACKUP_DATA_DIR}'. Please backup the current installation of IBEX "
                f"manually")


    #This function checks if the backup has been sucessful by checking for a VERSION.txt file within the backup folders
    @task("Verify backup") 
    def backup_checker(self):
        """
        Verify backup

        """
        EPICS_PATH_BACKUP = os.path.join(self._get_backup_dir(),'EPICS')
        PYTHON3_PATH_BACKUP = os.path.join(self._get_backup_dir(),'Python3')
        GUI_PATH_BACKUP = os.path.join(self._get_backup_dir(),'Client_E4')  
        SETTINGS_PATH = os.path.join(self._get_backup_dir(), "Settings")
        AUTOSAVE_PATH = os.path.join(self._get_backup_dir(), "Autosave")
        UTILS_PATH = os.path.join(self._get_backup_dir(), 'EPICS_UTILS')

        backup_paths = (EPICS_PATH_BACKUP, PYTHON3_PATH_BACKUP, GUI_PATH_BACKUP)

        for d in backup_paths:
            if not os.path.exists(os.path.join(d, "VERSION.txt")):
                self.prompt.prompt_and_raise_if_not_yes(f"Error found with backup. Backup failed at '{d}'. Please backup manually.")

        if not os.path.exists(SETTINGS_PATH):
            self.prompt.prompt_and_raise_if_not_yes(f"Error found with backup. Settings did not back up properly. Please backup manually.")
        if not os.path.exists(AUTOSAVE_PATH):
            self.prompt.prompt_and_raise_if_not_yes(f"Error found with backup. Autosave did not back up properly. Please backup manually.")
        if not os.path.exists(UTILS_PATH):
            self.prompt.prompt_and_raise_if_not_yes(f"Error found with backup. EPICS_Utils did not back up properly. Please backup manually.")

    @task("Removing old version of IBEX")
    def remove_old_ibex(self):
        """
        Removes older versions of IBEX server, client, genie_python and epics utils
        Returns:

        """
        for path in ALL_INSTALL_DIRECTORIES:
            self._file_utils.remove_tree(path[0], self.prompt, leave_top_if_link=True)
