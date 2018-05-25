import logging

# Logging Code
logger = logging.getLogger('memechain')
hdlr = logging.FileHandler('./data/debug.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

#logger.error('We have a problem')
#logger.info('While this is just chatty')