import os
from typing import Union
from datetime import datetime

def format_build_num_without_dash(build_num):
    return f"BUILD{build_num}"

def format_build_num_with_dash(build_num):
    return f"BUILD-{build_num}"

kits_root = r"\\isis\inst$\kits$\CompGroup\ICP"
epics_builds = ["EPICS_CLEAN_win10_x64", "EPICS_win7_x64", "EPICS_CLEAN_win7_x86", "EPICS_win7_x64_devel", "EPICS_STATIC_CLEAN_win7_x64"]
epics_build_dirs = [(f"EPICS\\{build}", format_build_num_with_dash) for build in epics_builds] 
build_dirs = [("Client_E4", format_build_num_without_dash), ("genie_python_3", format_build_num_with_dash)] + epics_build_dirs

def get_latest_build(dir, directory_formatter) -> Union[None, str]:
    latest_build = None
    with open(os.path.join(dir, "LATEST_BUILD.txt")) as latest_build_file:
        latest_build = latest_build_file.readline().strip()
    latest_build_dir = os.path.join(dir, directory_formatter(latest_build)) if latest_build is not None else None
    return latest_build_dir

def get_last_modified_datetime(dir):
    time_in_seconds_of_last_modification = os.path.getmtime(dir)
    datetime_of_last_modification = datetime.fromtimestamp(time_in_seconds_of_last_modification)
    return datetime_of_last_modification

def get_formatted_last_modified_datetime(dir):
    last_modified_date = get_last_modified_datetime(dir)
    return last_modified_date.strftime("%d/%m/%Y, %H:%M:%S")

def modified_in_last_x_days(dir, x_days):
    datetime_of_last_modification = get_last_modified_datetime(dir)
    datetime_now = datetime.now()
    timedelta_since_last_modification = datetime_now - datetime_of_last_modification
    return timedelta_since_last_modification.days < x_days

def confirm_success_or_failure(latest_build):
    x_days = 5
    last_modified_datetime = get_formatted_last_modified_datetime(latest_build)
    if modified_in_last_x_days(latest_build, x_days):
        print(f"SUCCESS: {latest_build} has been modified in the last {x_days} days. Last modified: {last_modified_datetime}")
    else:
        print(f"WARNING: {latest_build} modified longer than {x_days} ago. Last modified: {last_modified_datetime}")

def check_build_dir(build_dir, directory_formatter):
    latest_build = get_latest_build(build_dir, directory_formatter)
    if latest_build is None:
            print(f"WARNING: Could not get latest build dir from {build_dir}")
    else:
        confirm_success_or_failure(latest_build)

def check_build_dirs(build_dirs):
    for build_dir in build_dirs:
        directory = build_dir[0]
        directory_formatter = build_dir[1]
        build_dir_full_path = os.path.join(kits_root, directory)
        check_build_dir(build_dir_full_path, directory_formatter)

if __name__ == "__main__":
    check_build_dirs(build_dirs)