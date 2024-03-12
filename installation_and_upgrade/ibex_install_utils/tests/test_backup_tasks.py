import io
import os
from unittest.mock import patch, Mock
from ibex_install_utils.tasks.backup_tasks import BackupTasks
from ibex_install_utils.progress_bar import ProgressBar
from ibex_install_utils.tasks import BaseTasks
from ibex_install_utils.user_prompt import UserPrompt

class TestBackupTasks:
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_WHEN_updating_THEN_progress_bar_works(self, mockstdout):
        progress_bar = ProgressBar()
        progress_bar.progress = 10
        progress_bar.total = 20
        progress_bar.print()
        expected_output = '\rProgress: [==========          ] 50% (10 / 20)'
        assert mockstdout.getvalue() == expected_output
    
    def test_WHEN_verifying_backup_THEN_all_directories_checked(self):
        backup_path = 'C:\\Data\\old\\today\\'

        def mock_get_backup_dir():
            return backup_path
        
        BaseTasks._get_backup_dir = Mock(side_effect=mock_get_backup_dir)
        os.path.exists = Mock()
        prompter = UserPrompt(True, False)

        # For the purpose of testing, we don't need to properly set up the BackupTasks() constructor 
        # method, so '' is an empty argument to placehold
        BackupTasks(prompter,'','','','').backup_checker()

        for dir in [
            f'{backup_path}EPICS\\VERSION.txt',
            f'{backup_path}Python3\\VERSION.txt',
            f'{backup_path}Client_E4\\VERSION.txt',
            f'{backup_path}Settings',
            f'{backup_path}Autosave',
            f'{backup_path}EPICS_UTILS'
        ]:
            os.path.exists.assert_any_call(dir)
