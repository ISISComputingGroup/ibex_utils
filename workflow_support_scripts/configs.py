"""
Static variables used for calibration file conversion
"""

from datetime import date


class Constants:
    """constants used by conversion scripts"""
    WIKIURL = "https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Calibration-Files"
    ENCODING = "utf-8"


class FileTypes:
    """ File types used by conversion scripts"""
    ORIGINAL_CURVE_FILE_EXTENSION = ".curve"
    ORIGINAL_DAT_FILE_EXTENSION = ".dat"
    OUTPUT_FILE_EXTENSION = ".txt"


class ISISCalibration:
    """ Headers used by conversion scripts to meet IBEX calibration files format requirements """
    isis_calibration_rhfe = {
        "ISIS calibration":
            {
                "sensor_type": "RhFe",
                "format_version": "1",
                "conversion_date": date.today(),
                "column1_name": "Temp",
                "column1_units": "K",
                "column2_name": "Measurement",
                "column2_units": "Ohms"
            }
    }
