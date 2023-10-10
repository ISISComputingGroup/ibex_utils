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

ALL_INSTALL_DIRECTORIES = (EPICS_PATH, PYTHON_PATH, PYTHON_3_PATH, GUI_PATH, EPICS_UTILS_PATH)


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

    def move_file(self, src, dst, copy=False):
        all_files = []
        for root, dirs, files in os.walk(src):
            for file in files:
                all_files.append((os.path.join(root, file), os.path.join(dst, os.path.relpath(root, src))))

        total_files = len(all_files)

        if copy:
            operation = shutil.copy
        else:
            operation = shutil.move

        i = 0
        for file, dest_dir in all_files:
            try:
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                if os.path.exists(file):
                    operation(file, os.path.join(dest_dir, os.path.basename(file)))
                    i += 1
                else:
                    print(f"File not found: {file}")
            except Exception as e:
                print(f"Error: {e}")

            self.update_progress_bar(i, total_files)
        

    def _check_backup_space(self, src):
        # Checks if there is enough space to move dir at src into the backup directory
        # (all in bytes)
        _, _, free = shutil.disk_usage(BACKUP_DIR)
        backup_size = FileUtils.get_size(src)

        if backup_size > free:
            needed_space = round((backup_size - free) / (1024 ** 3), 2)
            self.prompt.prompt_and_raise_if_not_yes(f"You don't have enough space to backup. Free up {needed_space} GB at {BACKUP_DIR}")

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
            self._check_backup_space(src)

            if copy:
                print(f"Copying {src} to {backup_dir}")
                self.move_file(src, backup_dir, copy=True)
                # self.zip_file(src, backup_dir)
            else:
                print(f"Moving {src} to {backup_dir}")
                self.move_file(src, backup_dir)
                # self.zip_file(src, backup_dir)
                
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
            for app_path in ALL_INSTALL_DIRECTORIES:
                self._backup_dir(app_path, copy=True)

            

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
                # self.move_file(d, backup, copy=False)
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
            self._file_utils.remove_tree(path, self.prompt, leave_top_if_link=True)
