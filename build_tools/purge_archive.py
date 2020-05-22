import os
import shutil
import stat
from datetime import datetime, timedelta

max_build_age_in_days = 30
minimum_number_of_builds_to_keep = 10
build_area = r"\\isis\inst$\kits$\CompGroup\ICP"


def winapi_path(dos_path):
    path = os.path.abspath(dos_path)
    long_path_identifier = u"\\\\?\\"
    if path.startswith(long_path_identifier):
        win_path = path
    elif path.startswith(u"\\\\"):
        win_path = long_path_identifier + u"UNC\\" + path[2:]
    else:
        win_path = long_path_identifier + path
    return win_path


def rmtree_error(func, path, exc_info):
    try:
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
        func(winapi_path(path))
    except Exception as e:
        print("Unable to delete file: {}".format(e))


def delete_dir(directory):
    print("Deleting directory: {}".format(directory))
    try:
        shutil.rmtree(winapi_path(directory), onerror=rmtree_error)
    except Exception as e:
        print("Unable to delete directory {}: {}".format(directory, e))


def old_enough_to_delete(f):
    return datetime.now()-datetime.fromtimestamp(os.path.getmtime(f)) > timedelta(days=max_build_age_in_days)


def is_build_dir(d):
    return os.path.isdir(d) and "BUILD" in os.path.split(d)[-1].upper()


def deletion_directories(project_areas):
    dirs = []
    for project_area in project_areas:
        print("Identifying old builds for deletion in: {}".format(project_area))
        project_dirs = [os.path.join(project_area, sub_dir) for sub_dir in os.listdir(project_area)]
        build_dirs_by_age = sorted(filter(is_build_dir, project_dirs), key=os.path.getmtime, reverse=True)
        build_dirs_we_could_delete = build_dirs_by_age[minimum_number_of_builds_to_keep:]
        build_dirs_we_will_delete = filter(old_enough_to_delete, build_dirs_we_could_delete)
        dirs += build_dirs_we_will_delete
    return dirs


def purge(dry_run=False):
    print("Beginning archive purge...")
    project_areas = [os.path.join(build_area, proj) for proj in ("Client_E4", "genie_python", "genie_python_3", "VHDS")] + \
        [os.path.join(build_area, "EPICS", proj) for proj in os.listdir(os.path.join(build_area, "EPICS"))
         if proj.startswith("EPICS")]

    for d in deletion_directories(project_areas):
        if dry_run:
            print("{}".format(d))
        else:
            delete_dir(d)
    print("Archive purge complete.")


purge()
