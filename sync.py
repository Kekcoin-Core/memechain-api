from logger import *
import os
import json

from lib.db import MemeChainDB
from lib.blockchain import *
from lib.memechain import MemeTx, Validate
from lib.ipfs import IPFSTools

# Load configuration file
with open("config.json", "r") as f:
    config = json.loads(f.read())

class GenesisMeme(MemeTx):
    def __init__(self):
        # Genesis Meme Constants
        self.genesis_ipfs_id = ''
        self.genesis_kekcoin_block = 400000
        self.genesis_txid = ''
        self.genesis_img_format = 'png'

        self.ipfs_id = genesis_ipfs_id
        self.generate_genesis_hashlink()

class MemechainParser(object):
    """
    Wrapper class for various blockchain parsing functions
    used to construct the local memechain metadata database
    """

    def __init__(self, block_height):
        self.block_height = block_height
        self.memetxs = []

    def collect_memetxs(self):
        """
        Method used to parse the op_return data
        for the transactions in the block
        """
        block_txs = get_block_txs(block_height)

        for txid in block_txs:
            memetx = get_op_return_data(txid)
            self.parse_memetx(memetx, txid)

    def parse_memetx(self, memetx, txid):
        """
        Method used to parse the raw memetx metadata
        """
        if memetx[:4] == '3ae4':
            ipfs_id = memetx[4:][:len(memetx) - 4 - 16]
            hashlink = memetx[4:][len(memetx) - 4 - 16:]

            self.memetxs.append({
                'ipfs_id': ipfs_id,
                'hashlink': hashlink,
                'txid' : txid
            })

    def return_memetxs(self):
        """
        Method used to return the potentially valid memetxs

        Returns:
                Memetxs at block_height (array)
        """
        return self.memetxs

def sync_block(db, block):
    parser = MemechainParser(block)
    parser.collect_memetxs()

    memetxs = parser.return_memetxs()

    if memetxs:
        prev_block_memes = db.get_prev_block_memes()

        for meme in memetxs:
            memetx = MemeTx(meme['ipfs_id'])
            memetx.generate_hashlink(prev_block_memes)

            Validate(memetx, db=db, ipfs_dir=config['DATA_DIR'],
                prev_block_memes=prev_block_memes)
            
            if memetx.is_meme_valid():
                meme_filepath = IPFSTools().get_meme(ipfs_id, config['DATA_DIR'])
                ext = meme_filepath.split(".")[-1]

                if ext in ["jpg", "png", "gif"]:
                    db.add_meme({"ipfs_id": meme['ipfs_id'], "hashlink": meme['hashlink'],
                                     "txid": meme['txid'], "block": block, "imgformat": ext})

                    logger.info('COMMAND %s Success %s: %s' % ('Sync', 'Memechain', "Meme %s added to database." % meme['ipfs_id']))

                else:
                    logger.info('COMMAND %s Failed %s: %s' % ('Sync', 'Memechain', "Invalid Meme image extension %s" % ext)) 
            
            else:
                logger.info('COMMAND %s Failed %s: %s' % ('Sync', 'Memechain', "Invalid MemeTx %s" % meme['ipfs_id'])) 

    else:
        logger.info('COMMAND %s Failed %s: %s' % ('Sync', 'Memechain', "No Meme TXs found in block %s." % block))

if __name__ == '__main__':
    # Load database
    db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))
    
    # Check blockheight
    block_height = get_block_height()
    
    if db.get_memechain_height() == 0:
        # Load genesis meme
        genesis_meme = GenesisMeme()

        # Add genesis meme to database
        db.add_meme({"ipfs_id": genesis_meme.get_ipfs_id(), "hashlink": genesis_meme.get_hashlink(),
                         "txid": genesis_meme.genesis_txid, "block": genesis_meme.genesis_kekcoin_block, "imgformat": genesis_meme.genesis_img_format})

        if genesis_meme.genesis_kekcoin_block < block_height:
            for block in range(genesis_meme.genesis_kekcoin_block, block_height):
                sync_block(db, block)

        else:
            logger.error('COMMAND %s Failed %s: %s' % ('Sync', 'Blockchain Error', "Kekcoin blockchain syncing..."))

    else:
        last_meme = db.search_by_memechain_height(-1)

        if last_meme['block'] < block_height:
            for block in range(last_meme['block'], block_height):
                sync_block(db, block)

        else:
            logger.error('COMMAND %s Failed %s: %s' % ('Sync', 'Blockchain Error', "Kekcoin blockchain syncing..."))

