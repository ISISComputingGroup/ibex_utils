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
    "$(EPICS_BASE_HOST_LIBS)": "",
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
    "devKeithley2400": "KHLY2400=$(SUPPORT)/Keithley_2400/master",
    "devKeithley2400.dbd": "KHLY2400=$(SUPPORT)/Keithley_2400/master",
    "easySQLite": "SQLITE=$(SUPPORT)/sqlite/master",
    "eemcuController.dbd": "EEMCU=$(SUPPORT)/MCAG_Base_Project/master/epics/epicsIOC",
    "EssMCAGmotorController.dbd": "EEMCU=$(SUPPORT)/MCAG_Base_Project/master/epics/epicsIOC",
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

KNOWN_MACROS_LIST = [
    "ACCESSSECURITY=$(SUPPORT)/AccessSecurity/master",
    "AGILENT33220A=$(SUPPORT)/agilent33220A/master",
    "AGILENT3631A=$(SUPPORT)/agilent3631A/master",
    "AMINT2L=$(SUPPORT)/amint2l/master",
    "AREA_DETECTOR=$(SUPPORT)/areaDetector/master",
    "ASUBFUNCTIONS=$(SUPPORT)/asubFunctions/master",
    "ASYN=$(SUPPORT)/asyn/master",
    "AUTOSAVE=$(SUPPORT)/autosave/master",
    "AXIS=$(SUPPORT)/axis/master",
    "BARNDOORS=$(SUPPORT)/barndoors/master",
    "BOOST=$(EPICS_ROOT)/libraries/master/boost",
    "BUSY=$(SUPPORT)/busy/master",
    "CALC=$(SUPPORT)/calc/master",
    "CAPUTLOG=$(SUPPORT)/caPutLog/master",
    "CCD100=$(SUPPORT)/CCD100/master",
    "COMMON=$(ISISSUPPORT)/Common/master",
    "CRYVALVE=$(SUPPORT)/cryValve/master",
    "CSM=$(SUPPORT)/csm/master",
    "CURL=$(SUPPORT)/curl/master",
    "CYBAMAN=$(SUPPORT)/cybaman/master",
    "DANFYSIK8000=$(SUPPORT)/danfysikMps8000",
    "DAQMXBASE=$(SUPPORT)/DAQmxBase/master",
    "DEVIOCSTATS=$(SUPPORT)/devIocStats/master",
    "ECLAB=$(SUPPORT)/ECLab/master",
    "#EEMCU=$(SUPPORT)/MCAG_Base_Project/master/epics/m-epics-eemcu",
    "EEMCU=$(SUPPORT)/MCAG_Base_Project/master/epics/epicsIOC",
    "EFSW=$(SUPPORT)/efsw/master",
    "EUROTHERM2K=$(SUPPORT)/eurotherm2k/master",
    "FERMCHOP=$(SUPPORT)/FZJ_fermichopper/master",
    "FZJDDFERMCHOP=$(SUPPORT)/FZJ_DDfermichopper/master",
    "FILELIST=$(SUPPORT)/FileList/master",
    "FILESERVER=$(SUPPORT)/FileServer/master",
    "FINS=$(SUPPORT)/FINS/master",
    "FLATBUFFERS=$(SUPPORT)/flatbuffers/master",
    "GALIL=$(SUPPORT)/galil/master",
    "GEMORC=$(SUPPORT)/gemorc/master",
    "HAMEG8123=$(ISISSUPPORT)/Hameg_8123/master",
    "HIDEWINDOW=$(SUPPORT)/HideWindow/master",
    "HLG=$(SUPPORT)/hlg/master",
    "HTMLTIDY=$(SUPPORT)/htmltidy/master",
    "HVCAEN=$(SUPPORT)/HVCAENx527/master",
    "ICPCONFIG=$(SUPPORT)/icpconfig/master",
    "IEG=$(SUPPORT)/ieg/master",
    "INSTRON=$(SUPPORT)/instron/master",
    "IP=$(SUPPORT)/ip/master",
    "IPAC=$(SUPPORT)/ipac/master",
    "#ISISDAE=$(SUPPORT)/isisdae/master # comment out as contains incompatible version of TinyXML for DAE3",
    "JAWS=$(SUPPORT)/jaws/master",
    "JULABO=$(SUPPORT)/julabo/master",
    "KHLY2400=$(SUPPORT)/Keithley_2400/master",
    "KEPCO=$(SUPPORT)/kepco/master",
    "LKSH336=$(SUPPORT)/lakeshore/master/lakeshore336",
    "LKSH460=$(SUPPORT)/lakeshore460/master",
    "LIBICONV=$(SUPPORT)/libiconv/master",
    "LIBJSON=$(SUPPORT)/libjson/master",
    "LIBRDKAFKA=$(SUPPORT)/librdkafka/master",
    "LIBXML2=$(SUPPORT)/libxml2/master",
    "LIBXSLT=$(SUPPORT)/libxslt/master",
    "LINKAM95=$(SUPPORT)/linkam95/master",
    "LVDCOM=$(ISISSUPPORT)/lvDCOM/master",
    "MCA=$(SUPPORT)/mca/master",
    "MAGNET3D=$(ISISSUPPORT)/magnet3D/master",
    "MERCURY_ITC=$(ISISSUPPORT)/MercuryiTC/master",
    "MK2CHOPR=$(SUPPORT)/mk2chopper/master",
    "MODBUS=$(SUPPORT)/modbus/master",
    "MOTIONSETPOINTS=$(SUPPORT)/motionSetPoints/master",
    "MOTOR=$(SUPPORT)/motor/master",
    "MOTOREXT=$(SUPPORT)/motorExtensions/master",
    "MK2CHOPR=$(SUPPORT)/mk2chopper/master",
    "MYSQL=$(SUPPORT)/MySQL/master",
    "NEOCERA=$(SUPPORT)/neocera/master",
    "NETSHRVAR=$(SUPPORT)/NetShrVar/master",
    "NANODAC=$(SUPPORT)/nanodac/master",
    "NULLHTTPD=$(SUPPORT)/nullhttpd/master",
    "OPENSSL=$(SUPPORT)/OpenSSL/master",
    "OPTICS=$(SUPPORT)/optics/master",
    "PCRE=$(SUPPORT)/pcre/master",
    "PDR2000=$(SUPPORT)/pdr2000/master",
    "PIXELMAN=$(SUPPORT)/pixelman/master",
    "PROCSERVCONTROL=$(SUPPORT)/procServControl/master",
    "PUGIXML=$(SUPPORT)/pugixml/master",
    "PVCOMPLETE=$(SUPPORT)/pvcomplete/master",
    "PVDUMP=$(SUPPORT)/pvdump/master",
    "READASCII=$(SUPPORT)/ReadASCII/master",
    "ROTSC=$(SUPPORT)/rotating_sample_changer/master",
    "RUNCONTROL=$(SUPPORT)/RunControl/master",
    "RANDOM=$(SUPPORT)/random/master",
    "SAMPLECHANGER=$(SUPPORT)/sampleChanger/master",
    "SLACKING=$(EPICS_ROOT)/libraries/master/slacking",
    "SNCSEQ=$(SUPPORT)/seq/master",
    "SKFMB350=$(SUPPORT)/skf_mb350/master",
    "SKFCHOPPER=$(SUPPORT)/SKFChopper/master",
    "SPRLG=$(SUPPORT)/superlogics/master",
    "SQLITE=$(SUPPORT)/sqlite/master",
    "SSCAN=$(SUPPORT)/sscan/master",
    "STD=$(SUPPORT)/std/master",
    "STPS350=$(ISISSUPPORT)/Stanford_PS350/master",
    "STSR400=$(ISISSUPPORT)/Stanford_SR400/master",
    "STREAMDEVICE=$(SUPPORT)/StreamDevice/master",
    "TDKLAMBDAGENESYS=$(SUPPORT)/TDKLambdaGenesys/master",
    "TEKDMM40X0=$(SUPPORT)/Tektronix_DMM_40X0/master",
    "TEKAFG3XXX=$(SUPPORT)/Tektronix_AFG3XXX/master",
    "TEKMSO4104B=$(SUPPORT)/Tektronix_MSO_4104B/master",
    "TINYXML=$(SUPPORT)/TinyXML/master",
    "TPG300=$(SUPPORT)/TPG/master",
    "TPG=$(SUPPORT)/TPG/master",
    "TTIEX355P=$(SUPPORT)/ttiEX355P/master",
    "UTILITIES=$(SUPPORT)/utilities/master",
    "VISADRV=$(SUPPORT)/VISAdrv/master",
    "WEBGET=$(SUPPORT)/webget/master",
    "ZLIB=$(SUPPORT)/zlib/master",

    # EPICS v4
    "EV4_BASE=$(SUPPORT)/EPICS_V4/master",
    "PVDATABASE=$(EV4_BASE)/pvDatabaseCPP",
    "PVASRV=$(EV4_BASE)/pvaSrv",
    "PVACLIENT=$(EV4_BASE)/pvaClientCPP",
    "PVACCESS=$(EV4_BASE)/pvAccessCPP",
    "NORMATIVETYPES=$(EV4_BASE)/normativeTypesCPP",
    "PVDATA=$(EV4_BASE)/pvDataCPP",
    "PVCOMMON=$(EV4_BASE)/pvCommonCPP"]

