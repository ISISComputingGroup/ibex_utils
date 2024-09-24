#
# parse a Galil.ini from SECI and check it against PVs from galil IOC on instrument
#
# You need to have the NDX c$ mapped (i.e. \\ndxYYYY\c$) so it is readable by script 
#
import configparser
import argparse
import os
from genie_python import genie as g

INST = ""

PVPREFIX = ""

CONFIGFILE = ""

SETFILE = None

CHANGEFILE = None

SHOW_VALUE_OK = False

NOCHECK = False

MOTOR_TYPES = { 0 : "Servo", 1 :  "Rev Servo", 2 : "HA Stepper", 3 : "LA Stepper", 4 : "Rev HA Stepper", 5 :  "Rev LA Stepper" }

# seci defines an encoder type for analogue feedback, but epics does not. galil manual is unclear - it suggests you should use
# the normal types here and AF parameter to say if these types receive digital or analogue signals
ENCODER_TYPES = { 0 : "Normal Quadrature", 1 : "Pulse and Dir", 2 : "Reverse Quadrature", 3 : "Rev Pulse and Dir", 4 : "Analogue??" }

HOME_METHODS = { 0 : "none", 1 : "signal", 2 : "reverse limit", 3 : "forward limit" }

def main():
    global INST, PVPREFIX, CONFIGFILE, SHOW_VALUE_OK, SETFILE, CHANGEFILE, NOCHECK
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--inst', help='instrument to check e.g. CRISP (default: local system)', default=None)
        parser.add_argument('--verbose', help='verbose', action='count', default=0)
        parser.add_argument('--setfile', help='name of command file to generate with all values to set', default=None)
        parser.add_argument('--changefile', help='name of command file to generate with changes to values', default=None)
        parser.add_argument('--nocheck', help='do not try and connect to PVs', action='store_true')
        args = parser.parse_args()
        if args.inst is not None:
            INST = args.inst.upper()
            PVPREFIX = f"IN:{INST}:MOT:"
            CONFIGFILE = r"\\NDX{}\c$\LABVIEW MODULES\Drivers\Galil DMC2280\Galil.ini".format(INST)
        else:
            PVPREFIX = os.getenv("MYPVPREFIX") + "MOT:"
            CONFIGFILE = r"c:\LABVIEW MODULES\Drivers\Galil DMC2280\Galil.ini"

        if args.nocheck:
            NOCHECK = args.nocheck
        skips = {}
        skips["velocity"] = False
        skips["direction"] = False
        skips["offset"] = False
        skips["backlash"] = False
        skips["limits"] = False
        skips["acceleration"] = False
        skips["onoff"] = False
        skips["enable"] = False
        skips["ueip"] = False
        skips["edel"] = False
        skips["eguaftlimit"] = False
        skips["spdb"] = False
        if args.setfile:
            SETFILE = open(args.setfile, 'w')
        if args.changefile:
            CHANGEFILE = open(args.changefile, 'w')
        if args.verbose > 0:
            SHOW_VALUE_OK = True
        config = configparser.ConfigParser(interpolation=None)
        config.read(CONFIGFILE)
        for g in config.keys():
            if g == "DEFAULT":
                if len(config[g]) > 0:
                    raise Exception("error - non empty DEFAULT")
                continue
            doController(config[g], g, skips)
    except Exception as ex:
        print(ex)
    if SETFILE is not None:
        SETFILE.close()
    if CHANGEFILE is not None:
        CHANGEFILE.close()

