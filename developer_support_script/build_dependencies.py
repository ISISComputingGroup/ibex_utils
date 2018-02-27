"""
Utility to help create build dependencies
"""

import argparse

import os
import re


# lines which indicate what should be replaced in the release file
FIRST_OLD_RELEASE_LINE = "include $(TOP)/../../../configure/MASTER_RELEASE"
RELEASE_LINES_TO_IGNORE = [
    "# top level master release and local private options",
    "-include $(TOP)/../../../configure/MASTER_RELEASE.$(EPICS_HOST_ARCH)",
    "-include $(TOP)/../../../configure/MASTER_RELEASE.private",
    "-include $(TOP)/../../../configure/MASTER_RELEASE.private.$(EPICS_HOST_ARCH)"]
FIRST_NEW_LINE = "# START OF AUTO GENERATED DEPENDENCIES"
LAST_NEW_LINE = "# END OF AUTO GENERATED DEPENDENCIES"

# Dependencies found in the makefile and what should be included in the release file
KNOWN_DEPENDENCIES = {
    "$(EPICS_BASE_IOC_LIBS)": "",
    "$(MYSQLLIB)": "MYSQL=$(SUPPORT)/MySQL/master",
    "SM300Motor": "MOTOR=$(SUPPORT)/motor/master",
    "SM300Motor.dbd": "MOTOR=$(SUPPORT)/motor/master",
    "TinyXML": "TINYXML=$(SUPPORT)/TinyXML/master",
    "aaiRecord.dbd": "",
    "aaoRecord.dbd": "",
    "asSupport.dbd": "AUTOSAVE=$(SUPPORT)/autosave/master",
    "asubFunctions": "ASUBFUNCTIONS=$(SUPPORT)/asubFunctions/master",
    "asubFunctions.dbd": "ASUBFUNCTIONS=$(SUPPORT)/asubFunctions/master",
    "asyn": "ASYN=$(SUPPORT)/asyn/master\nONCRPC=$(SUPPORT)/oncrpc/master",
    "asyn.dbd": "ASYN=$(SUPPORT)/asyn/master\nONCRPC=$(SUPPORT)/oncrpc/master",
    "asynRecord.dbd": "ASYN=$(SUPPORT)/asyn/master",
    "asynRegistrars.dbd": "STREAMDEVICE=$(SUPPORT)/StreamDevice/master",
    "axis.dbd": "AXIS=$(SUPPORT)/axis/master",
    "autosave": "AUTOSAVE=$(SUPPORT)/autosave/master",
    "base.dbd": "",
    "busy": "BUSY=$(SUPPORT)/busy/master",
    "busySupport.dbd": "BUSY=$(SUPPORT)/busy/master",
    "ca": "",
    "caPutLog": "CAPUTLOG=$(SUPPORT)/caPutLog/master",
    "caPutLog.dbd": "CAPUTLOG=$(SUPPORT)/caPutLog/master",
    "calc": "CALC=$(SUPPORT)/calc/master",
    "calcSupport.dbd": "CALC=$(SUPPORT)/calc/master",
    "Com": "",
    "cmdButtonsSupport": "SNCSEQ=$(SUPPORT)/seq/master",
    "demoSupport": "SNCSEQ=$(SUPPORT)/seq/master",
    "$(COMMON_DIR)/vxTestHarnessRegistrars.dbd": "",
    "devIocStats": "DEVIOCSTATS=$(SUPPORT)/devIocStats/master",
    "devIocStats.dbd": "DEVIOCSTATS=$(SUPPORT)/devIocStats/master",
    "devSequencer.dbd": "SNCSEQ=$(SUPPORT)/seq/master",
    "devSoftMotor.dbd": "MOTOR=$(SUPPORT)/motor/master",
    "drvAsynIPPort.dbd": "ASYN=$(SUPPORT)/asyn/master",
    "drvAsynSerialPort.dbd": "ASYN=$(SUPPORT)/asyn/master",
    "easySQLite": "SQLITE=$(SUPPORT)/sqlite/master",
    "FileServer": "FILESERVER=$(SUPPORT)/FileServer/master",
    "icpconfig": "ICPCONFIG=$(SUPPORT)/icpconfig/master",
    "icpconfig.dbd": "ICPCONFIG=$(SUPPORT)/icpconfig/master",
    "libjson": "LIBJSON=$(SUPPORT)/libjson/master",
    "lvDCOM": "LVDCOM=$(ISISSUPPORT)/lvDCOM/master",
    "lvDCOM.dbd": "LVDCOM=$(ISISSUPPORT)/lvDCOM/master",
    "motionSetPoints": "MOTIONSETPOINTS=$(SUPPORT)/motionSetPoints/master",
    "motionSetPoints.dbd": "MOTIONSETPOINTS=$(SUPPORT)/motionSetPoints/master",
    "motor": "MOTOR=$(SUPPORT)/motor/master",
    "motorSimSupport": "MOTOR=$(SUPPORT)/motor/master",
    "motorSimSupport.dbd": "MOTOR=$(SUPPORT)/motor/master",
    "motorSupport.dbd": "MOTOR=$(SUPPORT)/motor/master",
    "optics": "OPTICS=$(SUPPORT)/optics/master",
    "pcre": "PCRE=$(SUPPORT)/pcre/master",
    "pcrecpp": "PCRE=$(SUPPORT)/pcre/master",
    "pixelman": "PIXELMAN=$(SUPPORT)/pixelman/master",
    "pixelman.dbd": "PIXELMAN=$(SUPPORT)/pixelman/master",
    "pvdump_dummy": "PVDUMP=$(SUPPORT)/pvdump/master",
    "pugixml": "PUGIXML=$(SUPPORT)/pugixml/master",
    "pv": "SNCSEQ=$(SUPPORT)/seq/master",
    "pvdump": "PVDUMP=$(SUPPORT)/pvdump/master",
    "pvdump.dbd": "PVDUMP=$(SUPPORT)/pvdump/master",
    "sampleChanger": "SAMPLECHANGER=$(SUPPORT)/sampleChanger/master",
    "sampleChanger.dbd": "SAMPLECHANGER=$(SUPPORT)/sampleChanger/master",
    "seq": "SNCSEQ=$(SUPPORT)/seq/master",
    "seqDev": "SNCSEQ=$(SUPPORT)/seq/master",
    "seqSoftIocSupport": "SNCSEQ=$(SUPPORT)/seq/master",
    "softMotor": "MOTOR=$(SUPPORT)/motor/master",
    "sqlite": "SQLITE=$(SUPPORT)/sqlite/master",
    "sscan": "SSCAN=$(SUPPORT)/sscan/master",
    "sscanSupport.dbd": "SSCAN=$(SUPPORT)/sscan/master",
    "std": "STD=$(SUPPORT)/std/master",
    "stdSupport.dbd": "STD=$(SUPPORT)/std/master",
    "streamSynApps.dbd": "STREAMDEVICE=$(SUPPORT)/StreamDevice/master",
    "testSupport.dbd": "SNCSEQ=$(SUPPORT)/seq/master",
    "utilities": "UTILITIES=$(SUPPORT)/utilities/master",
    "utilities.dbd": "UTILITIES=$(SUPPORT)/utilities/master",
    "xxx": "",
    "zlib": "ZLIB=$(SUPPORT)/zlib/master",
    "ADnEDSupport": "AREA_DETECTOR=$(SUPPORT)/areaDetector/master",
    "ADnEDSupport.dbd": "AREA_DETECTOR=$(SUPPORT)/areaDetector/master",
    "ADnEDTransform": "AREA_DETECTOR=$(SUPPORT)/areaDetector/master",
    "CAENHVWrapperSim": "HVCAEN=$(SUPPORT)/HVCAENx527/master",
    "ECLab": "ECLAB=$(SUPPORT)/ECLab/master",
    "ECLab.dbd": "ECLAB=$(SUPPORT)/ECLab/master",
    "EClib": "ECLAB=$(SUPPORT)/ECLab/master",
    "EClib64": "ECLAB=$(SUPPORT)/ECLab/master",
    "FINS": "FINS=$(SUPPORT)/FINS/master",
    "FileList": "FILELIST=$(SUPPORT)/FileList/master",
    "FileList.dbd": "FILELIST=$(SUPPORT)/FileList/master",
    "GalilSupport": "GALIL=$(SUPPORT)/galil/master",
    "GalilSupport.dbd": "GALIL=$(SUPPORT)/galil/master",
    "HVCAENx527": "HVCAEN=$(SUPPORT)/HVCAENx527/master",
    "HVCAENx527Sim": "HVCAEN=$(SUPPORT)/HVCAENx527/master",
    "HVCAENx527Summary": "HVCAEN=$(SUPPORT)/HVCAENx527/master",
    "HVCAENx527Support.dbd": "HVCAEN=$(SUPPORT)/HVCAENx527/master",
    "LinMot": "MOTOR=$(SUPPORT)/motor/master",
    "Mclennan": "MOTOR=$(SUPPORT)/motor/master",
    "NetShrVar": "NETSHRVAR=$(SUPPORT)/NetShrVar/master",
    "NetShrVar.dbd": "NETSHRVAR=$(SUPPORT)/NetShrVar/master",
    "Newport": "MOTOR=$(SUPPORT)/motor/master",
    "PI_GCS2Support": "MOTOR=$(SUPPORT)/motor/master",
    "PI_GCS2Support.dbd": "MOTOR=$(SUPPORT)/motor/master",
    "PVAServerRegister.dbd": "PVACCESS=$(EV4_BASE)/pvAccessCPP",
    "ReadASCII": "READASCII=$(SUPPORT)/ReadASCII/master",
    "ReadASCII.dbd": "READASCII=$(SUPPORT)/ReadASCII/master",
    "VISAdrv": "VISADRV=$(SUPPORT)/VISAdrv/master",
    "VISAdrv.dbd": "VISADRV=$(SUPPORT)/VISAdrv/master",
    "avcodec": "AREA_DETECTOR=$(SUPPORT)/areaDetector/master",
    "avdevice": "AREA_DETECTOR=$(SUPPORT)/areaDetector/master",
    "avformat": "AREA_DETECTOR=$(SUPPORT)/areaDetector/master",
    "avutil": "AREA_DETECTOR=$(SUPPORT)/areaDetector/master",
    "csmbase": "CSM=$(SUPPORT)/csm/master",
    "cvtRecord": "CSM=$(SUPPORT)/csm/master",
    "cvtRecord.dbd": "CSM=$(SUPPORT)/csm/master",
    "dbPv.dbd": "PVASRV=$(EV4_BASE)/pvaSrv",
    "devLinMotMotor.dbd": "MOTOR=$(SUPPORT)/motor/master",
    "devMclennanMotor.dbd": "MOTOR=$(SUPPORT)/motor/master",
    "devNewport.dbd": "MOTOR=$(SUPPORT)/motor/master",
    "drvVxi11.dbd": "ASYN=$(SUPPORT)/asyn/master",
    "eemcuSupport": "EEMCU=$(SUPPORT)/MCAG_Base_Project/master/epics/epicsIOC",
    "eemcuSupport.dbd": "EEMCU=$(SUPPORT)/MCAG_Base_Project/master/epics/epicsIOC",
    "efsw": "EFSW=$(SUPPORT)/efsw/master",
    "fermichopper.dbd": "FERMCHOP=$(SUPPORT)/FZJ_fermichopper/master",
    "ffmpegServer": "AREA_DETECTOR=$(SUPPORT)/areaDetector/master",
    "ffmpegServer.dbd": "AREA_DETECTOR=$(SUPPORT)/areaDetector/master",
    "finsUDP.dbd": "FINS=$(SUPPORT)/FINS/master",
    "homing.dbd": "MOTOR=$(SUPPORT)/motor/master",
    "htmltidy": "HTMLTIDY=$(SUPPORT)/htmltidy/master",
    "modbus": "MODBUS=$(SUPPORT)/modbus/master",
    "modbusSupport.dbd": "MODBUS=$(SUPPORT)/modbus/master",
    "oncrpc": "ONCRPC=$(SUPPORT)/oncrpc/master",
    "procServControl": "PROCSERVCONTROL=$(SUPPORT)/procServControl/master",
    "procServControl.dbd": "PROCSERVCONTROL=$(SUPPORT)/procServControl/master",
    "pvAccess": "PVACCESS=$(EV4_BASE)/pvAccessCPP",
    "pvData": "PVDATA=$(EV4_BASE)/pvDataCPP",
    "pvMB": "PVCOMMON=$(EV4_BASE)/pvCommonCPP",
    "pvaSrv": "PVASRV=$(EV4_BASE)/pvaSrv",
    "pvcomplete": "PVCOMPLETE=$(SUPPORT)/pvcomplete/master",
    "pvcomplete.dbd": "PVCOMPLETE=$(SUPPORT)/pvcomplete/master",
    "random": "RANDOM=$(SUPPORT)/random/master",
    "randomSupport.dbd": "RANDOM=$(SUPPORT)/random/master",
    "sncSummary.dbd": "SNCSEQ=$(SUPPORT)/seq/master",
    "stream": "STREAMDEVICE=$(SUPPORT)/StreamDevice/master",
    "stream.dbd": "STREAMDEVICE=$(SUPPORT)/StreamDevice/master",
    "swscale": "AREA_DETECTOR=$(SUPPORT)/areaDetector/master",
    "webget": "WEBGET=$(SUPPORT)/webget/master",
    "webget.dbd": "WEBGET=$(SUPPORT)/webget/master",
    "xxx.dbd": ""
}


