import json
import io
import os
import mimetypes
import random
import re
import falcon
import cPickle as pickle

from lib.ipfs import IPFSTools
from lib.db import MemeChainDB
from lib.memechain import MemeTx, Validate
from lib.blockchain import get_blockchain_info
from logger import *

# Load configuration file
with open("config.json", "r") as f:
    config = json.loads(f.read())

# Memechain API version
MEMECHAIN_VERSION = '1.0.0'

# Memechain allowed content types
ALLOWED_IMAGE_TYPES = ('image/gif', 'image/jpeg', 'image/png')

def validate_image_type(req, resp, resource, params):
    if req.content_type not in ALLOWED_IMAGE_TYPES:
        logger.error('COMMAND %s Failed %s: %s'
                     % ('validate_image_type', 'Memechain Error',
                        "Meme file extension not supported."))
        raise falcon.HTTPError(falcon.HTTP_400, 'Memechain Error',
                               "Meme file extension not supported.")

def validate_ip_address(req, resp, resource, params):
    if config["ALLOWED_IP_ADDRESSES"]:
        if req.remote_addr not in config["ALLOWED_IP_ADDRESSES"]:
            logger.error('COMMAND %s Failed %s: %s'
                         % ('validate_ip_address', 'Memechain Error',
                            "IP address not allowed."))
            raise falcon.HTTPError(falcon.HTTP_401, 'Memechain Error',
                                   "IP address not allowed.")

class get_info(object):
    def on_get(self, req, resp):
        logger.info('COMMAND %s Received' % self.__class__.__name__)
        db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))

        blockchain_info = get_blockchain_info()
        last_meme_info = db.get_last_meme()
        memechain_height = db.get_memechain_height()
        memechain_block_sync_height = pickle.load(open(os.path.join(config['DATA_DIR'], 'sync.p'), 'rb'))

        resp.status = falcon.HTTP_200
        resp.set_header('Powered-By', 'Memechain')

        logger.info('COMMAND %s Success' % self.__class__.__name__)
        resp.body = json.dumps({
            'success': True,
            'result': {'memechain_version' : MEMECHAIN_VERSION, 
                       'blockchain_height' : blockchain_info['blocks'],
                       'blockchain_balance' : float(blockchain_info['balance']),
                       'memechain_block_sync_height' : memechain_block_sync_height,
                       'memechain_height' : memechain_height,
                       'last_meme_metadata' : last_meme_info}})

class get_memechain_height(object):
    def on_get(self, req, resp):
        logger.info('COMMAND %s Received' % self.__class__.__name__)
        db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))

        height = db.get_memechain_height()

        resp.status = falcon.HTTP_200
        resp.set_header('Powered-By', 'Memechain')

        logger.info('COMMAND %s Success' % self.__class__.__name__)
        resp.body = json.dumps({
            'success': True,
            'result': height})


class get_meme_data_by_height(object):
    def on_get(self, req, resp, height):
        logger.info('COMMAND %s Received' % self.__class__.__name__)
        db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))

        meme_metadata = db.search_by_memechain_height(height)

        if not meme_metadata:
            logger.error('COMMAND %s Failed %s: %s' % (self.__class__.__name__,
                         'Database Error', "Meme not found."))
            raise falcon.HTTPError(falcon.HTTP_404, 'Database Error',
                                   "Meme not found.")

        resp.status = falcon.HTTP_200
        resp.set_header('Powered-By', 'Memechain')

        logger.info('COMMAND %s Success' % self.__class__.__name__)
        resp.body = json.dumps({
            'success': True,
            'result': meme_metadata})


