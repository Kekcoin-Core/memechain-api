import os

from hashlib import sha256

from op_return import *
from ipfs import IPFSTools

class Validate():
	"""
	Validator class for MemeChainTX object.
	"""
	def __init__(self, MemeTX, db_path, ipfs_dir, prev_block_memes):
		
		is_valid = self.check_duplicate(MemeTX.get_ipfs_id(), db_path)
		is_valid = self.check_ipfs_existance(ipfs_id, ipfs_dir)
		is_valid = self.is_valid_hash_link(prev_block_memes)
		#is_valid = check_cloudvision()

		if is_valid:
			MemeTX.set_is_valid()

	#def check_cloudvision(self):
	#	pass

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
		Checks whether the meme represented by the MemeTX exists on IPFS (either locally or globally).
		Args:
			ipfs_id  - attribute of MemeTX
			ipfs_dir - path of directory which contains the locally stored ipfs files
		"""
		if os.path.exists(ipfs_id):
			return False 	 #Meme already exists locally
		else:
			if not IPFSTools().get_meme(ipfs_id, ipfs_dir):
				return True  #Meme does not exist on IPFS yet
			else:
				return False #Meme already exists on global IPFS

	def check_duplicate(self, db_path, ipfs_id):
		"""
		Checks whether a MemeTX with ipfs_id is in MemeChainDB.
		Args:
			db_path - path of MemeChainDB data store
			ipfs_id - attribute of MemeTX
		"""
		db = MemeChainDB(db_path)
		try:
			db.search_by_ipfs_id(ipfs_id)
			return True
		#TODO: specify exception
		except:
			return False

class MemeTX():
	"""
	MemeChain TX object. Used to construct a MemeChainTX.
	"""
	def __init__(self, ipfs_id):
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

	def generate_hashlink(self, prev_block_memes):
		"""
		Method used to generate hash link
		Args:
			prev_block_memes (array of dicts)
		"""
		raw_str = prev_block_memes[0]['hashlink']
		raw_str += ''.join(meme['ipfs_id'] for meme in prev_block_memes)
		self.hashlink = sha256(raw_str)[:16]

