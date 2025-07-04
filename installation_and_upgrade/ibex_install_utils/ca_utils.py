import json
import os
import zlib
from ast import literal_eval
from typing import Any
from socket import gethostname
from ibex_install_utils.file_utils import FileUtils

from epics import caget

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


def dehex_decompress_and_dejson(value: str | bytes) -> Any:  # No known type
    """
    Convert string from zipped hexed json to a python representation
    :param value: value to convert
    :return: python representation of json
    """
    return json.loads(dehex_and_decompress(value))

def _get_pv_prefix(self, instrument: str, is_instrument: bool) -> str:
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

    self.instrument_name = clean_instrument

    if is_instrument:
        pv_prefix_prefix = "IN"
        print("THIS IS %s!" % self.instrument_name.upper())
    else:
        pv_prefix_prefix = "TE"
        print("THIS IS %s! (test machine)" % self.instrument_name.upper())
    return "{prefix}:{instrument}:".format(
        prefix=pv_prefix_prefix, instrument=self.instrument_name
    )


def _get_machine_details_from_identifier(
        self, machine_identifier: str | None
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
    input_list = caget("CS:INSTLIST")
    if input_list is not None:
        assert isinstance(input_list, str | bytes)
        instrument_list = dehex_decompress_and_dejson(input_list)
        instrument_details = next(
            (inst for inst in instrument_list if inst["pvPrefix"] == machine_identifier), None
        )
    else:
        print(
            "Error getting instlist, \nContinuing execution..."
        )

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
                instrument = machine_identifier.upper()[len(p):].rstrip(":")
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
    pv_prefix = self._get_pv_prefix(instrument, is_instrument)

    return instrument, machine, pv_prefix


class CaWrapper:
    """
    Wrapper around genie python's channel access class providing some useful abstractions.
    """

    def __init__(self):
        """
        Setting instrument is necessary because genie_python is being run from a network drive so it may not know
        where it is.
        """
        self.prefix, _, _ = _get_machine_details_from_identifier()

    def get_local_pv(self, name):
        """
        Get PV with the local PV prefix appended

        Args:
            name (str): Name of the PV to get.

        Returns:
            None if the PV was not connected
        """
        return caget(f"{self.prefix}{name}")

    def get_object_from_compressed_hexed_json(self, name):
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

    def get_blocks(self):
        """
        Returns:
            A collection of blocks, or None if the PV was not connected
        """
        #TODO implement this
        blocks_hexed = caget(f"{self.prefix}CS:SB:BLOCKNAMES")
        return literal_eval(FileUtils.dehex_and_decompress(blocks_hexed).decode())


    def cget(self, block):
        """
        Returns:
            A collection of blocks, or None if the PV was not connected.
        """
        return caget(f"{self.prefix}CS:SB:{block}")

    def set_pv(self, *args, **kwargs):
        """
        Sets the value of a PV.
        """
        return self._get_genie().set_pv(*args, **kwargs)
