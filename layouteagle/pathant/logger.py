import logging
import logging.config
from os import path

logger_config_file_path = "layouteagle/pathant/logger.config"
try:
    logging.config.fileConfig(path.normpath(logger_config_file_path))
except KeyError:
    raise FileNotFoundError(f'{logger_config_file_path} not found!')

palogger = logging.getLogger('PathAnt')