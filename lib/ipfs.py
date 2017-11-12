import ipfsApi
import os
import io

class Tools():
	def __init__(self):
		self.api = ipfsApi.Client('127.0.0.1', 5001)
		try:
			ipfsApi.assert_version(self.api.version()['Version'], minimum='0.4.3', maximum='0.5.0')
		except ipfsApi.exceptions.VersionMismatch:
			return "Please update the IPFS daemon."

	def add_meme(self, filepath):
		#Note: Objects added through ipfs add are pinned recursively by default.
		#Note: Possible to recursively add all memes in a directory - but not implemented. 
		try:
			with open(filepath, 'rb') as f:
				res = self.api.add(f, recursive) 
			return res
		except IOError:
			print("File {0} does not exist and couldn't be added.".format(filepath))
			return False

	def get_meme(self, multihash, subdirectory=None):
		""" 
			Downloads a file, or directory of files from IPFS.
			Files are placed in the current working directory. 
			Args:
				multihash (str) -- The path to the IPFS object(s) to be outputted
				subdirectory (str) -- The subdirectory in which to place the IPFS object(s)
		"""
		try:
			self.api.get(multihash)
			if subdirectory is not None:
				#Add support for other image formats
				os.rename(multihash, subdirectory+'/'+multihash+".jpg")
			elif subdirectory is None:
				os.rename(multihash, multihash+'.jpg')
		except ipfsApi.exceptions.StatusError:
			print("Invalid multihash supplied. File could not be retrieved.")
			return False

	def cat(self, multihash):
		""" 
			Retrieves the contents of a file identified by hash. 
			Arg:	
				multihash (str) -- The path to the IPFS object(s) to be retrieved
			Returns:
				File contents (str)
		"""
		try:
			return self.api.cat(multihash)
		except ipfsApi.exceptions.StatusError:
			print("Invalid multihash supplied. File contents could not be retrieved.")
			return False

	def clear_local_file(self, filepath, recursive=False):
		#Todo: figure out why this raises ipfsApi.exceptions.ErrorResponse but still removes pin.
		
		## These are the functions to perform:
		# self.api.pin_rm(filepath, recursive)
		# return self.api.repo_gc()

		## Since an error is thrown regardless of success or failure I've added a 
		## check to see whether or not the file has actually been unpinned.
		pins = self.api.pin_ls(type='recursive')['Keys']
		if filepath not in pins.keys():
			print("Could not find {0} to remove pin".format(filepath))
			return False

		try:
			self.api.pin_rm(filepath, recursive)
		except ipfsApi.exceptions.ErrorResponse:
			print("Exception ipfsApi.exceptions.ErrorResponse thrown.")
		
		self.api.repo_gc()

		pins = self.api.pin_ls(type='recursive')['Keys']
		if filepath not in pins.keys():
			print("Pin for {0} successfully removed".format(filepath))
			return

	def clear_all_local_files(self):
		# Want to clear locally stored data > remove all pins & garbage collect
		pins = self.api.pin_ls(type='recursive')['Keys']
		for key in pins.keys():
			self.api.pin_rm(path=key, recursive=True)
		return self.api.repo_gc()

	def get_peer_list(self):
		return self.api.swarm_peers()

	def connect_to_peer(self, address):
		#Haven't successfuly connected to a peer yet?
		try:
			return self.api.swarm_connect(address)
		except ipfsApi.exceptions.ErrorResponse:
			print "Connection failure. Connection refused."

	def disconnect_from_peer(self, address):
		""" 
			Arg:
				address: peer address + /ipfs/ + peer hash, i.e.,
						/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYERUEnRQAwe3N8SzbUtfsmvsqQLuvuJ

		"""
		try:
			return self.api.swarm_disconnect(address)
		except ipfsApi.exceptions.ErrorResponse:
			print("Invalid IPFS peer address provided.")
			return False

	def object_put(self, filepath, links):
		#IF we decide to add files as DAG objects
		#assert links = = [{name:, Hash:, size:},...]
		with open(filepath, 'rb') as f:
			# key = self.api.object_put(f)
			data = f

			key = self.api.object_put(io.BytesIO(b'''
       		{
				"Data": "another",
				"Links": [{ 
					"Name": "some link",
					"Hash": "QmS4BzH3XEMnwvv6bjWo5gDVJGf9Hguyq7mr8zFvKdb83V",
					"Size": 8
				}]
			}'''))

		return key

