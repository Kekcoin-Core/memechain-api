import json
import io
import os
import mimetypes
import random
import re
import falcon

from lib.ipfs import IPFSTools
from lib.db import MemeChainDB
from lib.memechain import MemeTx, Validate
from logger import *

# Load configuration file
with open("config.json", "r") as f:
    config = json.loads(f.read())


class get_info(object):
    def on_get(self, req, resp):
        pass


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
    _IMAGE_NAME_PATTERN = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-' +
                                     '[0-9a-f]{4}-[0-9a-f]{12}\.[a-z]{2,4}$')

    def on_get(self, req, resp, height):
        logger.info('COMMAND %s Received' % self.__class__.__name__)
        db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))

        meme_metadata = db.search_by_memechain_height(height)

        # Generate image file path
        name = '{img_name}{ext}'.format(img_name=meme_metadata["ipfs_id"],
                                        ext=meme_metadata["imgformat"])
        image_path = os.path.join(config['DATA_DIR'], name)

        if not self._IMAGE_NAME_PATTERN.match(name):
            # 404 Not found response
            logger.error('COMMAND %s Failed %s: %s'
                         % (self.__class__.__name__, 'Database Error',
                            "Meme not found."))
            raise falcon.HTTPError(falcon.HTTP_404, 'Database Error',
                                   "Meme not found.")

        else:
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
    _IMAGE_NAME_PATTERN = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-' +
                                     '[0-9a-f]{4}-[0-9a-f]{12}\.[a-z]{2,4}$')

    def on_get(self, req, resp, ipfs_id):
        logger.info('COMMAND %s Received' % self.__class__.__name__)
        db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))

        meme_metadata = db.search_by_ipfs_id(ipfs_id)

        # Generate image file path
        name = '{img_name}{ext}'.format(img_name=meme_metadata["ipfs_id"],
                                        ext=meme_metadata["imgformat"])
        image_path = os.path.join(config['DATA_DIR'], name)

        if not self._IMAGE_NAME_PATTERN.match(name):
            # 404 Not found response
            logger.error('COMMAND %s Failed %s: %s'
                         % (self.__class__.__name__, 'Database Error',
                            "Meme not found."))
            raise falcon.HTTPError(falcon.HTTP_404, 'Database Error',
                                   "Meme not found.")

        else:
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
    _ALLOWED_IMAGE_TYPES = ('image/gif', 'image/jpeg', 'image/png')

    def validate_image_type(self, req, resp, resource, params):
        if req.content_type not in self._ALLOWED_IMAGE_TYPES:
            logger.error('COMMAND %s Failed %s: %s'
                         % (self.__class__.__name__, 'Memechain Error',
                            "Meme file extension not supported."))
            raise falcon.HTTPError(falcon.HTTP_400, 'Memechain Error',
                                   "Meme file extension not supported.")

    @falcon.before(validate_image_type)
    def on_post(self, req, resp):
        logger.info('COMMAND %s Received' % self.__class__.__name__)
        db = MemeChainDB(os.path.join(config['DATA_DIR'], 'memechain.json'))

        # Generate random placeholder img name
        img_placeholder_name = random.random().split(".")[1]
        ext = mimetypes.guess_extension(req.content_type)
        name = '{img_name}{ext}'.format(img_name=img_placeholder_name, ext=ext)
        image_path = os.path.join(config['DATA_DIR'], name)

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
        os.rename(image_path, os.path.join(config['DATA_DIR'], new_name))

        # Add to Kekcoin chain
        memetx = MemeTx(ipfs_id)
        prev_block_memes = db.get_prev_block_memes()

        if prev_block_memes:
            memetx.generate_hashlink(prev_block_memes)

            Validate(memetx, db=db, ipfs_dir=config['DATA_DIR'],
                     prev_block_memes=prev_block_memes)

            if memetx.is_meme_valid():
                memetx.blockchain_write()

                resp.status = falcon.HTTP_201
                resp.set_header('Powered-By', 'Memechain')

                logger.info('COMMAND %s Success' % self.__class__.__name__)
                resp.body = json.dumps({
                    'success': True,
                    'result': ipfs_id})

            else:
                logger.error('COMMAND %s Failed %s: %s'
                             % (self.__class__.__name__, 'Memechain Error',
                                "Meme has not passed memechain validation."))
                raise falcon.HTTPError(falcon.HTTP_400, "Memechain error",
                                       "Meme has not passed " +
                                       " validation.")

        else:
            # Genesis block logic
            memetx = MemeTx(ipfs_id)
            meme.generate_genesis_hashlink()

            memetx.blockchain_write()

            resp.status = falcon.HTTP_201
            resp.set_header('Powered-By', 'Memechain')

            logger.info('COMMAND %s Success' % self.__class__.__name__)
            resp.body = json.dumps({
                'success': True,
                'result': ipfs_id})


class add_authored_meme(object):
    def on_post(self, req, resp):
        pass


# Falcon API
app = falcon.API()

# Get node info command
app.add_route('/api/getinfo', get_info())

# Height command
app.add_route('/api/getheight', get_memechain_height())

# Get meme data by height command
app.add_route('/api/getmemedatabyheight/{height}', get_meme_data_by_height())

# Get meme data by hash command
app.add_route('/api/getmemedatabyhash/{ipfs_id}', get_meme_data_by_hash())

# Get meme img by height command
app.add_route('/api/getmemeimgbyheight/{height}', get_meme_img_by_height())

# Get meme img by hash command
app.add_route('/api/getmemeimgbyhash/{ipfs_id}', get_meme_img_by_hash())

# Add meme command
app.add_route('/api/addmeme', add_meme())

# Add authored meme command
app.add_route('/api/addauthoredmeme', add_authored_meme())


# For development purposes only
if __name__ == '__main__':
    from wsgiref import simple_server

    httpd = simple_server.make_server('127.0.0.1', 1337, app)
    print("Running Memechain dev server...")
    httpd.serve_forever()
