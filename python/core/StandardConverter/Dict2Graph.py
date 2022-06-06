from numpy.core.multiarray import ndarray

from ant import Ant
from core import config
from helpers.nested_dict_tools import type_spec
from core.pathant.Converter import converter
from core.pathant.PathSpec import cache_flow
import networkx as nx


@converter('dict', 'graph')
class Dict2Graph(Ant):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, cached=cache_flow.iterate, **kwargs)
        self.n = n
        self.debug = debug

    def call(self, graph, meta=None):
        return self.to_graph_dict(graph), meta

    def rec_items(self, dict_list):
        if isinstance(dict_list, dict):
            yield from [(k, z) for k, v in dict_list.items() for y in list(self.rec_items(v)) for z in y]
        elif isinstance(dict_list, (list, set, tuple, ndarray)):
            yield from [list(self.rec_items(e)) for e in dict_list]
        else:
            yield dict_list

    def to_graph_dict(self, topics, fun=None):
        from collections import Mapping

        dig = nx.DiGraph()

        # Iterate through the layers
        q = list(topics.items())
        n = 0
        while q:
            v, dl = q.pop()
            if isinstance(dl, (list, set)):
                for l in dl:
                    dig.add_edge(v, n)
                    if isinstance(l, dict):
                        attr = l
                    else:
                        attr = {'attr': l}
                    dig.add_node(n, **attr)
                    n += 1
                continue
            for nv, nd in dl.items():
                dig.add_edge(v, nv)
                if isinstance(nd, Mapping):
                    q.append((nv, nd))

        ddic = nx.to_dict_of_dicts(dig)
        cross_nodes_2_i = {kk: i for i, kk in enumerate((k for (k, v) in (ddic.items()) if v))}
        rev_ddic= {kk: k for k, v in ddic.items() for kk, vv in v.items()}

        levels = 6
        nodes = [{'id': k,
                  'name': dig.nodes[k]['attr'] if 'attr' in dig.nodes[k] else k,
                  'val': 2 ** (levels - 1) if v else 2 ** (levels - 2),
                  'title': dig.nodes[k]['title'] if 'title' in dig.nodes[k] else None,
                  #'color': dig.nodes[k]['color'] if 'color' in dig.nodes[k] else 'white',
                  'group': cross_nodes_2_i[rev_ddic[k]] if k in rev_ddic else None,
                  'path':  dig.nodes[k]['html_path'].replace(config.tex_data, "") if 'html_path' in dig.nodes[k] else None
                  }

                 for k, v in ddic.items()] \
                + [{'id': "ROOT", 'name': "root", 'color': 'red', 'val': 2 ** (levels)}]

        center_links = [{'source': "ROOT", 'target': k}
                        for k, v in ddic.items() if list(v.items())]

        links = [{'source': k, 'target': n}
                 for k, v in ddic.items()
                 for n in v if v] \
                + center_links

        d = {'nodes': nodes, 'links': links}
        return d


if __name__ == "__main__":
    import pickle

    with open("topics.pickle", "rb") as f:
        topics = pickle.load(f)

    d2g = Dict2Graph
