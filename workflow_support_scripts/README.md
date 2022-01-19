# Workflow Support Scripts

### Calibration Files' Location: 

 `http://control-svcs.isis.cclrc.ac.uk/gitroot/instconfigs/common.git`

This repo should be cloned with:

 `git clone http://control-svcs.isis.cclrc.ac.uk/gitroot/instconfigs/common.git C:\Instrument\Settings\config\common`

### Converting Files

To convert files, cd to the directory that files are located and run `file_converter` script: `%PYTHON3% file_converter.py -i <input_folder> -o <output_folder>` 

**Note: Make sure that input folder does NOT contain both .dat and .curve calibration files for the same sensor. In this case, create a temporary folder, copy-paste desired file and set the folder as input_folder when running the script. 

After finishing converting, please check files and then copy and commit to the correct folder in `C:\Instrument\Settings\config\common`

### WIKI Page:

 `https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Calibration-Files/`