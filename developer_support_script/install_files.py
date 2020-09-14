"""
Look at the size of

"""
import getpass
import os
import subprocess
from six.moves import input

areas = {
    "config": r"{INST_PATH}\Settings\config\{HOST_NAME}\configurations",
    "Autosave": r"{INST_PATH}\var\autosave",
    "logs-other": r"{INST_PATH}\var\logs",
    "logs-conserver": r"{INST_PATH}\var\logs\conserver",
    "logs-ioc": r"{INST_PATH}\var\logs\ioc",
    "mysql-alarm": r"{INST_PATH}\var\mysql\Data\alarm",
    "mysql-archive": r"{INST_PATH}\var\mysql\Data\archive",
    "mysql-exp_data": r"{INST_PATH}\var\mysql\Data\exp_data",
    "mysql-iocdb": r"{INST_PATH}\var\mysql\Data\iocdb",
    "mysql-journal": r"{INST_PATH}\var\mysql\Data\journal",
    "mysql-msg_log": r"{INST_PATH}\var\mysql\Data\msg_log",
    "mysql-mysql": r"{INST_PATH}\var\mysql\Data\mysql",
    "mysql-performance_schema": r"{INST_PATH}\var\mysql\Data\performance_schema",
    "mysql-sys": r"{INST_PATH}\var\mysql\Data\sys",
    "gui": r"{INST_PATH}\Apps\Client\workspace"
}

files_in_dir = {
    "mysql_files": r"{INST_PATH}\var\mysql\Data"
}

FNULL = open(os.devnull, 'w')


class CalibrationsFolder(object):
    """
    Context manager for accessing calibration folders on remote instruments.
    """

    DRIVE_LETTER = "q"

    @staticmethod
    def disconnect_from_drive():
        """
        Returns: True if disconnect is successful, else False.
        """
        return subprocess.call(['net', 'use', f'{CalibrationsFolder.DRIVE_LETTER}:', '/del', '/y'],
                               stdout=FNULL, stderr=FNULL) == 0

    def connect_to_drive(self):
        """
        Returns: True if the connection is successful, else False
        """
        print("connecting")
        net_use_cmd_line = ['net', 'use', f'{CalibrationsFolder.DRIVE_LETTER}:', self.network_location,
                            f'/user:{self.username_with_domain}', self.password]
        return subprocess.call(net_use_cmd_line,
                               stdout=FNULL, stderr=FNULL) == 0

    def __init__(self, instrument_host, username, password):
        self.username_with_domain = f"{instrument_host}\\{username}"
        self.network_location = r'\\{}\c$\Instrument'.format(instrument_host)
        self.password = password

    def __enter__(self):
        """
        Returns: A git repository for the remote calibration folder if connection is successful, else None.
        """
        self.connect_to_drive()
        return self

    def __exit__(self, *args):
        self.disconnect_from_drive()


def bytes_to_mb(size_in_bytes):
    return size_in_bytes / 1024.0 / 1024.0


def size_of_files_in_dir(path):
    size = 0
    for f in os.listdir(path):
        full_path = os.path.join(path, f)
        size += os.path.getsize(full_path)
    return size


def size_of_dir_tree(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def get_for_instrument(instrument_host, username, password):
    with CalibrationsFolder(instrument_host, username, password) as repo:
        templates = {"HOST_NAME": instrument_host,
                     "INST_PATH": f"{repo.DRIVE_LETTER}:\\"}

        sizes = {}

        for name, templated_path in files_in_dir.items():
            path = templated_path.format(**templates)
            sizes[name] = size_of_files_in_dir(path)

        for name, templated_path in areas.items():
            path = templated_path.format(**templates)
            sizes[name] = size_of_dir_tree(path)

        try:
            sizes["logs-other"] -= sizes["logs-conserver"] + sizes["logs-ioc"]
        except KeyError:
            print("Error: One of logs-conserver or logs-ioc no longer exists!")

        return sizes


if __name__ == "__main__":
    username = input("Enter username (no domain): ")
    password = getpass.getpass("Enter password: ")

    all_sizes = {}
    inst_names = []

    for index, inst in enumerate(["NDXSANDALS", "NDXVESUVIO", "NDXZOOM", "NDXALF", "NDXEMMA-A", "NDXENGINX", "NDXGEM",
                                  "NDXHRPD", "NDXIMAT", "NDXIRIS", "NDXLARMOR", "NDEMUONFE", "NDXMERLIN", "NDXPOLARIS"]):
        print(f"-- {inst} --")
        sizes = get_for_instrument(inst, username, password)
        print(sizes)
        inst_names.append(inst)

        for name, size in sizes.items():
            try:
                inst_vals = all_sizes[name]
            except KeyError:
                inst_vals = []
                for i in range(index):
                    inst_vals.append(None)
                all_sizes[name] = inst_vals
            inst_vals.append(size)

    print("{:20},{}".format("File type", ",".join(inst_names)))
    for name, inst_sizes in sorted(all_sizes.items(), key=lambda x: x[0]):
        sizes_from_all_instruments = ", ".join(["{:10.1f}".format(bytes_to_mb(size)) for size in inst_sizes])
        print("{:20},{}".format(name, sizes_from_all_instruments))
