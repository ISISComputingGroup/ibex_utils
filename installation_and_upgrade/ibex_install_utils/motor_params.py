"""
Script to extract information from motors to be consumed by the motion controls team. Exports data as CSV. To run,
load the script into a genie_python console and run as a standard user script.
"""

import csv
import multiprocessing
from genie_python import genie as g

g.set_instrument(None, import_instrument_init=False)

VELOCITY_UNITS = "EGU per sec"

PV, AXIS_NAME = "PV", "Axis Name"
SETPOINT, POSITION = "Setpoint", "Position"
OFF = "User Offset"
LOW_LIM, HIGH_LIM = "Soft Low Limit", "Soft High Limit"
VELO, MAX_VELO = f"Velocity ({VELOCITY_UNITS})", f"Max Velocity ({VELOCITY_UNITS})"
ACCEL = "Acceleration (Time to Velocity)"
UNITS = "Units"
MOTOR_RES, INV_MOTOR_RES = "Motor Step Size (EGU per step)", "Motor Step Size (step per EGU)"
ENCODER_RES, INV_ENCODER_RES = "Encoder Step Size (EGU per step)", "Encoder Step Size (step per EGU)"
DECEL_DIST = "Max Deceleration Distance (EGU)"
P, I, D = "P", "I", "D"

K1, K2, K3 = "K1", "K2", "K3"
MTR_TYPE, ENC_TYPE, AUX_ENC_TYPE = "Motor Type", "Encoder Type", "Aux Encoder Type"
ZN, ZP = "Negative Anti-friction Bias", "Positive Anti-friction Bias"
AF, TL = "Analog Feedback", "Torque Limit"
CT, CP, FN, FC = "CT", "CP", "FN", "FC"
FA, FV = "Feedforward Acceleration", "Feedforward Velocity"

output_order = [AXIS_NAME, PV, SETPOINT, POSITION, UNITS, MOTOR_RES, INV_MOTOR_RES, ENCODER_RES, INV_ENCODER_RES, VELO,
                MAX_VELO, ACCEL, DECEL_DIST, LOW_LIM, HIGH_LIM, OFF, P, I, D, MTR_TYPE, ENC_TYPE, AUX_ENC_TYPE, K1, K2,
                K3, ZN, ZP, AF, TL, CT, CP, FN, FC, FA, FV]


all_motor_params = {AXIS_NAME: ".DESC", SETPOINT: ".VAL", POSITION: ".RBV",  UNITS: ".EGU", ENCODER_RES: ".ERES",
                    MOTOR_RES: ".MRES", ACCEL: ".ACCL", VELO: ".VELO", MAX_VELO: ".VMAX", LOW_LIM: ".DLLM",
                    HIGH_LIM: ".DHLM", OFF: ".OFF", P: ".PCOF", I: ".ICOF", D: ".DCOF"}

galil_specific_params = {MTR_TYPE: "_MTRTYPE_CMD", ENC_TYPE: "_MENCTYPE_CMD", AUX_ENC_TYPE: "_AENCTYPE_CMD",
                         K1: "_K1_SP", K2: "_K2_SP", K3: "_K3_SP", ZP: "_ZP_SP", ZN: "_ZN_SP",
                         FV: "_FV_SP", FA: "_FA_SP", FC: "_FC_SP", FN: "_FN_SP",
                         CP: "_CP_SP", CT: "_CT_SP", AF: "_AF_SP", TL: "_TL_SP"}


def pv_exists(pv):
    """
    Gets whether a pv exists.

    Args:
        pv (string): The PV to check.

    Returns:
        True if the PV exists, False otherwise
    """
    return True if g.get_pv(pv) is not None else False


def get_params_for_one_axis(axis, data):
    """
    Gets all the interesting parameters for one axis

    Args:
        axis (string): The PV of the axis.

    Returns:
        Dict containing the data for each axis
    """
    if pv_exists(axis):
        print(f"Gathering data for {axis}", flush=True)
    else: 
        return 
    
    axis_values = {name: g.get_pv(axis + pv) for name, pv in all_motor_params.items()}
    axis_values[PV] = axis

    try:
        axis_values[INV_MOTOR_RES] = 1.0 / axis_values[MOTOR_RES]
    except ZeroDivisionError:
        axis_values[INV_MOTOR_RES] = None

    try:
        axis_values[INV_ENCODER_RES] = 1.0 / axis_values[ENCODER_RES]
    except ZeroDivisionError:
        axis_values[INV_ENCODER_RES] = None

    axis_values[DECEL_DIST] = axis_values[MAX_VELO]*axis_values[ACCEL]
    if pv_exists(axis + "_MTRTYPE_CMD"):
        axis_values.update({name: g.get_pv(axis + pv) for name, pv in galil_specific_params.items()})
    else:
        print("Assuming not a GALIL")

    data.append(axis_values)


def get_params_and_save_to_file(file_reference, num_of_controllers=8):
    """
    Gets all the motor parameters and saves them to an open file reference as a csv.

    Args:
        file_reference (BinaryIO): The csv file to save the data to.
        num_of_controllers (int, optional): The number of motor controllers on the instrument (default is 8)
    """
    motor_processes = []
    manager = multiprocessing.Manager()
    data = manager.list()
    for motor in range(1, num_of_controllers+1):
        for axis in range(1, 9):
            axis_pv = g.prefix_pv_name("MOT:MTR{:02d}{:02d}".format(motor, axis))
            motor_processes.append(multiprocessing.Process(target=get_params_for_one_axis, args=(axis_pv, data)))
            
               

    for process in motor_processes:
        process.start()
        

    for process in motor_processes:
        process.join()

    writer = csv.DictWriter(file_reference, output_order, restval="N/A", extrasaction='ignore')
    writer.writeheader()
    writer.writerows(data)


def get_params_and_save(file_name, num_of_controllers=8):
    """
    Gets all the motor parameters and saves them to a file by name as a csv.

    Args:
        file_name: name of the file to save to
        num_of_controllers (int, optional): The number of motor controllers on the instrument (default is 8)
    """
    with open(file_name, "w") as f:
        get_params_and_save_to_file(f, num_of_controllers)
