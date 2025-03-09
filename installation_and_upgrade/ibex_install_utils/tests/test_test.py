# use the following command in an epic terminal
# .\pythonpath.bat ../../ test.py
# to run the file as a temp fix

import io
from unittest.mock import patch

from ibex_install_utils.progress_bar import ProgressBar


class TestStringMethods:
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_update_progress_bar(self, mockstdout):
        progress_bar = ProgressBar()
        progress_bar.progress = 10
        progress_bar.total = 20
        progress_bar.print()
        expected_output = "\rProgress: [==========          ] 50% (10 / 20)"
        assert mockstdout.getvalue() == expected_output

    # def test_zip_file(self):

    #    BackupTasks('','','','','').zip_file('test','test')