# note key names are lowercased by the parser e.g. use "motor steps per unit", "kp"
# however section names and values preserve case
def doAxis(config, galil, axis, skips):
    mn = motorNumber(galil, axis)    
    msteps_per_unit = config.getfloat(axisItem(axis, 'motor steps per unit'))
    esteps_per_unit = config.getfloat(axisItem(axis, 'encoder steps per unit'))
    eres = 1.0 / esteps_per_unit if esteps_per_unit != 0.0 else 0.0
    mres = 1.0 / msteps_per_unit if msteps_per_unit != 0.0 else 0.0
    speed = config.getfloat(axisItem(axis, 'speed'))
    velo = speed * mres
    accl = config.getfloat(axisItem(axis, 'acceleration'))
    dccl = config.getfloat(axisItem(axis, 'deceleration'))
    edel_multiplier = 2 # encoder steps for edel
    epics_accl = speed / accl if accl != 0.0 else 0.0 # epics acceleration is time to reach velocity
    motor_used = config.getboolean(axisItem(axis, "used"))
    negate_direction = config.getboolean(axisItem(axis, "negate motor direction"))
    
    if not motor_used:
        print(f"INFO: Skipping {mn} as not used in seci")
        return
    
    for item in ['initialisation', 'before move', 'after move', 'move call', 'home call']: # , 'set points'
        value = config.get(axisItem(axis, item))
        if value is not None and value != '""':
            print(f"WARNING: {mn} {item} in seci {galil} axis {axis} is {value}")
    
    # normally like ITA=1\0AKSA=1.313
    init_bits = config.get(axisItem(axis, 'initialisation')).replace('"','').split(r'\0A')
    for init in init_bits:
        if len(init) > 0 and '=' in init:
            (name, value) = init.split('=')
            init_axis = name[2].lower()            
            init_mn = motorNumber(galil, init_axis)   
            item = name[:2]
            if init_axis != axis:
                print(f"WARNING: initialisation string {name} does not refer to current axis")  
            if item == 'IT': 
                doValue(f"{init_mn}_ITCSMOOTH_SP", value, f"{init_mn}_ITCSMOOTH_MON") 
            elif item == 'PL':
                doValue(f"{init_mn}_POLE_SP", value, f"{init_mn}_POLE_MON") 
            elif item == 'KS':
                doValue(f"{init_mn}_STEPSMOOTH_SP", value, f"{init_mn}_STEPSMOOTH_MON") 
            elif item == 'OF':
                doValue(f"{init_mn}_BIASVOLTAGE_SP", value, f"{init_mn}_BIASVOLTAGE_MON") 
            elif item == 'OE':
                doValue(f"{init_mn}_OFFONERR_CMD", value, f"{init_mn}_OFFONERR_STATUS") 
            elif item == 'ER':
                doValue(f"{init_mn}_ERRLIMIT_SP", value, f"{init_mn}_ERRLIMIT_MON") 
            else:
                doValue(f"{init_mn}_{item}_SP", value, f"{init_mn}_{item}_MONITOR")
    if not NOCHECK:
        for item in ['PREM', 'POST', 'INIT']:          
            value = g.get_pv(f"{PVPREFIX}{mn}.{item}")
            if value is not None and value != "":
                print(f"INFO: {PVPREFIX}{mn}.{item} is \"{value}\"")
               
    doValue(f"{mn}.EGU", config.get(axisItem(axis, 'unit label')))
    doValue(f"{mn}.DESC", config.get(axisItem(axis, 'motor name')))
    ueip = config.getboolean(axisItem(axis, 'encoder present'))
    if not skips['ueip']:
        doValue(f"{mn}.UEIP", 'Yes' if ueip else 'No')
    for item in ['k1', 'k2', 'k3', 'zp', 'zn', 'tl', 'ct']:
        uitem = item.upper()
        doValue(f"{mn}_{uitem}_SP", config.getfloat(axisItem(axis, item)), f"{mn}_{uitem}_MONITOR")
    doValue(f"{mn}.PCOF", config.getfloat(axisItem(axis, "kp")) / 1023.875)
    doValue(f"{mn}.ICOF", config.getfloat(axisItem(axis, "ki")) / 2047.875) # note: different scaling would be needed for galil 4000
    doValue(f"{mn}.DCOF", config.getfloat(axisItem(axis, "kd")) / 4095.875)
    doValue(f"{mn}.MRES", mres)
    doValue(f"{mn}.ERES", eres)
    if not skips["edel"]:
        doValue(f"{mn}_EDEL_SP", edel_multiplier * eres, f"{mn}_EDEL_MON") # old galil
        doValue(f"{mn}_ENC_TOLERANCE_SP", edel_multiplier, f"{mn}_ENC_TOLERANCE_MON") # new galil
    hspeed = config.getfloat(axisItem(axis, "home speed"))
    if not skips['velocity']:
        doValue(f"{mn}.VELO", velo)
        doValue(f"{mn}.VMAX", velo)
        doValue(f"{mn}.JVEL", velo)
        doValue(f"{mn}.HVEL", hspeed * mres)
    doValue(f"{mn}.RDBD", config.getfloat(axisItem(axis, "positional accuracy")))
    if not skips["spdb"]:
        doValue(f"{mn}.SPDB", config.getfloat(axisItem(axis, "set-point deadband")))
    if negate_direction:
        print(f"INFO: {mn} has seci negated direction")
    if not skips['direction']:
        doValue(f"{mn}.DIR", "Neg" if negate_direction else "Pos")

    if not skips['acceleration']:
        doValue(f"{mn}.ACCL", epics_accl)
        doValue(f"{mn}.JAR", epics_accl)

    doValue(f"{mn}.RMOD", "Default")
    #doValue(f"{mn}_HOMEVAL_SP", 0)
    doValue(f"{mn}_WLP_CMD", "Off")
    if not skips['onoff']:
        doValue(f"{mn}_OFFDELAY_SP", 2)
        doValue(f"{mn}_ONDELAY_SP", 0)
    doValue(f"{mn}_JAH_CMD", "No")
    
    doValue(f"{mn}_MTRTYPE_CMD", MOTOR_TYPES[config.getint(axisItem(axis, "motor type"))], f"{mn}_MTRTYPE_STATUS")
    doValue(f"{mn}_MENCTYPE_CMD", ENCODER_TYPES[config.getint(axisItem(axis, "encoder type"))], f"{mn}_MENCTYPE_STATUS")
    
    de_energise = config.getboolean(axisItem(axis, "de-energise"))
    if not skips['onoff']:
        doValue(f"{mn}_AUTOONOFF_CMD", "On" if de_energise else "Off", f"{mn}_AUTOONOFF_STATUS")
        doValue(f"{mn}_ON_CMD", "Off" if de_energise else "On", f"{mn}_ON_STATUS")
    
    af = config.getboolean(axisItem(axis, "analog feedback"))
    doValue(f"{mn}_AF_SP", af, f"{mn}_AF_MONITOR") 

    doValue(f"{mn}.RTRY", 10 if ueip and config.getboolean(axisItem(axis, "correct motion")) else 0)
    
    if not skips['enable']:
        doValue(f"{mn}_able", "Enable" if motor_used else "Disable")

    print(f"INFO: {mn} seci home method: ", HOME_METHODS[config.getint(axisItem(axis, "home method"))])

    apply_home = config.getboolean(axisItem(axis, "apply home position"))
    seci_home_pos = config.getfloat(axisItem(axis, "home position"), 0.0)
    seci_home_offset = config.getfloat(axisItem(axis, "home offset"), 0.0)
    seci_offset = config.getfloat(axisItem(axis, "offset"), 0.0)
    seci_user_offset = config.getfloat(axisItem(axis, "user offset"), 0.0)
    print(f"INFO: {mn} seci home position {seci_home_pos} (apply: {apply_home}) home offset {seci_home_offset} offset {seci_offset} user offset {seci_user_offset}")
    if not skips['offset']:
        if apply_home:
            doValue(f"{mn}.OFF", seci_home_pos - seci_offset - seci_user_offset)
        else:
            doValue(f"{mn}.OFF", - seci_offset - seci_user_offset)
        
    eguaft = hspeed * hspeed / dccl / 2.0 / msteps_per_unit
    if not skips["eguaftlimit"]:
        doValue(f"{mn}_EGUAFTLIMIT_SP", eguaft, f"{mn}_EGUAFTLIMIT_MON")
    
    cp = config.getint(axisItem(axis, "CP"))
    if de_energise:
        cp = 0 if cp > 0 else -1
    else:
        cp = -1
    doValue(f"{mn}_CP_SP", cp, f"{mn}_CP_MONITOR")
  
    fbl = config.getfloat(axisItem(axis, "forward backlash"))
    bbl = config.getfloat(axisItem(axis, "backward backlash"))
    stall_error = config.getfloat(axisItem(axis, "stall allowed error"))
    if config.getboolean(axisItem(axis, "stall enable")):
        stall_error = config.getfloat(axisItem(axis, "stall allowed error"))
    else:
        stall_error = max(abs(fbl), abs(bbl))
    stall_time = msteps_per_unit * abs(stall_error) / speed
    doValue(f"{mn}_ESTALLTIME_SP", stall_time if stall_time > 1.2 else 1.2, f"{mn}_ESTALLTIME_MON")

    if config.getboolean(axisItem(axis, "rerun home")):
        print(f"INFO: {mn} rerun home enabled in seci")
    
    backlash = 0    
    if (fbl > 0 and bbl < 0):
        print(f"ERROR: {mn} seci backlash problem - forward > 0 and back < 0")
    if fbl > 0:
        backlash = fbl
    else:
        if bbl <= 0:
            backlash = bbl
        else:
            print(f"ERROR: {mn} seci backlash problem")

    if backlash == 0:
        print(f"INFO: {mn} no backlash defined in SECI, if this is correct then BVEL or BACC mismatches are not critical")
    if not skips["backlash"]:
        doValue(f"{mn}.BVEL", velo / 10.0)
        doValue(f"{mn}.BACC", epics_accl / 10.0)
        doValue(f"{mn}.BDST", -backlash)
    
    smax = config.getfloat(axisItem(axis, "soft max"))
    smax = smax if smax != float('inf') else 0
    smin = config.getfloat(axisItem(axis, "soft min"))
    smin = smin if smin != float('-inf') else 0
    umax = config.getfloat(axisItem(axis, "user max"))
    umin = config.getfloat(axisItem(axis, "user min"))
    if umax is not None and umax != float('inf'):
        print(f"user max defined as {umax} with soft max as {smax}, will use lower value, check that is correct")
        smax = min(smax, umax)
    if umin is not None and umin != float('-inf'):
        print(f"user min defined as {umin} with soft min as {smin}, will use higher value, check that is correct")
        smin = max(smin, umin)
    if (smin > smax):
        print(f"ERROR: SECI min limit {smin} > SECI max limit {smax}, will not adjust limits") 
    elif not skips["limits"]:
        doValue(f"{mn}.HLM", smax)
        doValue(f"{mn}.LLM", smin)
    
