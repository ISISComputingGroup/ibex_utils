import io
import os
from unittest.mock import patch, Mock
from ibex_install_utils.tasks.backup_tasks import BackupTasks
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.user_prompt import UserPrompt

EPICS_PATH_BACKUP = os.path.join(BaseTasks._get_backup_dir(),'EPICS', 'VERSION.txt')
PYTHON3_PATH_BACKUP = os.path.join(BaseTasks._get_backup_dir(),'Python3', 'VERSION.txt')
GUI_PATH_BACKUP = os.path.join(BaseTasks._get_backup_dir(),'Client_E4', 'VERSION.txt') 
SETTINGS_PATH = os.path.join(BaseTasks._get_backup_dir(), "Settings")
AUTOSAVE_PATH = os.path.join(BaseTasks._get_backup_dir(), "Autosave")
UTILS_PATH = os.path.join(BaseTasks._get_backup_dir(), 'EPICS_UTILS')

BACKUP_DIRECTORIES = [
    EPICS_PATH_BACKUP, PYTHON3_PATH_BACKUP, GUI_PATH_BACKUP, SETTINGS_PATH, AUTOSAVE_PATH, UTILS_PATH
]

class TestBackupTasks:
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_WHEN_updating_THEN_progress_bar_works(self, mockstdout):
   
        BackupTasks('','','','','').update_progress_bar(10, 20)
        expected_output = '\rProgress: [==========          ] 50% (10/20)'
        assert mockstdout.getvalue() == expected_output
    
    def test_WHEN_verifying_backup_THEN_all_directories_checked(self):
        os.path.exists = Mock()
        prompter = UserPrompt(True, False)
        BackupTasks(prompter,'','','','').backup_checker()

        for dir in BACKUP_DIRECTORIES:
            os.path.exists.assert_any_call(dir)