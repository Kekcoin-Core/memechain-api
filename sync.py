from logger import *
import os
import json
import cPickle as pickle

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
        self.genesis_ipfs_id = 'Qme7cKNGn2UgvvEbFSbu8qJ1oS7FcecUyQ8jT8EXW2zoJE'
        self.genesis_kekcoin_block = 585937
        self.genesis_txid = '6c50161c998473d9ef4c7a5df15cb1b0593f321d36da86dd6d716c5cb51ecdde'
        self.genesis_author = 'KP84V1wwcguCDf2PZYbkaWFnhUBAHc1sNu'
        self.genesis_img_format = 'jpg'

        self.ipfs_id = self.genesis_ipfs_id
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
        block_txs = get_block_txs(self.block_height)

        for txid in block_txs:
            memetx, author = get_op_return_data(txid)
            
            if memetx:
                self.parse_memetx(memetx, txid, author)

    def parse_memetx(self, memetx, txid, author):
        """
        Method used to parse the raw memetx metadata
        """
        # Identifier
        if memetx[:4] == '3ae4':
            # Command bytes
            if memetx[4:6] =='00':

                ipfs_id = memetx[6:][:len(memetx) - 6 - 16]
                hashlink = memetx[6:][len(memetx) - 6 - 16:]

                self.memetxs.append({
                    'ipfs_id': ipfs_id,
                    'hashlink': hashlink,
                    'txid' : txid,
                    'author' : author
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
            memetx.txid = meme['txid']

            Validate(memetx, db=db, ipfs_dir=config['DATA_DIR'],
                prev_block_memes=prev_block_memes, sync=True)
            
            if memetx.is_meme_valid():
                meme_filepath = IPFSTools().get_meme(meme['ipfs_id'], config['DATA_DIR'])
                ext = meme_filepath.split(".")[-1]

                if ext in ["jpg", "png", "gif"]:
                    db.add_meme(**{"ipfs_id": meme['ipfs_id'], "hashlink": meme['hashlink'],
                                     "txid": meme['txid'], "author": meme['author'], "block": block, "imgformat": ext})

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
        db.add_meme(**{"ipfs_id": genesis_meme.get_ipfs_id(), "hashlink": genesis_meme.get_hashlink(),
                         "txid": genesis_meme.genesis_txid, "author": genesis_meme.genesis_author, "block": genesis_meme.genesis_kekcoin_block, "imgformat": genesis_meme.genesis_img_format})

        # Sync loop
        if genesis_meme.genesis_kekcoin_block < block_height:
            for block in range(genesis_meme.genesis_kekcoin_block + 1, block_height + 1):
                sync_block(db, block)

            # Dump current sync height into a pickle
            pickle.dump(block_height, open(os.path.join(config['DATA_DIR'], 'sync.p'), 'wb'))

        else:
            logger.error('COMMAND %s Failed %s: %s' % ('Sync', 'Blockchain Error', "Kekcoin blockchain syncing..."))

    else:
        # Load last synced height
        try:
            synced_height = pickle.load(open(os.path.join(config['DATA_DIR'], 'sync.p'), 'rb'))
        except IOError as e:
            last_meme = db.get_last_meme()
            synced_height = last_meme['block']

        # Sync loop
        if synced_height < block_height:
            for block in range(synced_height + 1, block_height + 1):
                sync_block(db, block)

            # Dump current sync height into a pickle
            pickle.dump(block_height, open(os.path.join(config['DATA_DIR'], 'sync.p'), 'wb'))

        else:
            logger.error('COMMAND %s Failed %s: %s' % ('Sync', 'Blockchain Error', "Kekcoin blockchain syncing..."))

