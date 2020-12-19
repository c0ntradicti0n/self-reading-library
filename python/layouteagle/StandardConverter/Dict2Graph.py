from pprint import pprint

from numpy.core.multiarray import ndarray

from python.ant import Ant
from python.layouteagle import config
from python.helpers.nested_dict_tools import type_spec
from python.layouteagle.pathant.Converter import converter
from python.layouteagle.pathant.PathSpec import cache_flow
import networkx as nx


@converter('dict', 'graph')
class Dict2Graph(Ant):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, cached= cache_flow.iterate, **kwargs)
        self.n = n
        self.debug = debug

    def call(self, graph, meta=None):
        return self.to_graph_dict(graph), meta

    def rec_items(self, dict_list):
        if isinstance(dict_list, dict):
            yield from [(k, z) for k, v in dict_list.items() for y in list(self.rec_items(v)) for z in y]
        elif isinstance(dict_list, (list, set, tuple, ndarray)):
            yield from [list(self.rec_items(e)) for e in dict_list]
        else: yield dict_list


    def to_graph_dict(self, topics):
        """try:
            import textwrap
            edge_list = list(self.rec_items(topics))
            print(textwrap.fill(str(edge_list), 80))
            dig = nx.from_dict_of_dicts(topics)
        except nx.NetworkXError as e:
            pprint (type_spec(topics))
            raise e
            """

        from collections import Mapping
        #graph_data = {"root": {"level-0.A": 0,
        #                       "level-0.B": {"level-1.B.1": 2,
        #                                     "level-1.B.2": {"level-2.B.2.1": 3, "level-2.B.2.2": 1}}}}
        # Empty directed graph
        dig = nx.DiGraph()

        # Iterate through the layers
        q = list(topics.items())
        while q:
            v, d = q.pop()
            for nv, nd in d.items():
                dig.add_edge(v, nv)
                if isinstance(nd, Mapping):
                    q.append((nv, nd))

        ddic = nx.to_dict_of_dicts(dig)
        print(ddic)
        levels = 3
        nodes = [{'id': k,
                  'name': k.replace(config.test_dir, "").replace("pdf.htmlayout.txt", ""),
                  'val': 2 ** (levels - 1) if v else 2 ** (levels - 2)}

                 for k, v in ddic.items()] \
                + [{'id': "ROOT", 'name': "root", 'val': 2 ** (levels)}]

        center_links = [{'source': "ROOT", 'target': k} for k, v in ddic.items() if list(v.items())]

        links = [{'source': k, 'target': n} for k, v in ddic.items() for n in v if v] + center_links
        d = {'nodes': nodes, 'links': links}
        return d


if __name__ == "__main__":
    import pickle

    with open("topics.pickle", "rb") as f:
        topics = pickle.load(f)

    d2g = Dict2Graph
    #pprint(topics)
    print (list(d2g([topics])))