# soft min   soft max        home offset     position ref    position      
      #   User Offset      user max    user min   
      # Home - Move Pos        Home - Move After      Axis A Set Points = ""     Axis A Coerce Set Point = FALSE      Exclude Global Move       Stall Enable         Stall Allowed Error
def axisItem(axis, name):  
    return f'axis {axis} {name}'
                    
def doValue(set_pv, value, read_pv=None):
    prefixed_read_pv = "{}{}".format(PVPREFIX, read_pv)
    prefixed_set_pv = "{}{}".format(PVPREFIX, set_pv)
    if isinstance(value, str):
        value = value.replace('"', '')
    if SETFILE is not None:
        SETFILE.write(f"caput {prefixed_set_pv} {value}\n")
        SETFILE.flush()
    if NOCHECK:
        return
    current_sp = g.get_pv(prefixed_set_pv)
    sp_ok = True
    if not compareValues(current_sp, value):
        print("{} SP differs: current \"{}\" != expected \"{}\"".format(prefixed_set_pv, current_sp, value))
        sp_ok = False
        if CHANGEFILE is not None:
            CHANGEFILE.write(f"caput {prefixed_set_pv} {value}\n")
            CHANGEFILE.flush()
    elif SHOW_VALUE_OK:
        print("{} SP OK \"{}\"".format(prefixed_set_pv, current_sp))
    if read_pv is not None:
        current_rbv = g.get_pv(prefixed_read_pv)
        if not compareValues(current_rbv, value):
            if sp_ok:
                print("{} RBV differs (but SP was OK): currrent \"{}\" != expected \"{}\"".format(prefixed_read_pv, current_rbv, value))
            else:
                print("{} RBV differs: currrent \"{}\" != expected \"{}\"".format(prefixed_read_pv, current_rbv, value))
        elif SHOW_VALUE_OK or not sp_ok:
                print("{} RBV OK: \"{}\"".format(prefixed_read_pv, current_rbv))
            

