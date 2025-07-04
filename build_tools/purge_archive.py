import glob
import os
import shutil
import stat
from datetime import datetime, timedelta
from typing import Callable

max_build_age_in_days = 7
minimum_number_of_builds_to_keep = 5
build_area = r"\\isis.cclrc.ac.uk\inst$\kits$\CompGroup\ICP"


def winapi_path(dos_path: str) -> str:
    path = os.path.abspath(dos_path)
    long_path_identifier = "\\\\?\\"
    if path.startswith(long_path_identifier):
        win_path = path
    elif path.startswith("\\\\"):
        win_path = long_path_identifier + "UNC\\" + path[2:]
    else:
        win_path = long_path_identifier + path
    return win_path


def rmtree_error(func: Callable[[str], None], path: str, exc_info: tuple) -> None:
    try:
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
        func(winapi_path(path))
    except Exception as e:
        print(f"Unable to delete file: {e}")


def delete_dir(directory: str) -> None:
    print(f"Deleting directory: {directory}")
    try:
        shutil.rmtree(winapi_path(directory), onerror=rmtree_error)
    except Exception as e:
        print(f"Unable to delete directory {directory}: {e}")


def delete_file(file: str) -> None:
    print(f"Deleting file: {file}")
    try:
        os.remove(winapi_path(file))
    except Exception as e:
        print(f"Unable to delete file {file}: {e}")


def old_enough_to_delete(f: str) -> bool:
    return datetime.now() - datetime.fromtimestamp(os.path.getmtime(f)) > timedelta(
        days=max_build_age_in_days
    )


def is_build_dir(d: str) -> bool:
    return os.path.isdir(d) and "BUILD" in os.path.split(d)[-1].upper()


def deletion_directories(project_areas: list[str]) -> list[str]:
    dirs = []
    for project_area in project_areas:
        project_dirs = [os.path.join(project_area, sub_dir) for sub_dir in os.listdir(project_area)]
        build_dirs_by_age = sorted(
            filter(is_build_dir, project_dirs), key=os.path.getmtime, reverse=True
        )
        build_dirs_we_could_delete = build_dirs_by_age[minimum_number_of_builds_to_keep:]
        build_dirs_we_will_delete = filter(old_enough_to_delete, build_dirs_we_could_delete)
        dirs_to_add = list(build_dirs_we_will_delete)
        dirs += dirs_to_add
        print(f"Identifying {len(dirs_to_add)} old builds for deletion in: {project_area}")
    return dirs


def deletion_files(project_areas: list[str], pattern: str) -> list[str]:
    files = []
    for project_area in project_areas:
        files_by_age = sorted(
            glob.glob(os.path.join(project_area, pattern)), key=os.path.getmtime, reverse=True
        )
        files_we_could_delete = files_by_age[minimum_number_of_builds_to_keep:]
        files_we_will_delete = filter(old_enough_to_delete, files_we_could_delete)
        files_to_add = list(files_we_will_delete)
        files += files_to_add
        print(
            f"Identifying {len(files_to_add)} old {pattern} files for deletion in: {project_area}"
        )
    return files


def purge(dry_run: bool = False) -> None:
    print("Beginning archive purge...")
    project_areas = [
        os.path.join(build_area, proj)
        for proj in ("Client_E4", "Client_E4_win11", "script_generator", "genie_python_3", "VHDS")
    ] + [
        os.path.join(build_area, "EPICS", proj)
        for proj in os.listdir(os.path.join(build_area, "EPICS"))
        if proj.startswith("EPICS")
    ]
    project_areas.extend(
        [
            os.path.join(build_area, "developer", "EPICS", proj)
            for proj in os.listdir(os.path.join(build_area, "developer", "EPICS"))
            if proj.startswith("windows")
        ]
    )
    project_areas.extend(
        [
            os.path.join(build_area, "developer", "EPICS32", proj)
            for proj in os.listdir(os.path.join(build_area, "developer", "EPICS32"))
            if proj.startswith("win32")
        ]
    )
    for d in deletion_directories(project_areas):
        try:
            if dry_run:
                print(f"{d}")
            else:
                delete_dir(d)
        except Exception as e:
            print(f"Unable to delete directory {d}: {e}")
        except BaseException as be:
            print(f"BaseException - unable to delete directory {d}: {be}")
            break
    for f in deletion_files(project_areas, "ZBUILD-*.7z"):
        try:
            if dry_run:
                print(f"{f}")
            else:
                delete_file(f)
        except Exception as e:
            print(f"Unable to delete file {f}: {e}")
        except BaseException as be:
            print(f"BaseException - unable to delete file {f}: {be}")
            break
    print("Archive purge complete.")


purge()
