#use the following command in an epic terminal 
#.\pythonpath.bat ../../ test.py 
#to run the file as a temp fix

import io
from unittest.mock import patch
from ibex_install_utils.tasks.backup_tasks import BackupTasks

class TestStringMethods:
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_update_progress_bar(self, mockstdout):
   
        BackupTasks('','','','','').update_progress_bar(10, 20)
        expected_output = '\rProgress: [==========          ] 50% (10 / 20)'
        assert mockstdout.getvalue() == expected_output

    #def test_zip_file(self):

    #    BackupTasks('','','','','').zip_file('test','test')
