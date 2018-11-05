# 1. read in directory listing
# 2. create lists of *.conf and *.comp files from directory
# 3. for each file, parse XML for required tag and add value to list
# 4. remove duplicates from list

from os import listdir
from fnmatch import fnmatch
import xml.etree.ElementTree as ET


class ReadConfigFiles(object):
    """
    Reads SECI configuration files and extracts VI names
    """

    def __init__(self, search_path):
        """
        create lists for filenames and initialise to empty lists
        call methods for reading directory contents and searching for config filenames
        :param search_path: the search path for files 
        """

        self.full_path = search_path
        self.directory_contents = listdir(self.full_path)
        self.config_filenames = []
        self.comp_filenames = []
        self.vi_list = []
        self._extract_config_filenames()

    def _extract_config_filenames(self):
        """
        extract SECI config (*.conf) & component (*.comp) filenames
        add to separate lists
        """

        for filename in self.directory_contents:

            if fnmatch(filename, '*.conf'):

                self.config_filenames.append(filename)

            elif fnmatch(filename, '*.comp'):

                self.comp_filenames.append(filename)

    def _parse_vis_from_files(self, filenames):
        """
        extracts VI names and paths from config files
        :param filenames: list of filenames to process 
        :return: vis_in_files: list of VIs with fullpaths
        """

        vis_in_files = []

        for filename in filenames:

            filename_and_path = self.full_path + filename
            vis_in_file = self._parse_file(filename_and_path)
            vis_in_files.extend(vis_in_file)

        return vis_in_files

    def _parse_file(self, filename_and_path):
        """
        reads XML file and creates list of values for "FilePath" tag
        :param filename_and_path: absolute path of file to be parsed
        :return: vis_in_file: list of  VIs in file
        """

        # print "File being processed: " + filename_and_path

        vis_in_file = []
        tree = ET.parse(filename_and_path)
        root = tree.getroot()
        for child in root.iter('FilePath'):

            vi_path = ET.tostring(child, encoding=None, method="text")
            vis_in_file.append(vi_path.strip())

        return vis_in_file

    def _remove_duplicates(self, input_list):
        """
        remove duplicates from list, then sort alphabetically
        :param input_list: input list
        :return: output_list: original list with duplicates removed
        """

        # maintain list of "encountered" items in dummy list
        # if item not in this list, add item to it and to output list

        output_list = []
        encountered = set()

        for item in input_list:
            item = str.lower(item)

            if item not in encountered:
                output_list.append(item)
                encountered.add(item)

        # sort alphabetically

        output_list.sort()

        return output_list

    def analyse_config_files(self):
        """
        call methods to process files
        :return: config_vis: list containing absolute paths of VIs within SECI config file
        :return: comp_vis:   list containing absolute paths of VIs within SECI sub-config file
        """

        config_vis = self._remove_duplicates(self._parse_vis_from_files(self.config_filenames))
        comp_vis   = self._remove_duplicates(self._parse_vis_from_files(self.comp_filenames))

        # print "Config VIs"
        # print "\n".join(config_vis)
        #
        # print "Component VIs"
        # print "\n".join(comp_vis)

        return config_vis, comp_vis
