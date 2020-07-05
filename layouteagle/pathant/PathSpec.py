import logging

from layouteagle import config


class PathSpec:
    def __init__(self, *args, path_spec=None, **kwargs):
        self.path_spec = path_spec
        self.logger = logging.getLogger(str(path_spec) + __name__)
        self.temporary = config.hidden_folder

