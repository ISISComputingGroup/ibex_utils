import os
import shutil
import stat
from datetime import datetime, timedelta

max_build_age_in_days = 30
minimum_number_of_builds_to_keep = 10


def robocopy_delete(path):
    # Last fall back option when system delete fails. Typically when paths are too long
    empty_dir = os.path.join("P:\\", "Kits$", "CompGroup", "ICP", "empty_dir_for_robocopy")
    os.system("robocopy \"{}\" \"{}\" /PURGE /NJH /NJS /NP /NFL /NDL /NS /NC /R:0 /LOG:NUL".format(empty_dir, path))


def rmtree_error(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.
    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.
    If the error is for another reason it re-raises the error.
    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    try:
        if not os.access(path, os.W_OK):
            # Is the error an access error ?
            os.chmod(path, stat.S_IWUSR)
            func(path)
    except Exception as e:
        print("Could not delete file, falling back to robocopy. Exception: \n{}".format(e))
        robocopy_delete(path)


def delete_dir(directory):
    print("Deleting directory: {}".format(directory))
    try:
        # Use prefix \\? with abspath to work for long file names
        shutil.rmtree(os.path.join(r"\\?", directory), onerror=rmtree_error)
    except Exception as e:
        print("Unable to delete directory {}: {}".format(directory, e))


def old_enough_to_delete(f):
    return datetime.now()-datetime.fromtimestamp(os.path.getmtime(f)) > timedelta(days=max_build_age_in_days)


def is_build_dir(d):
    return os.path.isdir(d) and "BUILD" in os.path.split(d)[-1]


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


def check_drive(drive_letter):
    """
    The script assumes that P:\ has been mapped to \isis\inst$. Check to verify that is true
    """
    dirs = os.listdir("{}:\\".format(drive_letter))
    return "Instruments$" in dirs and "Kits$" in dirs


def purge(dry_run=False):
    if not check_drive("P"):
        print("P:\ does not appear to point to \isis\inst$")
        return
    print("Beginning archive purge...")
    build_area = os.path.join("P:\\", "Kits$", "CompGroup", "ICP")
    project_areas = [os.path.join(build_area, proj) for proj in ("Client", "genie_python")] + \
        [os.path.join(build_area, "EPICS", proj) for proj in os.listdir(os.path.join(build_area, "EPICS"))
         if proj.startswith("EPICS")]

    for d in deletion_directories(project_areas):
        if dry_run:
            print("{}".format(d))
        else:
            delete_dir(d)
    print("Archive purge complete.")


purge()
