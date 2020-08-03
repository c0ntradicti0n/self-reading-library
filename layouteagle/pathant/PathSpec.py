import logging

from layouteagle import config


class PathSpec:
    def __init__(self, *args, path_spec=None, **kwargs):
        self.path_spec = path_spec
        self.logger = logging.getLogger(str(path_spec) + __name__)
        self.temporary = config.hidden_folder

        self.meta_storage = []
        self.value_storage = []

    def answer_or_ask_neighbors(self, meta_match):


        answer = list(self.match(meta_match))
        print (answer)
        if answer:
            return answer

        print(list(self.ant.G.nodes(data=True)))
        print (self.path_spec._to)
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

