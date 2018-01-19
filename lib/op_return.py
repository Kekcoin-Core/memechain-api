"""
Basic OP_RETURN data storage tool for MemeChain.
"""

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import logging
import time
import math
from binascii import hexlify, unhexlify
from hashlib import sha256

try:
	import cPickle as pickle
except:
	import pickle

# Debug settings
debug = True
if debug:
	logging.basicConfig()
	logging.getLogger("BitcoinRPC").setLevel(logging.DEBUG)

# RPC Configuration
rpc_user = "user"
rpc_pass = "password"
rpc_port = "13377"


class Document():
	def __init__(self, data):
		# RPC Connection
		self.rpc = AuthServiceProxy(("http://%s:%s@127.0.0.1:%s/") % (rpc_user, rpc_pass, rpc_port))
		self.data = data

	def store_data(self, change_address):
		# Check if there are inputs
		if not change_address:
			raise Exception("Please enter a change address!")
		if not self.data:
			raise Exception("Please enter data to store!")
		# Define satoshi
		self.SATOSHI = 0.0001
		# Test and mold the data
		if len(self.data) > 351:
			raise Exception("You shall not pass.")
		dataChunks = list(enumerate(self.data[0 + i:39 + i] for i in range(0, len(self.data), 39)))
		print dataChunks
		blockHeight = self.rpc.getblockcount()
		blockHeightID = str(int(blockHeight) + 1)
		first_bytes = []
		first_bytes_str = ""
		# Create OP_RETURN transactions
		for i in dataChunks:
			si = list(i)
			si = str(si[0] + 1) + si[1]
			# Split inputs to avoid burning many coins into the void
			self.split_inputs(math.ceil(float(len(self.data) / 40)), change_address)
			time.sleep(5)
			# Get the inputs
			self.get_inputs()
			time.sleep(1)
			# Form and submit transactions
			first_bytes.append(
				self.create_transaction(self.txid, self.vout, self.input_address, change_address, self.change_amount,
										si)[:12])
		# Form the Data ID
		for s in first_bytes:
			first_bytes_str += s
		self.ID = blockHeightID + first_bytes_str
		return self.ID

	# Create OP_RETURN raw function
	def create_transaction(self, txidin, vout, input, change, changeamt, data):
		tx = self.rpc.createrawtransaction([{"txid": txidin, "vout": vout}], {input: self.SATOSHI, change: changeamt})
		oldScriptPubKey = tx[len(tx) - 60:len(tx) - 8]
		newScriptPubKey = "6a" + hexlify(chr(len(data))) + hexlify(data)
		newScriptPubKey = hexlify(chr(len(unhexlify(newScriptPubKey)))) + newScriptPubKey
		if oldScriptPubKey not in tx:
			print tx
			raise Exception("Something broke!")
		tx = tx.replace(oldScriptPubKey, newScriptPubKey)
		print self.rpc.decoderawtransaction(tx)
		tx = self.rpc.signrawtransaction(tx)['hex']
		tx = self.rpc.sendrawtransaction(tx)
		return tx

	# Get split inputs raw function
	def get_inputs(self):
		# Get unspent transactions
		unspent = self.rpc.listunspent()
		# Put the unspent transactions to the test
		for tx in unspent:
			print float(tx["amount"])
			if float(tx["amount"]) == 0.001:
				self.txid = tx["txid"]
				self.vout = tx["vout"]
				self.input_address = tx["address"]
				self.input_amount = float(tx["amount"])
				self.change_amount = self.input_amount - 0.0003
				break
		else:
			raise Exception("No proper inputs!")

	def split_inputs(self, split_qty, input_address_split):
		if int(split_qty) != 0:
			for i in range(int(split_qty)):
				self.rpc.sendtoaddress(input_address_split, 0.001)
		else:
			self.rpc.sendtoaddress(input_address_split, 0.001)
