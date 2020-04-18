import logging
import os
from collections import Iterable
from typing import List, Tuple

import networkx as nx
import pylab
from more_itertools import pairwise

from layouteagle.helpers.os_tools import make_dirs_recursive
from pathant.Pipeline import Pipeline
from pathant.converters import converters


class PathAnt:
    def __init__(self, necessary_paths={".layouteagle":["tex_data", "cache"]}):
        make_dirs_recursive(necessary_paths)
        self.G = nx.DiGraph()

        for _from, _to, functional_object in converters:
            self.add_edge(_from, _to, functional_object)


    def realize_node(self, node):
        os.system(f"mkdir {node.dir}")

    def __call__(self, source, target, *args, **kwargs):
        converters_path = nx.shortest_path(self.G, source, target)
        logging.debug(f"found path: {converters_path}")
        pipeline = [self.G[_from][_to]['functional_object'] for _from, _to in pairwise(converters_path)]
        return Pipeline(pipeline)

    def info(self, path="pathant.png", pipelines_to_highlight=None):
        import pylab as plt
        pylab.rcParams['figure.figsize'] = 20, 20

        dG = self.G.copy()


        if pipelines_to_highlight:
            for pipeline, color in zip(pipelines_to_highlight, ['red', 'green', 'orange']):
                edge_colors = [color
                               if attrs['functional_object'] in pipeline.pipeline else 'black'
                               for u,v, attrs  in dG.edges(data=True)]
        else:
            edge_colors = 'black'

        for (u, v, d) in dG.edges(data=True):
            d["functional_object"] = d['functional_object'].__class__.__name__

        pos = nx.kamada_kawai_layout(dG, dist={n1:{n2:1 for n2 in dG.nodes} for n1 in dG.nodes})

        edge_labels = {(u,v): f"{a['functional_object']} " + ("(needs also " + (", ".join(a['implicite'])) +')' if 'implicite' in a else "")  for u, v, a in dG.edges(data=True)}


        nx.draw_networkx_edge_labels(dG, pos, edge_labels=edge_labels, rotate=False)
        nx.draw(dG, pos, node_color="blue",
                font_weight='bold',
                edge_color = edge_colors,
                edge_labels=False,
                arrowsize=20, label='Path Ant',
                node_size=150, edge_cmap=plt.cm.Reds)


        pos_attrs = {}
        for node, coords in pos.items():
            pos_attrs[node] = coords[0] + 0.028, coords[1]


        nx.draw_networkx_labels(dG, pos_attrs)
        pylab.savefig(path)

        plt.show()


    def add_edge(self, froms, tos, functional_object, **kwargs):
        if isinstance(froms, (List)):
            for _from in froms:
                self.add_edge(_from, tos, functional_object, **kwargs)
        elif isinstance(froms, Tuple):
            for _from in froms:
                others = list(froms)
                others.remove(_from)
                self.add_edge(_from, tos, functional_object,
                              **{"implicite":
                                   others})

        elif isinstance(tos, (List, Tuple)):
            for _to in tos:
                self.add_edge(froms,_to, functional_object, **kwargs)
        else:
            functional_object.path_spec._from = "." + froms
            functional_object.path_spec._to = "." + tos
            self.G.add_edge(froms,tos, functional_object=functional_object, **kwargs)







import unittest

class TestPathAnt(unittest.TestCase):
    def test_make_model(self):
        from layouteagle.LayoutReader.labeled_feature_maker import TrueFormatUpmarkerPDF2HTMLEX
        from layouteagle.LayoutReader.feature_label_assigner import TrueFormatUpmarkerPDF2HTMLEX

        from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
        from layouteagle.LayoutReader.feature_tagger import PredictedLayout
        from layouteagle.NLP.nlp_blub import NLPBlub



        from layouteagle.LayoutReader.feature2features import Feature2Features
        from layouteagle.LayoutModel.layoutmodel import LayoutModeler

        ant = PathAnt()

        #pipe = ant("url", "tex")
        #result = list(pipe("http://arxiv.org"))

        pipe = ant("arxiv.org", "keras")
        ant.info(pipelines_to_highlight=[pipe])
        list(pipe("https://arxiv.org"))



if __name__=="__init__":
    unittest()


