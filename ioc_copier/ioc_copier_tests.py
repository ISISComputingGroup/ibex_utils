import ioc_copier
import unittest
import os
from unittest import mock


class TestIocCopier(unittest.TestCase):

    @mock.patch("builtins.print")
    @mock.patch.object(ioc_copier.sys, "argv", ["ioc_copier"])
    def test_handle_arguments_called_AND_no_arguments_THEN_exit(self, mock_print):
        with self.assertRaises(SystemExit):
            ioc_copier.handle_arguments()
        self.assertEqual(mock_print.call_count, 3)

    @mock.patch("builtins.print")
    @mock.patch.object(ioc_copier.sys, "argv", ["ioc_copier", "test", "test"])
    def test_handle_arguments_called_AND_less_than_4_arguments_THEN_exit(self, mock_print):
        with self.assertRaises(SystemExit):
            ioc_copier.handle_arguments()
        self.assertEqual(mock_print.call_count, 3)

    @mock.patch("builtins.print")
    @mock.patch.object(ioc_copier.sys, "argv", ["ioc_copier", "test", "test", "test", "test", "test"])
    def test_handle_arguments_called_AND_more_than_4_arguments_THEN_exit(self, mock_print):
        with self.assertRaises(SystemExit):
            ioc_copier.handle_arguments()
        self.assertEqual(mock_print.call_count, 3)

    @mock.patch("builtins.print")
    @mock.patch.object(ioc_copier.sys, "argv", ["ioc_copier", "test", "1", "2", "3"])
    def test_handle_arguments_called_AND_more_than_4_arguments_THEN_return_variables(self, mock_print):
        initial_copy, ioc, max_copy, start_copy = ioc_copier.handle_arguments()
        mock_print.assert_not_called()
        self.assertEqual(ioc, "test")
        self.assertEqual(start_copy, 1)
        self.assertEqual(initial_copy, 2)
        self.assertEqual(max_copy, 3)

    @mock.patch("builtins.print")
    @mock.patch.object(ioc_copier.sys, "argv", ["ioc_copier", "-h"])
    def test_help_check_called_AND_h_THEN_exit(self, mock_print):
        with self.assertRaises(SystemExit):
            ioc_copier.help_check()
        self.assertEqual(mock_print.call_count, 8)

    @mock.patch("builtins.print")
    def test_help_check_called_AND_no_h_THEN_no_prints(self, mock_print):
        ioc_copier.help_check()
        mock_print.assert_not_called()

    def test_replace_text_called_THEN_replace_text_start_in_text_with_current(self):
        test_text = ["test_02", "IOC_02", "IOC-02", "test_2", "IOC_2", "IOC-2", "RAMPFILELIST2", "RAMPFILELIST02"]
        check_text = ["test_03", "IOC_03", "IOC-03", "test_3", "IOC_3", "IOC-3",  "RAMPFILELIST3", "RAMPFILELIST03"]
        ioc_copier.replace_text(test_text, 2, 3, "test")
        self.assertEqual(check_text, test_text)

    def test_replace_text_called_AND_different_length_THEN_replace_text_start_in_text_with_current(self):
        test_text = ["test_02", "IOC_02", "IOC-02", "test_2", "IOC_2", "IOC-2"]
        check_text = ["test_13", "IOC_13", "IOC-13", "test_13", "IOC_13", "IOC-13"]
        ioc_copier.replace_text(test_text, 2, 13, "test")
        self.assertEqual(check_text, test_text)

    def test_replace_text_called_AND_contains_math_THEN_replace_text_does_not_break_math(self):
        test_text = ["n = 2+5", "test_02", "02+5"]
        check_text = ["n = 2+5", "test_13", "02+5"]
        ioc_copier.replace_text(test_text, 2, 13, "test")
        self.assertEqual(check_text, test_text)

    @mock.patch("os.rename")
    def test_rename_files_called_AND_underscore_in_name_THEN_files_renamed(self, mock_rename):
        root_folder = os.getcwd()
        rename = "IOC_02"
        ioc = "test"
        start_copy_padded = "02"
        current_copy_padded = "13"
        start_path = os.path.join(root_folder, rename)
        end_path = os.path.join(root_folder, "IOC_13")

        ioc_copier.rename_files(root_folder, rename, ioc, start_copy_padded, current_copy_padded)
        mock_rename.assert_called_with(start_path, end_path)

    @mock.patch("os.rename")
    def test_rename_files_called_AND_hyphen_in_name_THEN_files_renamed(self, mock_rename):
        root_folder = os.getcwd()
        rename = "IOC-02"
        ioc = "test"
        start_copy_padded = "02"
        current_copy_padded = "13"
        start_path = os.path.join(root_folder, rename)
        end_path = os.path.join(root_folder, "IOC-13")

        ioc_copier.rename_files(root_folder, rename, ioc, start_copy_padded, current_copy_padded)
        mock_rename.assert_called_with(start_path, end_path)

    @mock.patch("os.rename")
    def test_rename_files_called_AND_ioc_name_in_name_THEN_files_renamed(self, mock_rename):
        root_folder = os.getcwd()
        rename = "test_02"
        ioc = "test"
        start_copy_padded = "02"
        current_copy_padded = "13"
        start_path = os.path.join(root_folder, rename)
        end_path = os.path.join(root_folder, "test_13")

        ioc_copier.rename_files(root_folder, rename, ioc, start_copy_padded, current_copy_padded)
        mock_rename.assert_called_with(start_path, end_path)

    @mock.patch("os.rename")
    def test_rename_files_called_AND_name_does_not_contain_start_THEN_files_not_renamed(self, mock_rename):
        root_folder = os.getcwd()
        rename = "test_05"
        ioc = "test"
        start_copy_padded = "02"
        current_copy_padded = "13"

        ioc_copier.rename_files(root_folder, rename, ioc, start_copy_padded, current_copy_padded)
        mock_rename.assert_not_called()

    @mock.patch("os.rename")
    def test_rename_files_called_AND_name_does_not_contain_ioc_or_name_THEN_files_not_renamed(self, mock_rename):
        root_folder = os.getcwd()
        rename = "test_02"
        ioc = "not_test"
        start_copy_padded = "02"
        current_copy_padded = "13"

        ioc_copier.rename_files(root_folder, rename, ioc, start_copy_padded, current_copy_padded)
        mock_rename.assert_not_called()

    @mock.patch("ioc_copier.copytree")
    def test_copy_folder_AND_valid_ioc_name_and_format_THEN_correct_copy(self, mock_copy):
        file_format = "{}App"
        ioc_name = "test"
        zero_padded_current_copy = "03"
        path = os.path.join(os.getcwd(), file_format.format(f"{ioc_name}-{zero_padded_current_copy}"))
        result = ioc_copier.copy_folder(file_format, ioc_name, zero_padded_current_copy, "02")
        self.assertEqual(path, result)
        mock_copy.assert_called()

    @mock.patch("ioc_copier.copy_folder")
    @mock.patch("ioc_copier.rename_files")
    @mock.patch("ioc_copier.os.walk")
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="test_02\nIOC-2")
    def test_copy_loop_AND_valid_parameters_THEN_loops_to_max_calling_copies_AND_writes_to_file(self, mock_open, mock_walk, mock_rename, mock_folder):
        start_copy = 2
        initial_copy = 3
        max_copy = 5
        file_format = "{}"
        ioc = "test"
        mock_walk.return_value = [('/iocBoot', ('subfolder_02',), ('test_02.db',)),
                                  ('/iocBoot/subfolder_02', (), ('test_02.cpp', 'test_02.proto'))]
        ioc_copier.copy_loop(start_copy, initial_copy, max_copy, file_format, ioc)
        self.assertEqual(mock_folder.call_count, 3)
        mock_folder.assert_called_with("{}", "test-IOC", "05", "02")
        self.assertEqual(mock_open.call_count, 18)
        mock_open.assert_called_with("/iocBoot/subfolder_02\\test_02.proto", "w")
        file_handle = mock_open.return_value.__enter__.return_value
        file_handle.writelines.assert_called_with(["test_05\n", "IOC-5"])
        mock_rename.assert_called_with("/iocBoot/subfolder_02", "test_02.proto", "test", "02", "05")

    @mock.patch("ioc_copier.copy_folder")
    @mock.patch("ioc_copier.rename_files")
    @mock.patch("ioc_copier.os.walk")
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="test_08\nIOC-8")
    def test_copy_loop_AND_change_num_digits_THEN_writes_to_file(self, mock_open, mock_walk, mock_rename, mock_folder):
        start_copy = 8
        initial_copy = 9
        max_copy = 10
        file_format = "{}"
        ioc = "test"
        mock_walk.return_value = [('/iocBoot', ('subfolder_08',), ('test_08.db',)),
                                  ('/iocBoot/subfolder_08', (), ('test_08.cpp', 'test_08.proto'))]
        ioc_copier.copy_loop(start_copy, initial_copy, max_copy, file_format, ioc)
        self.assertEqual(mock_folder.call_count, 2)
        mock_folder.assert_called_with("{}", "test-IOC", 10, "08")
        self.assertEqual(mock_open.call_count, 12)
        mock_open.assert_called_with("/iocBoot/subfolder_08\\test_08.proto", "w")
        file_handle = mock_open.return_value.__enter__.return_value
        file_handle.writelines.assert_called_with(["test_10\n", "IOC-10"])
        mock_rename.assert_called_with("/iocBoot/subfolder_08", "test_08.proto", "test", "08", 10)

    @mock.patch("ioc_copier.copy_folder")
    @mock.patch("ioc_copier.rename_files")
    @mock.patch("ioc_copier.os.walk")
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="test_02\nIOC-2")
    def test_copy_loop_AND_valid_parameters_AND_exe_THEN_does_not_edit_exe(self, mock_open, mock_walk, mock_rename, mock_folder):
        start_copy = 2
        initial_copy = 3
        max_copy = 5
        file_format = "{}"
        ioc = "test"
        mock_walk.return_value = [('/iocBoot', ('subfolder_02',), ('test_02.db',)),
                                  ('/iocBoot/subfolder_02', (), ('test_02.cpp', 'test_02.exe'))]
        ioc_copier.copy_loop(start_copy, initial_copy, max_copy, file_format, ioc)
        self.assertEqual(mock_folder.call_count, 3)
        mock_folder.assert_called_with("{}", "test-IOC", "05", "02")
        self.assertEqual(mock_open.call_count, 12)
        mock_open.assert_called_with("/iocBoot/subfolder_02\\test_02.cpp", "w")
        file_handle = mock_open.return_value.__enter__.return_value
        file_handle.writelines.assert_called_with(["test_05\n", "IOC-5"])
        mock_rename.assert_called_with("/iocBoot/subfolder_02", "test_02.cpp", "test", "02", "05")

    @mock.patch("ioc_copier.copy_folder")
    @mock.patch("ioc_copier.rename_files")
    @mock.patch("ioc_copier.os.walk")
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="test_02\nIOC-2")
    def test_copy_loop_AND_valid_parameters_AND_pdb_THEN_does_not_edit_pdb(self, mock_open, mock_walk, mock_rename,
                                                                           mock_folder):
        start_copy = 2
        initial_copy = 3
        max_copy = 5
        file_format = "{}"
        ioc = "test"
        mock_walk.return_value = [('/iocBoot', ('subfolder_02',), ('test_02.db',)),
                                  ('/iocBoot/subfolder_02', (), ('test_02.cpp', 'test_02.pdb'))]
        ioc_copier.copy_loop(start_copy, initial_copy, max_copy, file_format, ioc)
        self.assertEqual(mock_folder.call_count, 3)
        mock_folder.assert_called_with("{}", "test-IOC", "05", "02")
        self.assertEqual(mock_open.call_count, 12)
        mock_open.assert_called_with("/iocBoot/subfolder_02\\test_02.cpp", "w")
        file_handle = mock_open.return_value.__enter__.return_value
        file_handle.writelines.assert_called_with(["test_05\n", "IOC-5"])
        mock_rename.assert_called_with("/iocBoot/subfolder_02", "test_02.cpp", "test", "02", "05")

    @mock.patch("ioc_copier.copy_folder")
    @mock.patch("ioc_copier.rename_files")
    @mock.patch("ioc_copier.os.walk")
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="test_02\nIOC-2")
    def test_copy_loop_AND_valid_parameters_AND_obj_THEN_does_not_edit_obj(self, mock_open, mock_walk, mock_rename,
                                                                           mock_folder):
        start_copy = 2
        initial_copy = 3
        max_copy = 5
        file_format = "{}"
        ioc = "test"
        mock_walk.return_value = [('/iocBoot', ('subfolder_02',), ('test_02.db',)),
                                  ('/iocBoot/subfolder_02', (), ('test_02.cpp', 'test_02.obj'))]
        ioc_copier.copy_loop(start_copy, initial_copy, max_copy, file_format, ioc)
        self.assertEqual(mock_folder.call_count, 3)
        mock_folder.assert_called_with("{}", "test-IOC", "05", "02")
        self.assertEqual(mock_open.call_count, 12)
        mock_open.assert_called_with("/iocBoot/subfolder_02\\test_02.cpp", "w")
        file_handle = mock_open.return_value.__enter__.return_value
        file_handle.writelines.assert_called_with(["test_05\n", "IOC-5"])
        mock_rename.assert_called_with("/iocBoot/subfolder_02", "test_02.cpp", "test", "02", "05")

    @mock.patch("ioc_copier.copy_folder")
    @mock.patch("ioc_copier.rename_files")
    @mock.patch("ioc_copier.os.walk")
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="test_02\nIOC-2")
    def test_copy_loop_AND_valid_parameters_AND_empty_THEN_copy_folder_AND_end(self, mock_open, mock_walk, mock_rename, mock_folder):
        start_copy = 2
        initial_copy = 3
        max_copy = 5
        file_format = "{}"
        ioc = "test"
        mock_walk.return_value = [('/iocBoot', (), ())]
        ioc_copier.copy_loop(start_copy, initial_copy, max_copy, file_format, ioc)
        self.assertEqual(mock_folder.call_count, 3)
        mock_folder.assert_called_with("{}", "test-IOC", "05", "02")
        mock_open.assert_not_called()
        file_handle = mock_open.return_value.__enter__.return_value
        file_handle.writelines.assert_not_called()
        mock_rename.assert_not_called()

    @mock.patch("ioc_copier.copy_folder")
    @mock.patch("ioc_copier.rename_files")
    @mock.patch("ioc_copier.os.walk")
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="test_02\nIOC-2")
    def test_copy_loop_AND_max_is_start_AND_empty_THEN_copy_folder_AND_end(self, mock_open, mock_walk, mock_rename,
                                                                               mock_folder):
        start_copy = 2
        initial_copy = 3
        max_copy = 2
        file_format = "{}"
        ioc = "test"
        mock_walk.return_value = [('/iocBoot', (), ())]
        ioc_copier.copy_loop(start_copy, initial_copy, max_copy, file_format, ioc)
        mock_folder.assert_not_called()
        mock_open.assert_not_called()
        file_handle = mock_open.return_value.__enter__.return_value
        file_handle.writelines.assert_not_called()
        mock_rename.assert_not_called()
