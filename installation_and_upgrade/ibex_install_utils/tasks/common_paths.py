import os

INSTRUMENT_BASE_DIR = os.path.join("C:\\", "Instrument")
APPS_BASE_DIR = os.path.join(INSTRUMENT_BASE_DIR, "Apps")
VAR_DIR = os.path.join(INSTRUMENT_BASE_DIR, "var")
INST_SHARE_AREA = os.path.join(r"\\isis.cclrc.ac.uk", "inst$")

SETTINGS_DIR = os.path.join(INSTRUMENT_BASE_DIR, "Settings")
SETTINGS_CONFIG_FOLDER = os.path.join("Settings", "config")
SETTINGS_CONFIG_PATH = os.path.join(INSTRUMENT_BASE_DIR, SETTINGS_CONFIG_FOLDER)

AUTOSAVE = os.path.join(VAR_DIR, "Autosave")
"""Path to the autosave directory."""

EPICS_PATH = os.path.join(APPS_BASE_DIR, "EPICS")
EPICS_IOC_PATH = os.path.join(EPICS_PATH, "ioc", "master")
EPICS_UTILS_PATH = os.path.join(APPS_BASE_DIR, "EPICS_UTILS")

BACKUP_DATA_DIR = os.path.join("C:\\", "data")
BACKUP_DIR = os.path.join(BACKUP_DATA_DIR, "old")
STAGE_DELETED = os.path.join(INST_SHARE_AREA, "backups$", "stage-deleted")

PYTHON_PATH = os.path.join(APPS_BASE_DIR, "Python")
PYTHON_3_PATH = os.path.join(APPS_BASE_DIR, "Python3")

GUI_PATH = os.path.join(APPS_BASE_DIR, "Client_E4")

THIRD_PARTY_INSTALLERS_DIR = os.path.join(r"\\isis.cclrc.ac.uk", "shares", "ISIS_Experiment_Controls_Public", "third_party_installers")