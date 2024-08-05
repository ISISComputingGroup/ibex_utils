# use the following command in an epic terminal
# python -m pytest
# to run the file as a temp fix

import io
from unittest.mock import Mock, patch


class TestDummyTest:
    @patch("sys.stdout", new_callable=io.StringIO)  # for patching mocked methods into tests
    def test_WHEN_true_THEN_true(self, mocked_stdout):
        mocked_func = Mock()

        mocked_func("hello mr.mock")
        mocked_func.assert_called_with("hello mr.mock")

        print("hello")
        assert mocked_stdout.getvalue() == "hello\n"
