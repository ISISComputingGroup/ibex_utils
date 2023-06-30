import os
import shutil


from ibex_install_utils.task import task
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.tasks.common_paths import INSTRUMENT_BASE_DIR, BACKUP_DATA_DIR, BACKUP_DIR, EPICS_PATH, \
    PYTHON_PATH, PYTHON_3_PATH, EPICS_UTILS_PATH, GUI_PATH

ALL_INSTALL_DIRECTORIES = (EPICS_PATH, PYTHON_PATH, PYTHON_3_PATH, GUI_PATH, EPICS_UTILS_PATH)


class BackupTasks(BaseTasks):

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
            if copy:
                print(f"Copying {src} to {backup_dir}")
                shutil.copytree(src, backup_dir, ignore=ignore)
            else:
                print(f"Moving {src} to {backup_dir}")
                self._file_utils.move_dir(src, backup_dir, self.prompt)
        else: #if src can't be found on the machine
            self.prompt.prompt_and_raise_if_not_yes(f"You appear to backing up {src}, but it doesn't exist on this machine. If it is Python, this is likely okay. Please manually check your installation first.")

    @task("Backup old directories")
    def backup_old_directories(self):
        """
        Backup old directories
        """
        if os.path.exists(BACKUP_DATA_DIR):
            if not os.path.exists(BACKUP_DIR):
                os.mkdir(BACKUP_DIR)

            # Delete all but the oldest backup
            current_backups = [os.path.join(BACKUP_DIR, d) for d in os.listdir(BACKUP_DIR)
                               if os.path.isdir(os.path.join(BACKUP_DIR, d)) and d.startswith("ibex_backup")]
            if len(current_backups) > 0:
                all_but_newest_backup = sorted(current_backups, key=os.path.getmtime)[:-1]
                backups_to_delete = all_but_newest_backup
            else:
                backups_to_delete = []

            for d in backups_to_delete:
                print(f"Removing backup {d}")
                self._file_utils.remove_tree(os.path.join(BACKUP_DIR, d), self.prompt)

            # Move the folders
            for app_path in ALL_INSTALL_DIRECTORIES:
                self._backup_dir(app_path, copy=False)

            # Backup settings and autosave
            self._backup_dir(os.path.join(INSTRUMENT_BASE_DIR, "Settings"), ignore=shutil.ignore_patterns("labview modules",
                                                                                     "$RECYCLE.BIN", "System Volume Information"))
            self._backup_dir(os.path.join(INSTRUMENT_BASE_DIR, "var", "Autosave"))
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
        SETTINGS_PATH = os.path.join(INSTRUMENT_BASE_DIR, "Settings")
        AUTOSAVE_PATH = os.path.join(INSTRUMENT_BASE_DIR, "Var", "Autosave")
        UTILS_PATH = os.path.join(self._get_backup_dir(), 'EPICS_UTILS')

        backup_paths = (EPICS_PATH_BACKUP, PYTHON3_PATH_BACKUP, GUI_PATH_BACKUP)

        for d in backup_paths:
            if not(os.path.exists(os.path.join(d, "VERSION.txt"))):
                backup_failed_str = "Backup failed at " + d
                self.prompt.prompt_and_raise_if_not_yes(f(backup_failed_str))
                self.prompt.prompt_and_raise_if_not_yes(f"Error found with backup. Continue? ")

        if not(os.path.exists(SETTINGS_PATH)):
            self.prompt.prompt_and_raise_if_not_yes(f"Error found with backup. Settings did not back up properly. Continue? ")
        if not(os.path.exists(AUTOSAVE_PATH)):
            self.prompt.prompt_and_raise_if_not_yes(f"Error found with backup. Autosave did not back up properly. Continue? ")
        if not(os.path.exists(UTILS_PATH)):
            self.prompt.prompt_and_raise_if_not_yes(f"Error found with backup. EPICS_Utils did not back up properly. Continue? ")


        
    @task("Removing old version of IBEX")
    def remove_old_ibex(self):
        """
        Removes older versions of IBEX server, client, genie_python and epics utils
        Returns:

        """
        for path in ALL_INSTALL_DIRECTORIES:
            self._file_utils.remove_tree(path, self.prompt, leave_top_if_link=True)
