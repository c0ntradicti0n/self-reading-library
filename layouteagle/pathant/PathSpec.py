from layouteagle import config
from layouteagle.pathant.logger import palogger


class PathSpec:
    def __init__(self, *args, path_spec=None, **kwargs):
        self.path_spec = path_spec
        self.logger = palogger
        self.temporary = config.hidden_folder

