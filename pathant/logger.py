import logging
import logging.config
from os import path

logging.config.fileConfig(path.normpath("pathant/logger.config"))

palogger = logging.getLogger('PathAnt')