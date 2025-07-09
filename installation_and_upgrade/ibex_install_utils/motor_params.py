"""
Script to extract information from motors to be consumed by the motion controls team.
Exports data as CSV.
To run, load the script into a genie_python console and run as a standard user script.
"""

import csv
from typing import BinaryIO

from aioca import CANothing, caget
from ibex_install_utils.ca_utils import get_machine_details_from_identifier

VELOCITY_UNITS = "EGU per sec"

PV, AXIS_NAME = "PV", "Axis Name"
SETPOINT, POSITION = "Setpoint", "Position"
OFF = "User Offset"
LOW_LIM, HIGH_LIM = "Soft Low Limit", "Soft High Limit"
VELO, MAX_VELO = f"Velocity ({VELOCITY_UNITS})", f"Max Velocity ({VELOCITY_UNITS})"
ACCEL = "Acceleration (Time to Velocity)"
UNITS = "Units"
MOTOR_RES, INV_MOTOR_RES = "Motor Step Size (EGU per step)", "Motor Step Size (step per EGU)"
ENCODER_RES, INV_ENCODER_RES = (
    "Encoder Step Size (EGU per step)",
    "Encoder Step Size (step per EGU)",
)
DECEL_DIST = "Max Deceleration Distance (EGU)"
P, I, D = "P", "I", "D"  # noqa: E741

K1, K2, K3 = "K1", "K2", "K3"
MTR_TYPE, ENC_TYPE, AUX_ENC_TYPE = "Motor Type", "Encoder Type", "Aux Encoder Type"
ZN, ZP = "Negative Anti-friction Bias", "Positive Anti-friction Bias"
AF, TL = "Analog Feedback", "Torque Limit"
CT, CP, FN, FC = "CT", "CP", "FN", "FC"
FA, FV = "Feedforward Acceleration", "Feedforward Velocity"

output_order = [
    AXIS_NAME,
    PV,
    SETPOINT,
    POSITION,
    UNITS,
    MOTOR_RES,
    INV_MOTOR_RES,
    ENCODER_RES,
    INV_ENCODER_RES,
    VELO,
    MAX_VELO,
    ACCEL,
    DECEL_DIST,
    LOW_LIM,
    HIGH_LIM,
    OFF,
    P,
    I,
    D,
    MTR_TYPE,
    ENC_TYPE,
    AUX_ENC_TYPE,
    K1,
    K2,
    K3,
    ZN,
    ZP,
    AF,
    TL,
    CT,
    CP,
    FN,
    FC,
    FA,
    FV,
]


all_motor_params = {
    AXIS_NAME: ".DESC",
    SETPOINT: ".VAL",
    POSITION: ".RBV",
    UNITS: ".EGU",
    ENCODER_RES: ".ERES",
    MOTOR_RES: ".MRES",
    ACCEL: ".ACCL",
    VELO: ".VELO",
    MAX_VELO: ".VMAX",
    LOW_LIM: ".DLLM",
    HIGH_LIM: ".DHLM",
    OFF: ".OFF",
    P: ".PCOF",
    I: ".ICOF",
    D: ".DCOF",
}

galil_specific_params = {
    MTR_TYPE: "_MTRTYPE_CMD",
    ENC_TYPE: "_MENCTYPE_CMD",
    AUX_ENC_TYPE: "_AENCTYPE_CMD",
    K1: "_K1_SP",
    K2: "_K2_SP",
    K3: "_K3_SP",
    ZP: "_ZP_SP",
    ZN: "_ZN_SP",
    FV: "_FV_SP",
    FA: "_FA_SP",
    FC: "_FC_SP",
    FN: "_FN_SP",
    CP: "_CP_SP",
    CT: "_CT_SP",
    AF: "_AF_SP",
    TL: "_TL_SP",
}


async def get_params_and_save_to_file(
    file_reference: BinaryIO, num_of_controllers: int = 8
) -> None:
    """
    Gets all the motor parameters and saves them to an open file reference as a csv.

    Args:
        file_reference (BinaryIO): The csv file to save the data to.
        num_of_controllers (int, optional): The number of motor controllers on the instrument
    """
    list_of_axis_pvs = []
    _, _, pv_prefix = get_machine_details_from_identifier()

    for motor_controller_num in range(1, num_of_controllers + 1):
        for axis_num in range(1, 9):
            axis_pv = f"{pv_prefix}MOT:MTR{motor_controller_num:02d}{axis_num:02d}"
            list_of_axis_pvs.append(axis_pv)

    rows = []

    for axis_pv in list_of_axis_pvs:
        hr_keys = (
            [axis_pv]
            + [i for i in all_motor_params.keys()]
            + [i for i in galil_specific_params.keys()]
        )
        hr_values = await caget(
            [axis_pv]
            + [axis_pv + i for i in all_motor_params.values()]
            + [axis_pv + i for i in galil_specific_params.values()],
            throw=False,
            timeout=0.1,
        )

        if all(isinstance(i, CANothing) for i in hr_values):
            # All PVs failed to connect so don't bother writing this axis
            continue

        # Sanitising - remove any CANothings and replace with None
        hr_values = [None if isinstance(i, CANothing) else i for i in hr_values]
        out_dict = dict(zip(hr_keys, hr_values))

        out_dict[PV] = axis_pv

        try:
            out_dict[INV_MOTOR_RES] = 1.0 / out_dict[MOTOR_RES]
        except ZeroDivisionError:
            out_dict[INV_MOTOR_RES] = None

        try:
            out_dict[INV_ENCODER_RES] = 1.0 / out_dict[ENCODER_RES]
        except ZeroDivisionError:
            out_dict[INV_ENCODER_RES] = None

        out_dict[DECEL_DIST] = out_dict[MAX_VELO] * out_dict[ACCEL]
        rows.append(out_dict)

    writer = csv.DictWriter(file_reference, output_order, restval="N/A", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
