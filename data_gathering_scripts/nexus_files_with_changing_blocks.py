"""
Utility
"""

from datetime import datetime, timedelta

import h5py
import os

# List of machines to perform analysis for
machines = ("NDXALF",
            "NDXENGINX",
            "NDXHRPD",
            "NDXIMAT",
            "NDXIRIS",
            "NDXLARMOR",
            "NDXMERLIN",
            "NDXMUONFE",
            "NDXPOLARIS",
            "NDXVESUVIO",
            "NDXZOOM")

IGNORE_LIST = ("EPICS_PUTLOG", "ICP_DAE_TD", "ICP_SYS_TD", "Status")

# List of cycles
CYCLES = ("cycle_17_1", "cycle_17_2", "cycle_17_3")

# Where the data is
TEMPLATED_PATH = r"\\isis\inst$\{machine}\Instrument\data\{cycle}"


def check(machine, cycle, outf):
    """
    Check that every data file contains the same blocks as previous data files or that the last data file is 1000s ago
    :param machine: machine to look at
    :param cycle: cycle to use
    :param outf: file to output results to
    :return: nothing
    """
    last_data_file = None
    header = f"--- FILES {machine} {cycle} ---\n"
    print(header)
    outf.write(header)

    path = TEMPLATED_PATH.format(machine=machine, cycle=cycle)
    try:
        listdir = sorted(os.listdir(path))
    except (IOError, WindowsError):
        outf.write("No files")
        listdir = []

    for file_name in listdir:
        if file_name.endswith(".nxs"):

            try:
                with h5py.File(os.path.join(path, file_name)) as f:
                    data_file = {
                        "start_time": f["raw_data_1"]["start_time"][0],
                        "end_time": f["raw_data_1"]["end_time"][0],
                        "run_number": f["raw_data_1"]["run_number"][0],
                        "blocks": f["raw_data_1"]["selog"].keys()
                    }

                if last_data_file is not None:
                    last_blocks = set(last_data_file["blocks"]) - set(IGNORE_LIST)
                    current_blocks = set(data_file["blocks"]) - set(IGNORE_LIST)
                    additions = last_blocks - current_blocks
                    removals = current_blocks - last_blocks
                    same = len(additions) + len(removals) == 0
                    end_of_last = datetime.strptime(last_data_file["end_time"], "%Y-%m-%dT%H:%M:%S")
                    start_of_current = datetime.strptime(data_file["start_time"], "%Y-%m-%dT%H:%M:%S")
                    gap = start_of_current - end_of_last
                    if not same and gap < timedelta(seconds=100):
                        run_number = data_file["run_number"]
                        outf.write(f"{run_number}, {gap.total_seconds()}, {start_of_current}: added {additions} removed {removals}\n")

                last_data_file = data_file
            except IOError:
                print(f"Problem opening/reading {file_name}")


with open(r"C:\temp\problems.txt", mode="w") as outf:
    for machine in machines:
        for cycle in CYCLES:
            check(machine, cycle, outf)
