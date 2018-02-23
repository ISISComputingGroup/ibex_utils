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
    "asSupport.dbd": "AUTOSAVE=$(SUPPORT)/autosave/master",
    "asubFunctions": "ASUBFUNCTIONS=$(SUPPORT)/asubFunctions/master",
    "asubFunctions.dbd": "ASUBFUNCTIONS=$(SUPPORT)/asubFunctions/master",
    "asyn": "ASYN=$(SUPPORT)/asyn/master\nONCRPC=$(SUPPORT)/oncrpc/master",
    "asyn.dbd": "ASYN=$(SUPPORT)/asyn/master",
    "axis.dbd": "AXIS=$(SUPPORT)/axis/master",
    "autosave": "AUTOSAVE=$(SUPPORT)/autosave/master",
    "base.dbd": "",
    "busy": "BUSY=$(SUPPORT)/busy/master",
    "busySupport.dbd": "BUSY=$(SUPPORT)/busy/master",
    "caPutLog": "CAPUTLOG=$(SUPPORT)/caPutLog/master",
    "caPutLog.dbd": "CAPUTLOG=$(SUPPORT)/caPutLog/master",
    "calc": "CALC=$(SUPPORT)/calc/master",
    "calcSupport.dbd": "CALC=$(SUPPORT)/calc/master",
    "devIocStats": "DEVIOCSTATS=$(SUPPORT)/devIocStats/master",
    "devIocStats.dbd": "DEVIOCSTATS=$(SUPPORT)/devIocStats/master",
    "devSequencer.dbd": "SNCSEQ=$(SUPPORT)/seq/master",
    "devSoftMotor.dbd": "MOTOR=$(SUPPORT)/motor/master",
    "drvAsynIPPort.dbd": "ASYN=$(SUPPORT)/asyn/master",
    "drvAsynSerialPort.dbd": "ASYN=$(SUPPORT)/asyn/master",
    "easySQLite": "SQLITE=$(SUPPORT)/sqlite/master",
    "icpconfig": "ICPCONFIG=$(SUPPORT)/icpconfig/master",
    "icpconfig.dbd": "ICPCONFIG=$(SUPPORT)/icpconfig/master",
    "libjson": "LIBJSON=$(SUPPORT)/libjson/master",
    "motionSetPoints": "MOTIONSETPOINTS=$(SUPPORT)/motionSetPoints/master",
    "motionSetPoints.dbd": "MOTIONSETPOINTS=$(SUPPORT)/motionSetPoints/master",
    "motor": "MOTOR=$(SUPPORT)/motor/master",
    "motorSimSupport": "MOTOR=$(SUPPORT)/motor/master",
    "motorSimSupport.dbd": "MOTOR=$(SUPPORT)/motor/master",
    "motorSupport.dbd": "MOTOR=$(SUPPORT)/motor/master",
    "pcre": "PCRE=$(SUPPORT)/pcre/master",
    "pugixml": "PUGIXML=$(SUPPORT)/pugixml/master",
    "pv": "SNCSEQ=$(SUPPORT)/seq/master",
    "pvdump": "PVDUMP=$(SUPPORT)/pvdump/master",
    "pvdump.dbd": "PVDUMP=$(SUPPORT)/pvdump/master",
    "sampleChanger": "SAMPLECHANGER=$(SUPPORT)/sampleChanger/master",
    "sampleChanger.dbd": "SAMPLECHANGER=$(SUPPORT)/sampleChanger/master",
    "seq": "SNCSEQ=$(SUPPORT)/seq/master",
    "seqDev": "SNCSEQ=$(SUPPORT)/seq/master",
    "softMotor": "MOTOR=$(SUPPORT)/motor/master",
    "sqlite": "SQLITE=$(SUPPORT)/sqlite/master",
    "sscan": "SSCAN=$(SUPPORT)/sscan/master",
    "sscanSupport.dbd": "SSCAN=$(SUPPORT)/sscan/master",
    "std": "STD=$(SUPPORT)/std/master",
    "stdSupport.dbd": "STD=$(SUPPORT)/std/master",
    "utilities": "UTILITIES=$(SUPPORT)/utilities/master",
    "utilities.dbd": "UTILITIES=$(SUPPORT)/utilities/master",
    "zlib": "ZLIB=$(SUPPORT)/zlib/master"
}


def build_dependencies(ioc_dir):
    """
    Create a list of dependencies from build.mak
    :param ioc_dir: path for the IOC
    :return: set of dependencies
    """
    app_dir = [app_dir for app_dir in os.listdir(ioc_dir) if app_dir.endswith("IOC-01App")]
    if len(app_dir) != 1:
        exit("ERROR: Too many/too few app dirs found. Found {}".format(app_dir))
    build_mak_filename = os.path.join(ioc_dir, app_dir[0], "src", "build.mak")
    print("    - Parsing {}".format(build_mak_filename))

    dependencies = set()
    for line in open(build_mak_filename):
        match = re.match(r"(?:\$\(APPNAME\)_DBD|\$\(APPNAME\)_LIBS) \+= (.*)", line)
        if match is not None:
            for dep in match.group(1).split():
                dependencies.add(dep)
    print("    - Dependencies {}".format(dependencies))
    return dependencies


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


def replace_dependencies_in_release_file(ioc_dir):
    """
    Replaces the dependencies in the RELEASE file with dependencies from the IOC directory.
    Args:
        ioc_dir: the IOC directory
    """
    abs_ioc_dir = os.path.abspath(ioc_dir)
    print("Working in '{0}'".format(abs_ioc_dir))
    dependencies = build_dependencies(abs_ioc_dir)
    lines = get_entries(dependencies)
    replace_config_lines(lines, abs_ioc_dir)
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
