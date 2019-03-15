# -*- coding: utf-8 -*-
"""
Uses h5py to extract given log values from an ISIS NeXus file over a given time period. It is assumed
that the control software has logged when values changed.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)

# std imports
from argparse import ArgumentParser
from collections import OrderedDict
from datetime import datetime, timedelta
import logging
import os.path as osp
import sys

# third party imports
from h5py import (File as HDF5File)
import numpy as np
from six import iteritems

# Logger for this module
LOGGER = logging.getLogger(__name__)

# ISIS NeXus entry names
ROOT_ENTRY = 'raw_data_1'
SAMPLE_ENV_LOGS_ENTRY = 'selog'
VALUE_LOG_ENTRY = 'value_log'
RUN_START_ENTRY = 'start_time'
TIME_ENTRY = 'time'
VALUE_ENTRY = 'value'
TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S'

# Constants
TEN_DAYS_IN_SECONDS = 10*24*60*60


def parse_args():
    """Parse input arguments to script"""
    parser = ArgumentParser(description='Process log entries from an ISIS NeXus file and display'
                                        'values from a given time period')
    parser.add_argument("filepath", help='Path to an ISIS NeXus file')
    parser.add_argument("selog_names", nargs='*', help='An optional list of SE log names')
    parser.add_argument("--outfile", help='Path to outputfile. If None is given then display to screen')
    return parser.parse_args()


def fatal(msg, exit_code=1):
    """
    End program by logging message and calling sys.exit with exit code = 1

    :param msg: Message to display at error log level
    :param exit_code: Exit code for program. Default=1
    """
    LOGGER.error(msg)
    sys.exit(exit_code)


def logs_info(h5file, rel_time_start, names=None):
    """
    Return values of log parameters when they change, i.e do not use every
    log entry but only display values when they change.

    :param h5file: Reference to H5File open at root level
    :param rel_time_start: A time relative to run start to begin processing logs
    :param names: An optional list of names to limit the log entries to process. Defaults to all selog
    :returns: A dict giving a list of time/values for each log entry
    """
    root = h5file[ROOT_ENTRY]
    start_time_str = root[RUN_START_ENTRY][0].decode('UTF-8')
    start_timestamp = datetime.strptime(start_time_str, TIMESTAMP_FORMAT)
    selog_group = root[SAMPLE_ENV_LOGS_ENTRY]

    names = names if names is not None else selog_group.keys()
    log_values = OrderedDict()
    for name in names:
        log_values[name] = find_log_info(selog_group[name], start_timestamp,
                                         rel_time_start)

    return log_values


def find_log_info(h5group, start_timestamp, rel_time_start):
    """
    Assumes that the times in the time array are relative to run start
    :param h5group: The open log entry group
    :param start_time: Start datetime of run
    :param rel_time_start: A time relative to run start to begin processing logs
    :return: A tuple of (time, value) pairs for each change in log value
    """
    times_and_values = h5group[VALUE_LOG_ENTRY]
    all_times = times_and_values[TIME_ENTRY].value
    # find first time entry
    rel_time_indices = np.where(all_times >= -rel_time_start)[0]
    if rel_time_indices.size == 0:
        LOGGER.warning('No times found within given time frame in "{}"'.format(h5group.name))
        return None
    all_values = times_and_values[VALUE_ENTRY].value
    if all_values.size != all_times.size:
        LOGGER.warning('times/values array size mismatch in "{}"'.format(h5group.name))
        return None

    # find indices where the values change
    timerange_values = all_values[rel_time_indices]
    timerange_times = all_times[rel_time_indices]
    value_change_indices = np.where(timerange_values[:-1] != timerange_values[1:])[0]

    def append_value(value_list, time_in_seconds, value):
        value_list.append((start_timestamp + timedelta(seconds=time_in_seconds), value))
        return value_list

    log_info = []
    if len(value_change_indices) > 1:
        # the first index will be the last index where the value is the same
        # but we want to keep that assigned to the first timestamp
        append_value(log_info, int(timerange_times[0]), timerange_values[value_change_indices[0]])
        # now append the rest of the pairs
        for idx in value_change_indices[1:]:
            append_value(log_info, int(timerange_times[idx]), timerange_values[idx])
    else:
        append_value(log_info, int(timerange_times[0]), timerange_values[0])

    return log_info


def write_out(info, out_file):
    """
    :param info: The dictionary of log information
    :param outfile: Destination to write output
    """
    for log_name, values in iteritems(info):
        out_file.write(log_name + "\n")
        for time, value in values:
            if isinstance(value, (float, np.float32, np.float64)):
                format_str = "{}    {:.5f}"
            else:
                format_str = "{}    {}"
            out_file.write(format_str.format(time, value))
            out_file.write('\n')
        out_file.write('\n')


def main():
    """Entry-point of program"""
    args = parse_args()

    if not osp.exists(args.filepath):
        fatal('File {} does exist.'.format(args.filepath))

    try:
        h5file = HDF5File(args.filepath, mode='r')
    except Exception as exc:
        fatal(str(exc))

    info = logs_info(h5file, TEN_DAYS_IN_SECONDS, args.selog_names)
    if args.outfile is not None:
        outfile = open(args.outfile, 'w')
    else:
        outfile = sys.stdout

    write_out(info, outfile)


if __name__ == '__main__':
    main()
