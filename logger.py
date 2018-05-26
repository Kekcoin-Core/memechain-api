import logging, os, json

# Load configuration file
with open("config.json", "r") as f:
	config = json.loads(f.read())

# Logging Code
logger = logging.getLogger('memechain')
hdlr = logging.FileHandler(os.path.join(config['DATA_DIR'], 'debug.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)

#logger.error('We have a problem')
#logger.info('While this is just chatty')