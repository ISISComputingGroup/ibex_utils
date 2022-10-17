import ioc_copier
import unittest
import os
from parameterized import parameterized
from unittest import mock


class TestIocCopier(unittest.TestCase):

    @mock.patch("builtins.print")
    def test_check_valid_ioc_to_copy_AND_no_st_common_THEN_exit(self, mock_print):
        with self.assertRaises(SystemExit):
            ioc_copier.check_valid_ioc_to_copy("test")
        self.assertEqual(mock_print.call_count, 1)

    @mock.patch("builtins.print")
    @mock.patch("ioc_copier.os.path.exists")
    def test_check_valid_ioc_to_copy_AND_st_common_AND_no_seq_THEN_not_exit(self, mock_exists, mock_print):
        mock_open = mock.mock_open(read_data="test")
        mock_exists.return_value = True
        with mock.patch("builtins.open", mock_open):
            ioc_copier.check_valid_ioc_to_copy("test")
        self.assertEqual(mock_print.call_count, 0)

    @mock.patch("builtins.print")
    @mock.patch("ioc_copier.os.path.exists")
    def test_check_valid_ioc_to_copy_AND_st_common_AND_seq_THEN_exit(self, mock_exists, mock_print):
        mock_open = mock.mock_open(read_data="seq ")
        mock_exists.return_value = True
        with mock.patch("builtins.open", mock_open):
            with self.assertRaises(SystemExit):
                ioc_copier.check_valid_ioc_to_copy("test")
        self.assertEqual(mock_print.call_count, 1)

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
        initial_copy, ioc, max_copy = ioc_copier.handle_arguments()
        mock_print.assert_not_called()
        self.assertEqual(ioc, "test")
        self.assertEqual(ioc_copier.START_COPY, 1)
        self.assertEqual(initial_copy, 2)
        self.assertEqual(max_copy, 3)

    @mock.patch("builtins.print")
    @mock.patch.object(ioc_copier.sys, "argv", ["ioc_copier", "-h"])
    def test_help_check_called_AND_h_THEN_exit(self, mock_print):
        with self.assertRaises(SystemExit):
            ioc_copier.help_check()
        self.assertEqual(mock_print.call_count, 9)

    @mock.patch("builtins.print")
    def test_help_check_called_AND_no_h_THEN_no_prints(self, mock_print):
        ioc_copier.help_check()
        mock_print.assert_not_called()

    @parameterized.expand([
        ("", ["test_02", "IOC_02", "IOC-02", "test_2", "IOC_2", "IOC-2", "RAMPFILELIST2", "RAMPFILELIST02"],
         ["test_03", "IOC_03", "IOC-03", "test_3", "IOC_3", "IOC-3",  "RAMPFILELIST3", "RAMPFILELIST03"], 3, 0),
        ("handle_length",["test_02", "IOC_02", "IOC-02", "test_2", "IOC_2", "IOC-2"],
         ["test_13", "IOC_13", "IOC-13", "test_13", "IOC_13", "IOC-13"], 13, 0),
        ("handle_math",["n = 2+5", "test_02", "02+5"], ["n = 2+5", "test_13", "02+5"], 13, 0),
        ("handle_asub", ["record(aSub"], ["record(aSub"], 13, 1),
        ("handle_asub2", ["record(aSub", "record(aSub"], ["record(aSub", "record(aSub"], 13, 1)
    ])
    @mock.patch("builtins.print")
    def test_replace_text_called_THEN_replace_text_start_in_text_with_current(self, _, test_text, check_text, copy,
                                                                              print_called, mock_print):
        ioc_copier.START_COPY = 2
        ioc_copier.current_copy = copy
        ioc_copier.padded_start_copy = ioc_copier.add_zero_padding(ioc_copier.START_COPY)
        ioc_copier.padded_current_copy = ioc_copier.add_zero_padding(ioc_copier.current_copy)
        ioc_copier.asub_record = False
        test_text = ioc_copier.replace_text(test_text, "test")
        self.assertEqual(check_text, test_text)
        self.assertEqual(mock_print.call_count, print_called)

    @parameterized.expand([
        ("_with_cmd", 1, "st.cmd",
         "test_01\n< iocBoot/ioctest-IOC-01/st-common.cmd", ["test_03\n", "< iocBoot/ioctest-IOC-01/st-common.cmd"], 0),
        ("_with_cmd_not_1", 2, "st.cmd",
         "test_02\n< iocBoot/ioctest-IOC-02/st-common.cmd", ["test_03\n", "< iocBoot/ioctest-IOC-03/st-common.cmd"], 0),
        ("_with_src_make", 1, "App\src\Makefile",
         "test_01\ntest-IOC-01App/src/build.mak\n###-IOC-01 and delete build.mak from",
         ["test_03\n", "test-IOC-01App/src/build.mak\n", "###-IOC-01 and delete build.mak from"], 0),
        ("_with_src_make_not_1", 2, "App\src\Makefile",
         "test_02\ntest-IOC-02App/src/build.mak\n###-IOC-02 and delete build.mak from",
         ["test_03\n", "test-IOC-02App/src/build.mak\n", "###-IOC-02 and delete build.mak from"], 0),
        ("_with_db_make", 1, "App\Db\Makefile", "", [], 1),
        ("_with_db_make_not_1", 2, "App\Db\Makefile", "", [], 0),
    ])
    @mock.patch("ioc_copier.remove_db_plus")
    def test_get_file_text_called_THEN_handle_all_casses(self, _, start, file, read, result, comment, mock_comment):
        mock_open = mock.mock_open(read_data=read)
        ioc_copier.START_COPY = start
        ioc_copier.current_copy = 3
        ioc_copier.padded_start_copy = ioc_copier.add_zero_padding(ioc_copier.START_COPY)
        ioc_copier.padded_current_copy = ioc_copier.add_zero_padding(ioc_copier.current_copy)
        with mock.patch("builtins.open", mock_open):
            got = ioc_copier.get_file_text(file, "test", "root")

            self.assertEqual(got, result)
        self.assertEqual(mock_comment.call_count, comment)

    @parameterized.expand([
        ("_remove", ["DB += test.db"], []),
        ("_do_not_remove", ["test"], ["test"]),
        ("_missing_dot", ["DB += test"], ["DB += test"]),
        ("_missing_DB", ["+= test.db"], ["+= test.db"]),
    ])
    def test_remove_db_plus_makefile_THEN_comments_correct_lines(self, _, input, output):
        self.assertEqual(ioc_copier.remove_db_plus(input), output)


    @parameterized.expand([
        ("_with_underscore", "IOC_02", "IOC_13"),
        ("_with_hyphen", "IOC-02", "IOC-13"),
        ("with_ioc_name", "test_02", "test_13"),
    ])
    @mock.patch("os.rename")
    def test_rename_files_called_in_name_THEN_files_renamed(self, _, rename, check, mock_rename):
        root_folder = os.getcwd()
        ioc = "test"
        ioc_copier.padded_start_copy = "02"
        ioc_copier.padded_current_copy = "13"
        start_path = os.path.join(root_folder, rename)
        end_path = os.path.join(root_folder, check)

        ioc_copier.rename_files(root_folder, rename, ioc)
        mock_rename.assert_called_with(start_path, end_path)

    @parameterized.expand([
        ("_no_start_to_replace", "test_05", "test"),
        ("_no_ioc_or_name_to_replace", "test_02", "not_test"),
    ])
    @mock.patch("os.rename")
    def test_rename_files_called_THEN_files_not_renamed(self, _, rename, ioc, mock_rename):
        root_folder = os.getcwd()
        ioc_copier.padded_start_copy = "02"
        ioc_copier.padded_current_copy = "13"

        ioc_copier.rename_files(root_folder, rename, ioc)
        mock_rename.assert_not_called()

    @mock.patch("ioc_copier.copytree")
    def test_copy_folder_AND_valid_ioc_name_and_format_THEN_correct_copy(self, mock_copy):
        file_format = "{}App"
        ioc_name = "test"
        ioc_copier.padded_start_copy = "02"
        ioc_copier.padded_current_copy = "03"
        path = os.path.join(os.getcwd(), file_format.format(f"{ioc_name}-{ioc_copier.padded_current_copy}"))
        result = ioc_copier.copy_folder(file_format, ioc_name)
        self.assertEqual(path, result)
        mock_copy.assert_called()

    @parameterized.expand([
        ("_valid_parameters", 2, 3,5,3,18, "cpp"),
        ("_change_num_digits", 8, 9, 11, 3, 18, "cpp"),
        ("_does_not_edit_exe", 2, 3, 5, 3, 12, "exe"),
        ("_does_not_edit_pdb", 2, 3, 5, 3, 12, "pdb"),
        ("_does_not_edit_obj", 2, 3, 5, 3, 12, "obj"),

    ])
    @mock.patch("ioc_copier.copy_folder")
    @mock.patch("ioc_copier.rename_files")
    @mock.patch("ioc_copier.os.walk")
    def test_copy_loop_THEN_writes_to_file(self, _, start_copy, initial_copy, max_copy, folder_count, open_count,
                                           file_type, mock_walk, mock_rename, mock_folder):

        ioc_copier.START_COPY = start_copy
        padded_start_copy = ioc_copier.add_zero_padding(start_copy)
        padded_max_copy = ioc_copier.add_zero_padding(max_copy)
        file_format = "{}"
        ioc = "test"
        mock_open = mock.mock_open(read_data=f"test_{padded_start_copy}\nIOC-{start_copy}")
        with mock.patch("builtins.open", mock_open):
            mock_walk.return_value = [('/iocBoot', (f'subfolder_{padded_start_copy}',), (f'test_{padded_start_copy}.db',)),
                                      (f'/iocBoot/subfolder_{padded_start_copy}', (),
                                       (f'test_{padded_start_copy}.{file_type}',  f'test_{padded_start_copy}.proto'))]
            ioc_copier.copy_loop(initial_copy, max_copy, file_format, ioc)
            self.assertEqual(mock_folder.call_count, folder_count)
            mock_folder.assert_called_with("{}", "test-IOC")
            self.assertEqual(mock_open.call_count, open_count)
            mock_open.assert_called_with(f"/iocBoot/subfolder_{padded_start_copy}\\test_{padded_start_copy}.proto", "w")
            file_handle = mock_open.return_value.__enter__.return_value
            file_handle.writelines.assert_called_with([f"test_{padded_max_copy}\n", f"IOC-{max_copy}"])
            mock_rename.assert_called_with(f"/iocBoot/subfolder_{padded_start_copy}",
                                           f"test_{padded_start_copy}.proto", "test")

    @mock.patch("ioc_copier.copy_folder")
    @mock.patch("ioc_copier.rename_files")
    @mock.patch("ioc_copier.os.walk")
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="test_02\nIOC-2")
    def test_copy_loop_AND_valid_parameters_AND_empty_THEN_copy_folder_AND_end(self, mock_open, mock_walk, mock_rename, mock_folder):
        ioc_copier.START_COPY = 2
        initial_copy = 3
        max_copy = 5
        file_format = "{}"
        ioc = "test"
        mock_walk.return_value = [('/iocBoot', (), ())]
        ioc_copier.copy_loop(initial_copy, max_copy, file_format, ioc)
        self.assertEqual(mock_folder.call_count, 3)
        mock_folder.assert_called_with("{}", "test-IOC")
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
        ioc_copier.START_COPY = 2
        initial_copy = 3
        max_copy = 2
        file_format = "{}"
        ioc = "test"
        mock_walk.return_value = [('/iocBoot', (), ())]
        ioc_copier.copy_loop(initial_copy, max_copy, file_format, ioc)
        mock_folder.assert_not_called()
        mock_open.assert_not_called()
        file_handle = mock_open.return_value.__enter__.return_value
        file_handle.writelines.assert_not_called()
        mock_rename.assert_not_called()

    @parameterized.expand([
        ("_length_1_add_0", "3", "03"),
        ("_length_2_no_0", "13", "13"),
        ("_length_2_plus_no_0", "180", "180"),
    ])
    def test_add_zero_padding(self, _, initial, check):
        self.assertEqual(ioc_copier.add_zero_padding(initial), check)


if __name__ == '__main__':
    unittest.main()
