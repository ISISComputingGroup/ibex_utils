import json
import os

import zlib


class CaWrapper(object):
    """
    Wrapper around genie python's channel access class providing some useful abstractions.
    """

    def __init__(self):
        """
        Setting instrument is necessary because genie_python is being run from a network drive so it may not know
        where it is.
        """
        self.g = None

    def _get_genie(self):

        # Do import locally (late) as otherwise it writes logs to c:\instrument\var which interferes with VHD deploy.
        if self.g is not None:
            return self.g

        from genie_python import genie as g
        self.g = g
        self.g.set_instrument(os.getenv("MYPVPREFIX"), import_instrument_init=False)
        return g

    def get_local_pv(self, name):
        """
        Get PV with the local PV prefix appended

        Args:
            name (str): Name of the PV to get.

        Returns:
            None if the PV was not connected
        """
        return self._get_genie().get_pv(name, is_local=True)

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

    def get_blocks(self):
        """
        Returns:
            A collection of blocks, or None if the PV was not connected
        """
        return self._get_genie().get_blocks()

    def cget(self, block):
        """
        Returns:
            A collection of blocks, or None if the PV was not connected.
        """
        return self._get_genie().cget(block)