def doController(config, galil, skips):
    cn = controllerNumber(galil)
    enable = config.getboolean("enable")
    address = "<None>"
    if enable:
        print(f"INFO: Seci Controller {galil} -> EPICS DMC{cn} MTR{cn}xx")
        ip = config["ip address"]
        com = config["com port"]
        if not NOCHECK:
            address_pv = "{}{}{}".format(PVPREFIX, dmc(galil), ":ADDRESS_MON")
            address = g.get_pv(address_pv)
        print(f"INFO: SECI ip {ip} COM {com} - current EPICS address {address}") 
        if (config.get("galil init", '""') != '""'):
            print("WARNING: seci galil init is {}, inhibit {}, in {}".format(config["galil init"], config["galil init inhibit"], galil))
        if (config.get("program", '"<Not A Path>"') != '"<Not A Path>"'):
            print("WARNING: seci program is {} in {}".format(config["program"], galil))
        for axis_no in range(8):
            axis = chr(ord('a') + axis_no)
            if config.get(f"axis {axis} motor name") is not None:
                doAxis(config, galil, axis, skips)   
    else:
        print(f"INFO: Skipping Controller {galil} (DMC{cn} MTR{cn}xx) as not enabled in seci")

# G0 -> 01 etc.
def controllerNumber(galil):
    if galil[0] == 'G':
        return "{:02d}".format(int(galil[1]) + 1)

# construct MTRxxyy, axis 'a' -> 01 
def motorNumber(galil, axis):
    return "MTR" + controllerNumber(galil) + "{:02d}".format(ord(axis) - ord('a') + 1)
     
def dmc(galil):
    return "DMC" + controllerNumber(galil)

# return True is same else false
def compareValues(val1, val2):
    tolerance = 0.003
    try:
        v1 = float(val1)
        v2 = float(val2)
        if v1 == v2:
            return True
        if v1 != 0:
            if abs((v1 - v2) / v1) < tolerance:
                return True
        return False

    except:
        if val1 == val2:
            return True
        else:
            return False

main()
