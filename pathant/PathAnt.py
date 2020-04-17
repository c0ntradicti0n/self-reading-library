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

    def info(self, path="pathant.png"):
        import pylab as plt
        dG = self.G.copy()
        for (u, v, d) in dG.edges(data=True):
            del d["functional_object"]

        pos = nx.spring_layout(dG)

        edge_labels = nx.get_edge_attributes(dG,'implicite')

        nx.draw_networkx_edge_labels(dG, pos, labels=edge_labels)
        nx.draw(dG, pos, node_color="blue",
                with_labels=True, font_weight='bold',
                arrowsize=20, label='Path Ant',
                node_size=150, edge_color="black", edge_cmap=plt.cm.Reds)
        pylab.show()
        pylab.savefig(path)

    def add_edge(self, _from, _to, functional_object, **kwargs):
        if isinstance(_from, (List)):
            for __from in _from:
                self.add_edge(__from, _to, functional_object, **kwargs)
        elif isinstance(_from, Tuple):
            for __from in _from:
                self.add_edge(__from, _to, functional_object,
                              **{"implicite":
                                   list(_from).pop(_from.index(__from))})

        elif isinstance(_to, (List, Tuple)):
            for __to in _to:
                self.add_edge(_from,_to, functional_object, **kwargs)
        else:
            functional_object.path_spec._from = "." + _from
            functional_object.path_spec._to = "." + _to
            self.G.add_edge(_from,_to, functional_object=functional_object, **kwargs)







import unittest

class TestPathAnt(unittest.TestCase):
    def test_make_model(self):
        from layouteagle.LayoutReader.labeled_feature_maker import TrueFormatUpmarkerPDF2HTMLEX
        from layouteagle.LayoutReader.feature_label_assigner import TrueFormatUpmarkerPDF2HTMLEX

        from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
        from layouteagle.LayoutReader.feature2features import Feature2Features
        from layouteagle.LayoutModel.layoutmodel import LayoutModeler

        ant = PathAnt()
        ant.info()

        #pipe = ant("url", "tex")
        #result = list(pipe("http://arxiv.org"))

        pipe = ant("url", "keras")
        result = list(pipe("http://arxiv.org"))


if __name__=="__init__":
    unittest()


