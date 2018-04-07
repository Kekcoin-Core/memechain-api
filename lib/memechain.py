from hashlib import sha256

import op_return

class Validate():
	"""
	Validator class for MemeChainTX object.
	"""
	def __init__(self):
		pass

	def check_cloudvision(self):
		pass

	def is_valid_hash_link(self):
		pass

	def check_ipfs_existance(self):
		pass

	def check_duplicate(self):
		pass


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

