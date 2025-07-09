import json
import zlib
from ast import literal_eval
from socket import gethostname
from typing import Any, List

import epicscorelibs.path.pyepics  # noqa: F401
import numpy as np
from epics import caget, caput

from ibex_install_utils.file_utils import FileUtils


def crc8(value: str) -> str:
    """
    Generate a CRC 8 from the value (See EPICS\\utils_win32\\master\\src\\crc8.c).

    Args:
        value: the value to generate a CRC from

    Returns:
        string: representation of the CRC8 of the value; two characters

    """
    if value == "":
        return ""

    crc_size = 8
    maximum_crc_value = 255
    generator = 0x07

    as_bytes = value.encode("utf-8")

    crc = 0  # start with 0 so first byte can be 'xored' in

    for byte in as_bytes:
        crc ^= byte  # XOR-in the next input byte

        for i in range(8):
            # unlike the c code we have to artifically restrict the
            # maximum value wherever it is caluclated
            if (crc >> (crc_size - 1)) & maximum_crc_value != 0:
                crc = ((crc << 1 & maximum_crc_value) ^ generator) & maximum_crc_value
            else:
                crc <<= 1

    return "{0:02X}".format(crc)


def dehex_and_decompress(value: bytes | str) -> str:
    """
    Dehex and decompress a string and return it
    :param value: compressed hexed string
    :return: value as a strinnng
    """
    if isinstance(value, bytes):
        # If it comes as bytes then cast to string
        value = value.decode("utf-8")

    return zlib.decompress(bytes.fromhex(value)).decode("utf-8")


def dehex_decompress_and_dejson(value: str | bytes) -> Any:  # noqa: ANN401
    """
    Convert string from zipped hexed json to a python representation
    :param value: value to convert
    :return: python representation of json
    """
    return json.loads(dehex_and_decompress(value))


def _get_pv_prefix(instrument: str, is_instrument: bool) -> str:
    """
    Create the pv prefix based on instrument name and whether it is an
    instrument or a dev machine

    Args:
        instrument: instrument name
        is_instrument: True is an instrument; False not an instrument

    Returns:
        string: the PV prefix
    """
    clean_instrument = instrument
    if clean_instrument.endswith(":"):
        clean_instrument = clean_instrument[:-1]
    if len(clean_instrument) > 8:
        clean_instrument = clean_instrument[0:6] + crc8(clean_instrument)

    instrument_name = clean_instrument

    if is_instrument:
        pv_prefix_prefix = "IN"
    else:
        pv_prefix_prefix = "TE"
    return "{prefix}:{instrument}:".format(prefix=pv_prefix_prefix, instrument=instrument_name)


def get_machine_details_from_identifier(
    machine_identifier: str | None = None,
) -> tuple[str, str, str]:
    """
    Gets the details of a machine by looking it up in the instrument list first.
    If there is no match it calculates the details as usual.

    Args:
        machine_identifier: should be the pv prefix but also accepts instrument name;
        if none defaults to computer host name

    Returns:
        The instrument name, machine name and pv_prefix based in the machine identifier
    """
    instrument_pv_prefix = "IN:"
    test_machine_pv_prefix = "TE:"

    instrument_machine_prefixes = ["NDX", "NDE"]
    test_machine_prefixes = ["NDH"]

    if machine_identifier is None:
        machine_identifier = gethostname()

    # machine_identifier needs to be uppercase for both 'NDXALF' and 'ndxalf' to be valid
    machine_identifier = machine_identifier.upper()

    # get the dehexed, decompressed list of instruments from the PV INSTLIST
    # then find the first match where pvPrefix equals the machine identifier
    # that's been passed to this function if it is not found instrument_details will be None
    instrument_details = None
    instlist_raw = caget("CS:INSTLIST")
    if instlist_raw is not None and isinstance(instlist_raw, np.ndarray):
        instrument_list = dehex_decompress_and_dejson(
            instlist_raw.tobytes().decode().rstrip("\x00")
        )
        instrument_details = next(
            (inst for inst in instrument_list if inst["pvPrefix"] == machine_identifier), None
        )
    else:
        print("Error getting instlist, \nContinuing execution...")

    if instrument_details is not None:
        instrument = instrument_details["name"]
    else:
        instrument = machine_identifier.upper()
        for p in (
            [instrument_pv_prefix, test_machine_pv_prefix]
            + instrument_machine_prefixes
            + test_machine_prefixes
        ):
            if machine_identifier.startswith(p):
                instrument = machine_identifier.upper()[len(p) :].rstrip(":")
                break

    if instrument_details is not None:
        machine = instrument_details["hostName"]
    elif machine_identifier.startswith(instrument_pv_prefix):
        machine = "NDX{0}".format(instrument)
    elif machine_identifier.startswith(test_machine_pv_prefix):
        machine = instrument
    else:
        machine = machine_identifier.upper()

    is_instrument = any(
        machine_identifier.startswith(p)
        for p in instrument_machine_prefixes + [instrument_pv_prefix]
    )
    pv_prefix = _get_pv_prefix(instrument, is_instrument)

    return instrument, machine, pv_prefix


class CaWrapper:
    """
    Wrapper around genie python's channel access class providing some useful abstractions.
    """

    def __init__(self) -> None:
        """
        Get the current PV prefix.
        """
        _, _, self.prefix = get_machine_details_from_identifier()

    def get_local_pv(self, name: str) -> str | int | float | None:
        """
        Get PV with the local PV prefix appended

        Args:
            name (str): Name of the PV to get.

        Returns:
            None if the PV was not connected
        """
        return caget(f"{self.prefix}{name}")  # type: ignore

    def get_object_from_compressed_hexed_json(self, name: str) -> bytes | None:
        """
        Gets an object from a compressed hexed json PV

        Args:
            name (str): Name of the PV to get

        Returns:
            None if the PV was not available, otherwise the decoded json object
        """
        data = self.get_local_pv(name)
        if data is None:
            return None
        else:
            return FileUtils.dehex_and_decompress(data)

    def get_blocks(self) -> List[str]:
        """
        Returns:
            A collection of blocks, or None if the PV was not connected
        """
        blocks_hexed = caget(f"{self.prefix}CS:BLOCKSERVER:BLOCKNAMES")
        if blocks_hexed is None:
            raise Exception("Error getting blocks from blockserver PV.")
        return literal_eval(FileUtils.dehex_and_decompress(blocks_hexed.tobytes()).decode())

    def cget(self, block: str) -> str | int | float | None:
        """
        Returns:
            A collection of blocks, or None if the PV was not connected.
        """
        return caget(f"{self.prefix}CS:SB:{block}")  # type: ignore

    def set_pv(self, pv: str, value: str | float | int, is_local: bool = False) -> None:
        """
        Sets the value of a PV.
        """
        if is_local:
            caput(f"{self.prefix}{pv}", value)
        else:
            caput(pv, value)