def find(pattern, path):
    """
    Find a file which matches a regex
    Args:
        pattern: regex to find
        path: path to start in

    Returns: list of matching filenames

    """
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if re.match(pattern, name) is not None:
                result.append(os.path.join(root, name))
    return result


def build_dependencies(ioc_dir):
    """
    Create a list of dependencies from build.mak
    :param ioc_dir: path for the IOC
    :return: set of dependencies
    """

    file_list = find(r"(build.mak)|(Makefile)", ioc_dir)

    if len(file_list) < 1:
        exit("ERROR: Too few makefiles. Found {}".format(file_list))

    all_dependencies = set()
    for file_to_parse in file_list:
        dependencies = set()
        print("    - Parsing {}".format(file_to_parse))

        for line in open(file_to_parse):
            match = re.match(r".*(?:_DBD|_LIBS) \+= (.*)", line)
            if match is not None:
                for dep in match.group(1).split():
                    dependencies.add(dep)

            match = re.match(r".*(?:_DBD_|_LIBS_).* \+= (.*)", line)
            if match is not None:
                print("STRANGE: Strange line fix manually {}".format(line))

        print("    - Dependencies {}".format(dependencies))
        all_dependencies = all_dependencies.union(dependencies)

    return all_dependencies


def get_entries(dependencies):
    """
    Get entries to add to release file
    Args:
        dependencies: dependencies for the IOC

    Returns:

    """
    lines = set()
    missing = set()
    for dependency in dependencies:
        try:
            lines.add(KNOWN_DEPENDENCIES[dependency])
        except KeyError:
            missing.add(dependency)
    if len(missing) != 0:
        print("\nERROR: There are unknown dependencies:\n    {}".format("    \n".join(sorted(missing))))
        print("\n(Fix this by adding the dependency to the KNOWN_DEPENDENCIES dictionary in this script. ")
        print("A list of possible dependencies can be found in EPICS\configure\MASTER_RELEASE)")
        exit(1)
    sorted_lines = sorted([line for line in lines if line is not ""])
    to_print = "\n".join(sorted_lines)
    print("    - Adding lines:\n        {}".format(to_print.replace("\n", "\n        ")))
    return sorted_lines