class get_meme_data_by_range(object):
    def on_get(self, req, resp, start, finish):
        logger.info('COMMAND %s Received' % self.__class__.__name__)
        db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))

        memes =[]
        if start > finish:
            direction = -1
        else:
            direction = 1

        for height in range(int(start), int(finish) + 1, direction):
            meme_metadata = db.search_by_memechain_height(height)

            if not meme_metadata:
                logger.error('COMMAND %s Failed %s: %s' % (self.__class__.__name__,
                         'Database Error', "Meme {} not found.".format(height)))
                raise falcon.HTTPError(falcon.HTTP_404, 'Database Error',
                                       "Meme {} not found.".format(height))

            else:
                memes.append(meme_metadata)

        resp.status = falcon.HTTP_200
        resp.set_header('Powered-By', 'Memechain')

        logger.info('COMMAND %s Success' % self.__class__.__name__)
        resp.body = json.dumps({
            'success': True,
            'result': memes})


class get_meme_data_by_hash(object):
    def on_get(self, req, resp, ipfs_id):
        logger.info('COMMAND %s Received' % self.__class__.__name__)
        db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))

        meme_metadata = db.search_by_ipfs_id(ipfs_id)

        if not meme_metadata:
            logger.error('COMMAND %s Failed %s: %s'
                         % (self.__class__.__name__, 'Database Error',
                             "Meme not found."))
            raise falcon.HTTPError(falcon.HTTP_404, 'Database Error',
                                   "Meme not found.")

        resp.status = falcon.HTTP_200
        resp.set_header('Powered-By', 'Memechain')

        logger.info('COMMAND %s Success' % self.__class__.__name__)
        resp.body = json.dumps({
            'success': True,
            'result': meme_metadata})


class get_meme_img_by_height(object):
    def on_get(self, req, resp, height):
        logger.info('COMMAND %s Received' % self.__class__.__name__)
        db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))

        meme_metadata = db.search_by_memechain_height(height)

        # Generate image file path
        name = '{img_name}.{ext}'.format(img_name=meme_metadata["ipfs_id"],
                                        ext=meme_metadata["imgformat"])
        image_path = os.path.join(config['DATA_DIR'], name)

        # Open image file
        stream = io.open(image_path, 'rb')
        stream_len = os.path.getsize(image_path)

        # Generate image response
        resp.status = falcon.HTTP_200
        resp.set_header('Powered-By', 'Memechain')
        resp.content_type = mimetypes.guess_type(name)[0]

        logger.info('COMMAND %s Success' % self.__class__.__name__)
        resp.stream, resp.stream_len = stream, stream_len


class get_meme_img_by_hash(object):
    def on_get(self, req, resp, ipfs_id):
        logger.info('COMMAND %s Received' % self.__class__.__name__)
        db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))

        meme_metadata = db.search_by_ipfs_id(ipfs_id)

        # Generate image file path
        name = '{img_name}.{ext}'.format(img_name=meme_metadata["ipfs_id"],
                                        ext=meme_metadata["imgformat"])
        image_path = os.path.join(config['DATA_DIR'], name)

        # Open image file
        stream = io.open(image_path, 'rb')
        stream_len = os.path.getsize(image_path)

        # Generate image response
        resp.status = falcon.HTTP_200
        resp.set_header('Powered-By', 'Memechain')
        resp.content_type = mimetypes.guess_type(name)[0]

        logger.info('COMMAND %s Success' % self.__class__.__name__)
        resp.stream, resp.stream_len = stream, stream_len


