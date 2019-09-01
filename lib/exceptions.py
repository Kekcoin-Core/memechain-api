class InvalidExtensionError(Exception):
	def __init__(self, arg):
		self.strerror = arg

class InvalidMultihashError(Exception):
	def __init__(self, arg):
		self.strerror = arg

class InvalidDownloadError(Exception):
	def __init__(self, arg):
		self.strerror = arg