def write_extra_lines(outfile, lines):
    """
    Add extra lines in to build file
    Args:
        outfile: file to out to
        lines: lines to add
    """
    outfile.write("{}\n".format(FIRST_NEW_LINE))
    outfile.write("\n".join(lines))
    outfile.write("\n")
    outfile.write("{}\n".format(LAST_NEW_LINE))


def replace_config_lines(lines, ioc_dir):
    """
    Replace the expected config lines with generated lines.
    Args:
        lines: lines to replace.
        ioc_dir: ioc directory
    """
    release_filename = os.path.join(ioc_dir, "configure", "RELEASE")
    print("    - Replace lines in {}".format(release_filename))
    with open(release_filename) as infile:
        release_file_contents = infile.readlines()

    exclude = False
    with open(release_filename, mode="w") as outfile:
        for line in release_file_contents:
            exclude_line = exclude
            for excluded_line in RELEASE_LINES_TO_IGNORE:
                if excluded_line == line.strip():
                    exclude_line = True
            if FIRST_OLD_RELEASE_LINE == line.strip():
                write_extra_lines(outfile, lines)
            elif FIRST_NEW_LINE == line.strip():
                write_extra_lines(outfile, lines)
                exclude = True
            elif LAST_NEW_LINE == line.strip():
                exclude = False
            elif not exclude_line:
                outfile.write(line)


def replace_dependencies_in_release_file(base_dir):
    """
    Replaces the dependencies in the RELEASE file with dependencies from the base directory.
    Args:
        base_dir: the base directory which contains the release file
    """
    abs_base_dir = os.path.abspath(base_dir)
    print("Working in '{0}'".format(abs_base_dir))
    dependencies = build_dependencies(abs_base_dir)
    lines = get_entries(dependencies)
    replace_config_lines(lines, abs_base_dir)
    print("Done")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Edit the configure\RELEASE file to add dependencies needed')
    parser.add_argument('base_dir',
                        nargs='?',
                        help="base directory relative to current working directory; default current working dir")

    args = parser.parse_args()

    if args.base_dir is None:
        replace_dependencies_in_release_file(os.curdir)
    else:
        replace_dependencies_in_release_file(args.base_dir)
