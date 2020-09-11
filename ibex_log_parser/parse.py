import os
import re
from datetime import datetime

# Filter log lines containing
TICKET = "Ticket2162:"

# Severe log line
SEVERE = "SEVERE:"
SEVERE_LINE_START = f"{SEVERE} {TICKET}"


class LogLine:
    def __init__(self, time, pv, message):
        self.time = time
        self.message = message.strip()
        self.pv = pv.strip()

    def __repr__(self):
        date_time_string = datetime.strftime(self.time, "%H:%M:%S.%f")
        return f"{date_time_string}: {self.message}"


def parse_severe_line(previous_line, line):

    # Mar 22, 2017 12:04:24 PM org.epics.pvmanager.SourceDesiredRateDecoupler sendDesiredRateEvent
    pattern = r"(.* (?:AM|PM)).*"
    match = re.match(pattern, previous_line)
    date_string, = match.groups()
    date_time = datetime.strptime(date_string, '%b %d, %Y %I:%M:%S %p')
    # SEVERE: Ticket2162: TE:NDW1407:CS:IOC:INSTETC_01:DEVIOS:TOD - PVDirector event connected true

    match = re.match(SEVERE_LINE_START + "(.*) - (.*)", line)
    if match is None:
        exit("ERROR: servere message not match {0}".format(line))

    pv, message = match.groups()

    return LogLine(date_time, pv, message)


def parse_normal_line(line):
    # *2017-03-22 12:04:24.556 [PVMgr Worker 3] INFO  org.epics.pvmanager.PVReaderImpl - Ticket2162: TE:NDW1407:CS:BLOCKSERVER:PVS:ACTIVE - PVReaderImpl valueChange

    pattern = r"\*(.*) \[.*" + TICKET + r"(.*) - (.*)"
    match = re.match(pattern, line)
    if match is None:
        print(f"Can not understand {line}")
        return None

    time_string, pv, message = match.groups()

    dateTime = datetime.strptime(time_string, r"%Y-%m-%d %H:%M:%S.%f")

    return LogLine(dateTime, pv, message)


def check_time(time, start_time_hour, start_time_mins, start_time_secs):
    if time.hour != start_time_hour:
        return time.hour > start_time_hour

    if time.minute != start_time_mins:
        return time.minute > start_time_mins

    return time.second >= start_time_secs


def print_and_log(log_file, message):
    print(message)
    log_file.write(f"\n{message}")


def read_log_files(log_file, day, month):
    filedir = r"C:\Instrument\runtime-ibex.product\logs" + "\\" + month
    filepaths = [os.path.join(filedir, filepath) for filepath in os.listdir(filedir) if month + "-" + day in filepath]
    filepaths.append(r"C:\Instrument\runtime-ibex.product\logs\isis.log")

    pvChanges = []
    previous_line = ""
    for filepath in filepaths:
        print_and_log(log_file, f"Reading: {filepath}")
        with open(filepath) as file:
            for line in file:
                if TICKET in line:
                    if line.startswith(SEVERE):
                        pvChange = parse_severe_line(previous_line, line)
                    else:
                        pvChange = parse_normal_line(line)

                    if pvChange is not None:
                        pvChanges.append(pvChange)
                previous_line = line

    return sorted(pvChanges, key=lambda student: student.time)


def log_changed_pvs(log_file, pvChanges):
    print_and_log(log_file, "PVS:")
    for pv_name in set([x.pv for x in pvChanges]):
        print_and_log(log_file, "    {0}".format(pv_name))
    print_and_log(log_file, "\n\n")


def log_pv_timeline(log_file, pvChanges, wanted_pvs):
    print_and_log(log_file, "Timeline for {0}".format(wanted_pvs))
    for pvChange in pvChanges:
        if pvChange.pv in wanted_pvs:
            print_and_log(log_file, "{0:>20} = {1}".format(pvChange.pv.strip()[-20:], pvChange))


def log_events_after_time(log_file, pvChanges, start_time_hour, start_time_mins, start_time_secs):
    print_and_log(log_file, "Timeline after {0}:{1}:{2}".format(start_time_hour, start_time_mins, start_time_secs))
    for pvChange in pvChanges:
        if check_time(pvChange.time, start_time_hour, start_time_mins, start_time_secs):
            print_and_log(log_file, "{0:>20} = {1}".format(pvChange.pv.strip()[-20:], pvChange))


def log_flow_control(log_file, pvChanges):

    print_and_log(log_file, "Flow control")
    for pvChange in pvChanges:
        if str("flow control") in str(pvChange.message).lower():
            print_and_log(log_file, pvChange)


if __name__ == "__main__":

    month = "2017-04"
    day = "06"

    start_time_hour = 16
    start_time_mins = 24
    start_time_secs = 00

    with open(r"c:\tmp\ibexLog{0}-{1}.txt".format(month, day), mode="w") as log_file:
        pvChanges = read_log_files(log_file, day, month)

        log_changed_pvs(log_file, pvChanges)

        log_pv_timeline(log_file, pvChanges, ["TE:NDW1407:CS:SB:TEMP1", "all"])
        # log_pv_timeline(log_file, pvChanges, ["TE:NDW1407:SIMPLE:NUMBERED1", "unknown", "buffer"])

        # log_events_after_time(log_file, pvChanges, start_time_hour, start_time_mins, start_time_secs)

        # log_flow_control(log_file, pvChanges)
