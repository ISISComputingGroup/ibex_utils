import json
import os

import zlib

import six
from genie_python import genie as g


class CaWrapper(object):
    """
    Wrapper around genie python's channel access class providing some useful abstractions.
    """

    def __init__(self):
        """
        Setting instrument is necessary because genie_python is being run from a network drive so it may not know
        where it is.
        """
        g.set_instrument(os.getenv("MYPVPREFIX"), import_instrument_init=False)

    def get_local_pv(self, name):
        """
        Get PV with the local PV prefix appended

        Args:
            name (str): Name of the PV to get.

        Returns:
            None if the PV was not connected
        """
        return g.get_pv(name, is_local=True)

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
            return json.loads(zlib.decompress(data.decode('hex')))

    @six.wraps(g.get_blocks)
    def get_blocks(self):
        """
        Returns:
            A collection of blocks, or None if the PV was not connected
        """
        return g.get_blocks()

    @six.wraps(g.cget)
    def cget(self, block):
        """
        Returns:
            A collection of blocks, or None if the PV was not connected.
        """
        return g.cget(block)
