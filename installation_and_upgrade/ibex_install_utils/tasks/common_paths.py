import os

INSTRUMENT_BASE_DIR = os.path.join("C:\\", "Instrument")
APPS_BASE_DIR = os.path.join(INSTRUMENT_BASE_DIR, "Apps")
VAR_DIR = os.path.join(INSTRUMENT_BASE_DIR, "var")
INST_SHARE_AREA = os.path.join(r"\\isis.cclrc.ac.uk", "inst$")

SETTINGS_CONFIG_FOLDER = os.path.join("Settings", "config")
SETTINGS_CONFIG_PATH = os.path.join(INSTRUMENT_BASE_DIR, SETTINGS_CONFIG_FOLDER)

EPICS_PATH = os.path.join(APPS_BASE_DIR, "EPICS")
EPICS_UTILS_PATH = os.path.join(APPS_BASE_DIR, "EPICS_UTILS")

BACKUP_DATA_DIR = os.path.join("C:\\", "data")
BACKUP_DIR = os.path.join(BACKUP_DATA_DIR, "old")
STAGE_DELETED = os.path.join(INST_SHARE_AREA, "backups$", "stage-deleted")

PYTHON_PATH = os.path.join(APPS_BASE_DIR, "Python")
PYTHON_3_PATH = os.path.join(APPS_BASE_DIR, "Python3")


GUI_PATH = os.path.join(APPS_BASE_DIR, "Client")
GUI_PATH_E4 = os.path.join(APPS_BASE_DIR, "Client_E4")
