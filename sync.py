from logger import *
import os, json

from lib.db import MemeChainDB
from lib.op_return import *
from lib.memechain import MemeTx, Validate

# Load configuration file
with open("config.json", "r") as f:
	config = json.loads(f.read())

class SyncTools():
	"""
	Wrapper class for various syncing functions
	"""
	def __init__(self):
		pass

if __name__ == '__main__':
	# Sync logic
	pass