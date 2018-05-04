import logging, json, io, os, mimetypes, random

import falcon

from lib.ipfs import IPFSTools
from lib.db import MemeChainDB

# Logging Code
logger = logging.getLogger('memechain')
hdlr = logging.FileHandler('./data/debug.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

#logger.error('We have a problem')
#logger.info('While this is just chatty')

class getMemeChainHeight(object):
	def on_get(self, req, resp):
		db = MemeChainDB('data/memechain.json')

		height = db.get_height()

		resp.status = falcon.HTTP_200  # This is the default status
		resp.set_header('Powered-By', 'MemeChain')

		resp.body = json.dumps({
			'success' : True,
			'result' : height
			})

class getMemeDataByHeight(object):
	def on_get(self, req, resp, height):
		db = MemeChainDB('data/memechain.json')

		meme_metadata = db.search_by_height(height)

		resp.status = falcon.HTTP_200  # This is the default status
		resp.set_header('Powered-By', 'MemeChain')

		resp.body = json.dumps({
			'success' : True,
			'result' : meme_metadata
			})

class getMemeDataByHash(object):
	def on_get(self, req, resp, ipfs_id):
		db = MemeChainDB('data/memechain.json')

		meme_metadata = db.search_by_ipfs_id(ipfs_id)

		resp.status = falcon.HTTP_200  # This is the default status
		resp.set_header('Powered-By', 'MemeChain')

		resp.body = json.dumps({
			'success' : True,
			'result' : meme_metadata
			})

class getMemeImgByHeight(object):
	def on_get(self, req, resp):
		pass

class getMemeImgByHash(object):
	def on_get(self, req, resp):
		pass

class addMeme(object):
	_CHUNK_SIZE_BYTES = 4096
	def on_post(self, req, resp):
		# Generate random placeholder img name
		img_placeholder_name = random.random().split(".")[1]
		ext = mimetypes.guess_extension(req.content_type)
		name = '{img_name}{ext}'.format(img_name=img_placeholder_name, ext=ext) 
		image_path = os.path.join("./data", name)

		# Write image to local storage
		with io.open(image_path, 'wb') as image_file:
			while True:
				chunk = req.stream.read(self._CHUNK_SIZE_BYTES)
				if not chunk:
					break

				image_file.write(chunk)

		# Add image to ipfs
		ipfs_id = IPFSTools().add_meme(imgage_path)['Hash']

		# Rename local img file to ipfs_id for easy reference
		new_name = '{img_name}{ext}'.format(img_name=ipfs_id, ext=ext)
		os.rename(image_path, os.path.join("./data", new_name))
		
		# Add to kekcoin chain
		###

        resp.status = falcon.HTTP_201


class addAuthoredMeme(object):
	def on_post(self, req, resp):
		pass


# Falcon API
app = falcon.API()

# Height command
app.add_route('/api/getheight', getMemeChainHeight())

# Get meme data by height command
app.add_route('/api/getmemedatabyheight/{height}', getMemeDataByHeight())

# Get meme data by hash command
app.add_route('/api/getmemedatabyhash/{ipfs_id}', getMemeDataByHash())

# Get meme img by height command
app.add_route('/api/getmemeimgbyheight/{height}', getMemeImgByHeight())

# Get meme img by hash command
app.add_route('/api/getmemeimgbyhash/{ipfs_id}', getMemeImgByHash())

# Add meme command
app.add_route('/api/addmeme', addMeme())

# Add authored meme command
app.add_route('/api/addauthoredmeme', addAuthoredMeme())


## For development purposes only ## 
if __name__ == '__main__':
	from wsgiref import simple_server

	httpd = simple_server.make_server('127.0.0.1', 1337, app)
	httpd.serve_forever()