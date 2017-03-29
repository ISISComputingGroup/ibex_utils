from Directory_Operations import ReadConfigFiles

# create instance of 'ReadConfigFiles' as 'filelist' and supply directory to be read
filelist = ReadConfigFiles("C:/temp/")

# converts each element in list to string, concatenates with newline character, then prints whole string

# print '\n'.join([str(x) for x in config_filenames])

xml_data = filelist.analyse_config_files()

# print xml_data