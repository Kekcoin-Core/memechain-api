from logger import *
import os
import json

from lib.db import MemeChainDB
from lib.blockchain import *
from lib.memechain import MemeTx, Validate

# Load configuration file
with open("config.json", "r") as f:
    config = json.loads(f.read())


class MemechainParser(object):
    """
    Wrapper class for various blockchain parsing functions
    used to construct the local memechain metadata database
    """

    def __init__(self, block_height):
        self.block_height = block_height
        self._memetxs_raw = []
        self.memetxs = []

    def collect_memetxs(self):
        """
        Method used to parse the op_return data
        for the transactions in the block
        """
        block_txs = get_block_txs(block_height)

        for txid in block_txs:
            memetx = get_op_return_data(txid)
            self._memetxs_raw.append(memetx)

    def parse_memetxs(self):
        """
        Method used to parse the raw memetx metadata
        """
        for memetx in self._memetxs_raw:
            if memetx[:4] == '3ae4':
                ipfs_id = memetx[4:][:len(memetx) - 4 - 16]
                hashlink = memetx[4:][len(memetx) - 4 - 16:]

                self.memetxs.append({
                    'ipfs_id': ipfs_id,
                    'hashlink': hashlink
                })

    def return_memetxs(self):
        """
        Method used to return the potentially valid memetxs

        Returns:
                Memetxs at block_height (array)
        """
        return self.memetxs


if __name__ == '__main__':
    # Sync logic
    pass
