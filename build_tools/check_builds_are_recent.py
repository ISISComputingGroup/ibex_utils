import os
from typing import Union
from datetime import datetime

kits_root = r"\\isis\inst$\kits$\CompGroup\ICP"
build_dirs = ["Client_E4"]

def get_latest_build(dir) -> Union[None, str]:
    latest_build = None
    with open(os.path.join(dir, "LATEST_BUILD.txt")) as latest_build_file:
        latest_build = latest_build_file.readline().strip()
    latest_build_dir = os.path.join(dir, f"BUILD{latest_build}") if latest_build is not None else None
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

def check_build_dir(build_dir):
    latest_build = get_latest_build(build_dir)
    if latest_build is None:
            print(f"WARNING: Could not get latest build dir from {build_dir}")
    else:
        confirm_success_or_failure(latest_build)

def check_build_dirs(build_dirs):
    for build_dir in build_dirs:
        build_dir_full_path = os.path.join(kits_root, build_dir)
        check_build_dir(build_dir_full_path)

if __name__ == "__main__":
    check_build_dirs(build_dirs)
