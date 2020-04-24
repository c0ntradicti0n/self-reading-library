import logging
import logging.config
import os
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

palogger = logging.getLogger('PathAnt')