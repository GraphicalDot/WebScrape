#!/usr/bin/env python

import logging
"""
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler

handler = logging.FileHandler('hello.log')
handler.setLevel(logging.INFO)

FORMAT = "%(asctime)-15s %(clientip)s %(user)-8s  %(review_id)-8s %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("tcpserver")
d = {'clientip' : '192.168.0.1', 'user' : 'fbloggs', "review_id": 3232}
logger.warning("Protocol problem: %s", "connection reset", extra=d)


# create a logging format

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(review_id)s')
handler.setFormatter(formatter)

# add the handlers to the logger

logger.addHandler(handler)
logger.info('Hello baby', review_id=123)
logger.error('Hello baby', 997)

try:
        open('/path/to/does/not/exist', 'rb')
except (SystemExit, KeyboardInterrupt):
        raise
except Exception, e:
        logger.error('Failed to open file', exc_info=True, extra=d)

"""


import logging
from random import choice
class ContextFilter(logging.Filter):
        """
	This is a filter which injects contextual information into the log.
        Rather than use actual contextual information, we just use random
        data in this demo.
	"""
        USERS = ['jim', 'fred', 'sheila']
        IPS = ['123.231.231.123', '127.0.0.1', '192.168.0.1']

        def filter(self, record):
                record.ip = choice(ContextFilter.IPS)
                record.user = choice(ContextFilter.USERS)
                print record
                return True

if __name__ == '__main__':
        levels = (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL)
        logging.basicConfig(level=logging.DEBUG,
                       format='%(asctime)-15s %(name)-5s %(levelname)-8s IP: %(ip)-15s User: %(user)-8s %(message)s')
   
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)


        handler = logging.FileHandler('hello.log')
        handler.setLevel(logging.INFO)

        f = ContextFilter()
        logger.addFilter(f)
        logger.debug('A debug message')
        logger.info('An info message with %s', 'some parameters')
        for x in range(10):
            lvl = choice(levels)
            lvlname = logging.getLevelName(lvl)