KNOWN_MACROS = {}
for macro in KNOWN_MACROS_LIST:
    macro_name = macro.split("=")[0]
    KNOWN_MACROS[macro_name] = macro


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


def macro_dependencies(ioc_dir):
    """
    Get a list of possible dependenices for the macros
    Args:
        ioc_dir:

    Returns:

    """
    file_list = find(r".*", ioc_dir)

    all_dependencies = set()
    for file_to_parse in file_list:
        dependencies = set()
        print(f"    - Parsing {file_to_parse}")

        for line in open(file_to_parse):
            try:
                splits = line.split("$(")[1:]
            except IndexError:
                splits = []
            try:
                splits.extend(line.split("${")[1:])
            except IndexError:
                pass
            for split in splits:
                for macro, dependency in KNOWN_MACROS.items():
                    if split.strip().startswith(macro):
                        dependencies.add(dependency)

        print(f"    - Dependencies {dependencies}")
        all_dependencies = all_dependencies.union(dependencies)

    return all_dependencies


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
        print(f"    - Parsing {file_to_parse}")

        for line in open(file_to_parse):
            match = re.match(r".*(?:_DBD|_LIBS) \+= (.*)", line)
            if match is not None:
                for dep in match.group(1).split():
                    dependencies.add(dep)

            match = re.match(r".*(?:_DBD_|_LIBS_).* \+= (.*)", line)
            if match is not None:
                print(f"STRANGE: Strange line fix manually {line}")

        print("    - Dependencies {}".format(dependencies))
        all_dependencies = all_dependencies.union(dependencies)

    return all_dependencies


def get_entries(dependencies, macros):
    """
    Get entries to add to release file
    Args:
        dependencies: dependencies for the IOC
        macros: macros to add (yes I know it is not nice but it works)

    Returns:

    """
    lines = set(macros)
    missing = set()
    for dependency in dependencies:
        try:
            lines.add(KNOWN_DEPENDENCIES[dependency])
        except KeyError:
            missing.add(dependency)
    if len(missing) != 0:
        print("\nERROR: There are unknown dependencies:\n    {}".format("    \n".join(sorted(missing))))
        print("\n(Fix this by adding the dependency to the KNOWN_DEPENDENCIES dictionary in this script. ")
        print("A list of possible dependencies can be found in EPICS\\configure\\MASTER_RELEASE)")
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

    macros = macro_dependencies(abs_base_dir)
    if "ioc" in abs_base_dir:
        macros.add("ACCESSSECURITY=$(SUPPORT)/AccessSecurity/master")
    dependencies = build_dependencies(abs_base_dir)
    lines = get_entries(dependencies, macros)

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
