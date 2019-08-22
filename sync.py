from logger import *
import os
import json
import pickle as pickle
import time
from lib.db import MemeChainDB
from lib.blockchain import *
from lib.memechain import MemeTx, Validate
from lib.ipfs import IPFSTools
import psutil

# Load configuration file
with open("config.json", "r") as f:
    config = json.loads(f.read())

class GenesisMeme(MemeTx):
    def __init__(self):
        # Genesis Meme Constants
        self.genesis_ipfs_id = 'QmUNCRjfvVts5kdxNJTQvTABE8AKPUFDyYsjqefFj2bEbG'
        self.genesis_kekcoin_block = 947594
        self.genesis_txid = '36ee54a262ee65ca54e41baf1298cc7f6aa1f3c6a29fb79c4ab75582ee6ec9af'
        self.genesis_author = 'KVsKHQbuoKUgHNaFm4jZKZVHDAKPPCvwbr'
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
            valid_state = memetx.is_meme_valid()
            if valid_state == -1:
                meme_filepath = IPFSTools().get_meme(meme['ipfs_id'], config['DATA_DIR'])
                ext = meme_filepath.split(".")[-1]

                if db.search_by_ipfs_id(meme['ipfs_id']):
                    db.update_meme(meme['ipfs_id'], block)
                    logger.info('COMMAND %s Success %s: %s' % (
                    'Sync', 'Memechain', "Meme %s update in database." % meme['ipfs_id']))
                else:
                    db.add_meme(**{"ipfs_id": meme['ipfs_id'], "hashlink": meme['hashlink'],
                                     "txid": meme['txid'], "author": meme['author'], "block": block, "imgformat": ext, "status": "confirm"})
                    logger.info('COMMAND %s Success %s: %s' % ('Sync', 'Memechain', "Meme %s added to database." % meme['ipfs_id']))
            elif valid_state != 3:
                meme_filepath = IPFSTools().get_meme(meme['ipfs_id'], config['DATA_DIR'])
                os.remove(meme_filepath)
                logger.info('COMMAND %s Failed %s: %s' % ('Sync', 'Memechain', "Invalid MemeTx %s." % meme['ipfs_id'])) 

    else:
        if config["ENABLE_LOG_MEMTX_NOT_FOUND"]:
            logger.info('COMMAND %s Failed %s: %s' % ('Sync', 'Memechain', "No Meme TXs found in block %s." % block))

def check_files_status(db):
    for file in os.listdir(config['DATA_DIR']):
        if file.endswith(tuple(config["ALLOWED_IMAGE_EXTENSIONS"])):
            if db.search_by_ipfs_id(file.split(".")[0]) is None:
                os.remove(os.path.join(config['DATA_DIR'], file))
                logger.info('COMMAND %s Failed %s: %s' % ('Sync', 'Memechain', "Remove file from data folder (not exist in db)  %s." % file))

    for meme in db.get_all_memes():
        if not os.path.isfile(os.path.join(config['DATA_DIR'], meme["ipfs_id"] + "." + meme["imgformat"])):
            logger.info('COMMAND %s Failed %s: %s' % (
            'Sync', 'Memechain', "File not  found in data folder (exist in db)  %s." % meme["ipfs_id"]))
            ipfs = IPFSTools()
            ipfs.get_meme(meme["ipfs_id"], config['DATA_DIR'])
            logger.info('COMMAND %s Info %s: %s' % ('Sync', 'Memechain', "Try downloading missing file with id  %s." % meme["ipfs_id"]))


def check_running():
    counter = 0
    for q in psutil.process_iter():
        if q.name().find('sync'):
            if len(q.cmdline())>1 and 'sync.py' in q.cmdline()[1]:
                counter = counter + 1
    if counter > 1:
        return True
    else:
        return False



if __name__ == '__main__':
    # Load database
    db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))



    if not config["MULTIPLE_SYNC_RUNNING"] and check_running():
        logger.info('COMMAND %s Failed %s: %s' % ('Sync', 'Memechain', "Sync process already running.Shutdown current sync"))
        sys.exit(1)

    if config["CHECK_FILES_ON_RUNNING"]:
        check_files_status(db)

    # Check blockheight
    block_height = get_block_height()
    
    if db.get_memechain_height() == 0:
        # Load genesis meme
        genesis_meme = GenesisMeme()

        memetx = MemeTx(genesis_meme.genesis_ipfs_id)
        memetx.generate_genesis_hashlink()
        memetx.txid = genesis_meme.genesis_txid
      
        Validate(memetx, db=db, ipfs_dir=config['DATA_DIR'],
            prev_block_memes=[], sync=True, genesis=True)
        # Add genesis meme to database


        db.add_meme(**{"ipfs_id": genesis_meme.get_ipfs_id(), "hashlink": genesis_meme.get_hashlink(),
                         "txid": genesis_meme.genesis_txid, "author": genesis_meme.genesis_author, "block": genesis_meme.genesis_kekcoin_block, "imgformat": genesis_meme.genesis_img_format, "status": "confirm"})

        # Sync loop
        if genesis_meme.genesis_kekcoin_block < block_height:
            block = genesis_meme.genesis_kekcoin_block + 1
            max_errors = 0
            while block < block_height + 1:
                try:
                    sync_block(db, block)
                except IOError as e:
                    logger.error('COMMAND %s Failed %s: %s' % ('Sync', 'Memechain', "Invalid ipfs multihash.%s") % e)
                    if max_errors < 10:
                        time.sleep(10)
                        block = block - 1
                        max_errors = max_errors + 1
                    else:
                        max_errors = 0
                except KeyboardInterrupt:
                    # Dump current sync height into a pickle
                    pickle.dump(block, open(os.path.join(config['DATA_DIR'], 'sync.p'), 'wb'))
                block = block + 1

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
        
        if synced_height-10 < block_height:
            block = synced_height-10 + 1
            max_errors = 0
            while block < block_height + 1:
                try:
                    sync_block(db, block)
                except IOError as e:
                    logger.error('COMMAND %s Failed %s: %s' % ('Sync', 'Memechain', "Invalid ipfs multihash.%s") % e)
                    if max_errors < 10:
                        time.sleep(10)
                        block = block - 1
                        max_errors = max_errors + 1
                    else:
                        max_errors = 0
                except KeyboardInterrupt:
                    # Dump current sync height into a pickle
                    pickle.dump(block, open(os.path.join(config['DATA_DIR'], 'sync.p'), 'wb'))
                block = block + 1

            # Dump current sync height into a pickle
            pickle.dump(block_height, open(os.path.join(config['DATA_DIR'], 'sync.p'), 'wb'))

        else:
            logger.error('COMMAND %s Failed %s: %s' % ('Sync', 'Blockchain Error', "Kekcoin blockchain syncing..."))

