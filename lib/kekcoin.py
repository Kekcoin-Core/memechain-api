from OP_RETURN import OP_RETURN_store

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


class MemeChainTX():
	"""
	MemeChain TX object. Used to construct a MemeChainTX.
	"""
	def __init__(self, ipfs_id, img_hash, hashlink):
		self.ipfs_id = ipfs_id
		self.img_hash = img_hash
		self.hashlink + hashlink

		self._is_valid = False
	
	def meme_is_valid(self):
		self._is_valid = True

	def is_meme_valid(self):
		return self._is_valid

	def ipfs_id(self):
		return self.ipfs_id

	def img_hash(self):
		return self.img_hash

	def hash_link(self, cur_meme_id, prev_meme_ids = []):
		"""
		This function takes as input the IPFS ID of the new meme to add to the chain, and computes the hash of it 
		concatenated with each of the previous meme hashes in an order specified by the _order_equilevel_memes() function.
		This hash, the 'hash link', is returned.
		"""
		prev_meme_ids = _order_equilevel_memes(prev_meme_ids)
		string = ''
		for item in prev_meme_ids:
			string += item
		hashable = cur_meme_id + string
		self.hashlink = hash(hashable)
		return self.hashlink

	def _order_equilevel_memes(ipfs_ids = []):
		"""
		Take as input memechain ipfs IDs from a given block, as it appears on the blockchain, and order it alphanumerically,
		i.e. a,b,c,.....,y,z,0,1,2,...,9. The ordering is returned as a list of IPFS IDs [<ipfs ID>, <ipfs ID>, ...].
		"""
		#all ipfs id's are the same length, 46 characters. So:
		#compare elements in the strings until one of them is greater/lower than the others
		ordered_ids = []
		temp = []
		for i in range(0,45):
			for item in ipfs_ids:
				temp.append(item[0])
			lowest_char = min(temp)
			
	def store(data, testnet = False):
		OP_RETURN_store(data, testnet):



