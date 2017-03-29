from Directory_Operations import ReadConfigFiles

# create instance of 'ReadConfigFiles' as 'filelist' and supply directory to be read
# filelist = ReadConfigFiles("C:/temp/")

filelist = ReadConfigFiles("//ndxvesuvio/c$/Program Files (x86)/STFC ISIS Facility/SECI/Configurations/")

xml_data = filelist.analyse_config_files()

# print xml_data

# concatenates each element in list with newline character, then prints whole string

for item in xml_data:

    print '\n'.join(x for x in item)
    print "Number of VIs: " + str(len(item))
