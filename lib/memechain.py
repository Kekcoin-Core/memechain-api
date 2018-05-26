import os
from hashlib import sha256
from blockchain import *
from ipfs import IPFSTools


class Validate(object):
    """
    Validator class for MemeChainTX object.
    """
    def __init__(self, MemeTX, db, ipfs_dir, prev_block_memes):
        is_valid = [self.check_duplicate(MemeTX.get_ipfs_id(), db),
                    self.check_ipfs_existance(ipfs_id, ipfs_dir),
                    self.is_valid_hash_link(prev_block_memes),
                    self.check_cloudvision()]

        if False not in is_valid:
            MemeTX.set_is_valid()

    def check_cloudvision(self):
        return False

    def is_valid_hash_link(self, prev_block_memes):
        """
        Compares the MemeTX hashlink with the expected hashlink.
        Args:
                prev_block_memes (array of dicts)
        """
        raw_str = prev_block_memes[0]['hashlink']
        raw_str += ''.join(meme['ipfs_id'] for meme in prev_block_memes)
        hashlink = sha256(raw_str)[:16]
        if hashlink != MemeTX.get_hashlink():
            return False
        else:
            return True

    def check_ipfs_existance(self, ipfs_id, ipfs_dir):
        """
                Checks whether the meme represented by the MemeTX exists
                on IPFS (either locally or globally).
                Args:
                        ipfs_id  - attribute of MemeTX
                        ipfs_dir - path of directory which contains the
                                   locally stored ipfs files
        """
        if os.path.exists(ipfs_id):
            return False  # Meme already exists locally
        else:
            # IPFS Tools should be instanciated.
            ipfs = IPFSTools()
            if not ipfs.get_meme(ipfs_id, ipfs_dir):
                return True  # Meme does not exist on IPFS yet
            else:
                return False  # Meme already exists on global IPFS

    def check_duplicate(self, db, ipfs_id):
        """
        Checks whether a MemeTX with ipfs_id is in MemeChainDB.
        Args:
                db_path - path of MemeChainDB data store
                ipfs_id - attribute of MemeTX
        """
        try:
            db.search_by_ipfs_id(ipfs_id)
            return True
        # TODO: specify exception
        except:
            return False


class MemeTx(object):
    """
    MemeChain TX object. Used to construct a MemeChainTX.
    """

    def __init__(self, ipfs_id):
        # Identifier is first 4 letters of the SHA256 hash of KEK
        self._identifier = '3ae4'
        self.ipfs_id = ipfs_id
        self._is_valid = False

    def set_is_valid(self):
        self._is_valid = True

    def is_meme_valid(self):
        return self._is_valid

    def get_ipfs_id(self):
        return self.ipfs_id

    def get_img_hash(self):
        """
        SHA2-256 hash of image
        """
        return self.ipfs_id[2:]

    def get_txid(self):
        return self.txid

    def get_hashlink(self):
        return self.hashlink

    def set_hashlink(self, hashlink):
        self.hashlink = hashlink

    def generate_genesis_hashlink(self):
        self.hashlink = sha256(self.ipfs_id)[:16]

    def generate_hashlink(self, prev_block_memes):
        """
        Method used to generate hash link
        Args:
                prev_block_memes (array of dicts)
        """
        raw_str = prev_block_memes[0]['hashlink']
        raw_str += ''.join(meme['ipfs_id'] for meme in prev_block_memes)
        self.hashlink = sha256(raw_str)[:16]

    def blockchain_write(self):
        if "hashlink" not in locals().keys():
            raise ValueError("Hashlink has not been generated.")
        else:
            rawtx = create_raw_op_return_transaction(
                self._identifier + self.ipfs_id + self.hashlink)
            signedtx = sign_raw_transaction(rawtx)
            self.txid = send_raw_transaction(signedtx)
