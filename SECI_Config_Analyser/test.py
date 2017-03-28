from Directory_Operations import ReadConfigFiles

search_path = "C:/temp/"

filelist = ReadConfigFiles()

filenames = filelist.read_directory_contents(search_path)

config_filenames = filelist.extract_config_filenames(filenames)

# converts each element in list to string, concatenates with newline character, then prints whole string

# print '\n'.join([str(x) for x in config_filenames])

xml_data = filelist.analyse_config_files(search_path, config_filenames[1])

print xml_data