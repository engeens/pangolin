"""
In your module:
from helpers.log import logger
logger.error('something here...')
logger.warning('something here...')
logger.info('something here...')
"""

import logging
from gluon import current
request = current.request
logger = logging.getLogger("web2py.app." + request.application)
logger.setLevel(logging.DEBUG) # INFO, DEBUG, WARNNING, ERROR, CRITICAL