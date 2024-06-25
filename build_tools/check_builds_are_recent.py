import os
from typing import Union
from datetime import datetime
import sys
import json

kits_root = r"\\isis\inst$\kits$\CompGroup\ICP"

def format_build_num_with_dash(build_num):
    return f"BUILD-{build_num}"

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

def was_modified_recently(latest_build, num_days):
    last_modified_datetime = get_formatted_last_modified_datetime(latest_build)
    modified_recently = modified_in_last_x_days(latest_build, num_days)
    if modified_recently:
        print(f"SUCCESS: {latest_build} has been modified in the last {num_days} days. Last modified: {last_modified_datetime}")
    else:
        print(f"WARNING: {latest_build} modified longer than {num_days} ago. Last modified: {last_modified_datetime}")
    return modified_recently

def check_build_dir(build_dir, num_days, directory_formatter):
    latest_build = get_latest_build(build_dir, directory_formatter)
    modified_recently = False
    if latest_build is None:
        print(f"WARNING: Could not get latest build dir from {build_dir}")
    else:
        modified_recently = was_modified_recently(latest_build, num_days)
    return modified_recently

def check_build_dirs(build_dirs):
    build_dirs_not_modified_recently = []
    for build_dir in build_dirs:
        directory = build_dir[0]
        stale_days_limit = int(build_dir[1])
        directory_formatter = build_dir[2]
        build_dir_full_path = os.path.join(kits_root, directory)
        modified_recently = check_build_dir(build_dir_full_path, stale_days_limit, directory_formatter)
        if not modified_recently:
            build_dirs_not_modified_recently.append(build_dir_full_path)
    return build_dirs_not_modified_recently

if __name__ == "__main__":
    builds_to_check = os.getenv("BUILDS_TO_CHECK")
    if builds_to_check is None:
        print (f"ERROR: BUILDS_TO_CHECK enviroment variable not set")
        sys.exit(1)
    try:
        builds_by_stale_times = json.loads(builds_to_check)
    except ValueError as e:
        print(f"ERROR: parameter is not valid JSON.\nParameter:{builds_to_check}\nSpecific Error: {e.args}")
        sys.exit(1)
    build_dirs = []
    for time, builds_by_stale_time in builds_by_stale_times.items():
        for build in builds_by_stale_time:
            directory_formatter = format_build_num_with_dash
            build_dirs.append((build,time,directory_formatter))    
    build_dirs_not_modified_recently = check_build_dirs(build_dirs)
    if build_dirs_not_modified_recently:
        sys.exit(1)
    else:
        sys.exit(0)
