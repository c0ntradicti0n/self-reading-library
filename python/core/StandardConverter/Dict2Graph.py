import logging

from numpy.core.multiarray import ndarray

from ant import Ant
from core import config
from helpers.nested_dict_tools import type_spec, list2dict
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
        dd = list2dict(topics, key=lambda x: x['html_path'])
        ddd = {"root": dd}
        dig = nx.DiGraph()
        q = list(ddd.items())
        while q:
            v, d = q.pop()
            for nv, nd in d.items():
                dig.add_edge(v, nv)
                if isinstance(nd, dict):
                    if 'doc_id' in nd:
                        dig.nodes[nv].update(nd)
                    else:
                        q.append((nv, nd))

        cross_nodes_2_i = {kk: i for i, kk in enumerate((k for (k, v) in (dd.items()) if v))}
        rev_ddic = {kk: k for k, v in dd.items() for kk, vv in v.items()}

        for k, v, attr in dig.edges(data=True):
            dig.nodes[v].update(attr)
        levels = 6
        nodes = [self.make_node(k, v, attr, dig, levels, cross_nodes_2_i, rev_ddic)

                 for k, attr in dig.nodes(data=True)]

        links = [{'source': k, 'target': v} for k, v in dig.edges]

        d = {'nodes': nodes, 'links': links}
        return d

    def make_node(self, k, v, attr, dig, levels, cross_nodes_2_i, rev_ddic):
        try:
            return {'id': k,
                    'name': dig.nodes[k]['attr'] if 'attr' in dig.nodes[k] else k,
                    'val': 2 ** (levels - 1) if v else 2 ** (levels - 2),
                    'title': (dig.nodes[k]['title'].strip().replace("\n", " ").title() if 'title' in dig.nodes[
                        k] and config.hidden_folder not in dig.nodes[k]['title'] else (
                        " ".join(dig.nodes[k]['used_text_boxes'][0][0][0].split(" ")[:20]).replace("\n",
                                                                                                   "").title() if "used_text_boxes" in
                                                                                                                  dig.nodes[
                                                                                                                      k] else None)),
                    'group': cross_nodes_2_i[rev_ddic[k]] if k in rev_ddic else None,
                    'path': dig.nodes[k]['html_path'].replace(config.tex_data, "")
                    if 'html_path' in dig.nodes[k] else None
                    }
        except Exception as e:
            logging.error("Failed to make node!", exc_info=True)
            return {'id': k,
                    'name': dig.nodes[k]['attr'] if 'attr' in dig.nodes[k] else k,
                    'val': "0",
                    'title': "error",
                    'group': 0,
                    'path': "error"
                    }


if __name__ == "__main__":
    import pickle

    with open("topics.pickle", "rb") as f:
        topics = pickle.load(f)

    d2g = Dict2Graph
