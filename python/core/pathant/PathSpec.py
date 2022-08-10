import logging
import coloredlogs
import sys
from enum import Enum
from config import config
import logging
from config import config

class cache_flow(Enum):
    iterate = 1
    add_each = 2
    read_or_make = 3


class PathSpec:
    def __init__(self, *args, path_spec=None, cached: cache_flow = None, **kwargs):
        self.path_spec = path_spec
        logger = logging.getLogger(sys.modules[self.__class__.__module__].__file__)
        coloredlogs.install(
            fmt="%(asctime)s-"
                "%(levelname)s-%(name)s:%(message)s",
            level=config.logging_level, logger=logger)
        self.logger = logger

        self.temporary = config.hidden_folder

        self.meta_storage = []
        self.value_storage = []
        self.cached = cached

    def __enter__(self):
        print (self.__class__.__name__ + " enter")
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        print (self.__class__.__name__ + " exit")

        pass

    def answer_or_ask_neighbors(self, meta_match):


        answer = list(self.match(meta_match))

        if answer:
            return answer

        neighbors = self.ant.G.in_edges(self.path_spec._from[1:])
        print ("NEIBORS", neighbors)
        for edge in neighbors:
            neighbor = self.ant.G.edges[edge]
            print ("NEIGHBOR", neighbor)
            answer = neighbor['functional_object'].answer_or_ask_neighbors(meta_match)
            if answer:
                return answer


    def match(self, meta_match):
        print ("MATCH", meta_match)
        return filter(lambda x: meta_match in x, self.meta_storage)