class add_meme(object):
    _CHUNK_SIZE_BYTES = 4096

    @falcon.before(validate_image_type)
    @falcon.before(validate_ip_address)
    def on_post(self, req, resp):
        logger.info('COMMAND %s Received' % self.__class__.__name__)
        db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))

        # Generate random placeholder img name
        img_placeholder_name = str(random.random()).split(".")[1]

        ext = mimetypes.guess_extension(req.content_type)
        if ext == '.jpe':
            ext = '.jpg'

        name = '{img_name}{ext}'.format(img_name=img_placeholder_name, ext=ext)
        image_path = os.path.join(config['DATA_DIR'], name)

        # Write image to local storage
        with io.open(image_path, 'wb') as image_file:
            while True:
                chunk = req.stream.read(self._CHUNK_SIZE_BYTES)
                if not chunk:
                    break

                image_file.write(chunk)

        # Check file size
        meme_filesize = os.path.getsize(image_path) * 0.000001 # in MB

        if meme_filesize > 10:
            os.remove(image_path)
            
            logger.error('COMMAND %s Failed %s: %s'
                         % (self.__class__.__name__, 'Upload Error',
                            "Meme filesize too large."))
            raise falcon.HTTPError(falcon.HTTP_400, "Upload error",
                                   "Meme filesize too large.")

        # Add image to ipfs
        ipfs_id = IPFSTools().add_meme(image_path)['Hash']

        # Rename local img file to ipfs_id for easy reference
        new_name = '{img_name}{ext}'.format(img_name=ipfs_id, ext=ext)
        os.rename(image_path, os.path.join(config['DATA_DIR'], new_name))

        # Add to Kekcoin chain
        memetx = MemeTx(ipfs_id)
        prev_block_memes = db.get_prev_block_memes()

        if prev_block_memes:
            memetx.generate_hashlink(prev_block_memes)

            try:
                Validate(memetx, db=db, ipfs_dir=config['DATA_DIR'],
                         prev_block_memes=prev_block_memes)
            
            except TypeError as e:
                # Delete invalid Meme
                os.remove(os.path.join(config['DATA_DIR'], new_name))

                logger.error('COMMAND %s Failed %s: %s'
                             % (self.__class__.__name__, 'Memechain Error',
                                "Meme has not passed memechain validation, file extension not supported."))
                raise falcon.HTTPError(falcon.HTTP_400, "Memechain error",
                                       "Meme has not passed validation, file extension not supported.")         

            if memetx.is_meme_valid():
                memetx.blockchain_write()

                resp.status = falcon.HTTP_201
                resp.set_header('Powered-By', 'Memechain')

                logger.info('COMMAND %s Success' % self.__class__.__name__)
                resp.body = json.dumps({
                    'success': True,
                    'result': {'ipfs_id' : ipfs_id, 'txid' : memetx.get_txid(), 'hashlink' : memetx.get_hashlink(), 'author' : memetx.get_author()}})

            else:
                # Delete invalid Meme
                os.remove(os.path.join(config['DATA_DIR'], new_name))

                logger.error('COMMAND %s Failed %s: %s'
                             % (self.__class__.__name__, 'Memechain Error',
                                "Meme has not passed memechain validation: "))
                raise falcon.HTTPError(falcon.HTTP_400, "Memechain error",
                                       "Meme has not passed validation: ")
        else:
            # Genesis block logic
            memetx = MemeTx(ipfs_id)
            memetx.generate_genesis_hashlink()

            memetx.blockchain_write()

            resp.status = falcon.HTTP_201
            resp.set_header('Powered-By', 'Memechain')

            logger.info('COMMAND %s Success' % self.__class__.__name__)
            resp.body = json.dumps({
                'success': True,
                'result': {'ipfs_id' : ipfs_id, 'txid' : memetx.get_txid(), 'hashlink' : memetx.get_hashlink(), 'author' : memetx.get_author()}})


# Falcon API
app = application = falcon.API()

# Get node info command
app.add_route('/api/getinfo', get_info())

# Height command
app.add_route('/api/getheight', get_memechain_height())

# Get meme data by height command
app.add_route('/api/getmemedatabyheight/{height}', get_meme_data_by_height())

# Get meme data by range command
app.add_route('/api/getmemedatabyheightrange/{start}-{finish}', get_meme_data_by_range())

# Get meme data by hash command
app.add_route('/api/getmemedatabyhash/{ipfs_id}', get_meme_data_by_hash())

# Get meme img by height command
app.add_route('/api/getmemeimgbyheight/{height}', get_meme_img_by_height())

# Get meme img by hash command
app.add_route('/api/getmemeimgbyhash/{ipfs_id}', get_meme_img_by_hash())

# Add meme command
app.add_route('/api/addmeme', add_meme())