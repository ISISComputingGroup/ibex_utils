# read in directory listing

# create lists of *.conf and *.comp files from directory

# for each file, search for lines containing ".vi" and add to list

# remove duplicates from list

# process lines to remove superfluous text (i.e. full path)


class ReadConfigFiles(object):

    """Reads SECI configuration files and extracts VI names"""""

    def __init__(self, search_path):
        # create lists for filenames and initialise to empty lists

        self.full_path = search_path
        self.directory_contents = list()
        self.config_filenames = list()
        self.comp_filenames = list()
        self.vi_list = list()

    def read_directory_contents(self,):
        # read filenames into list

        from os import listdir

        directory_contents = listdir(self.full_path)

        return directory_contents

    def extract_config_filenames(self, directory_contents):
        # extract SECI config & component filenames

        import fnmatch

        for filename in directory_contents:

            if fnmatch.fnmatch(filename, '*.conf'):

                self.config_filenames.append(filename)

            elif fnmatch.fnmatch(filename, '*.comp'):

                self.comp_filenames.append(filename)

        return self.config_filenames, self.comp_filenames

    def analyse_config_files(self, config_filenames):
        # read XML data of files

        import xml.etree.ElementTree as ET

        vi_list = list()

        for filename in config_filenames:

            filename_and_path = self.full_path + filename

            print "File being processed: " + filename_and_path

            tree = ET.parse(filename_and_path)

            root = tree.getroot()

            for child in root.iter('FilePath'):

                vi_path = ET.tostring(child, encoding=None, method="text")

                # print vi_path

                vi_list.append(vi_path.strip())

        print vi_list

        return
