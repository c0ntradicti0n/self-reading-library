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

    def make_path(self, G, source, target):
        return nx.shortest_path(G, source, target)

    def __call__(self, source, target, *args, **kwargs):
        converters_path = self.make_path(self.G, source, target)
        logging.debug(f"found path: {converters_path}")
        pipeline = [self.G[_from][_to]['functional_object'] for _from, _to in pairwise(converters_path)]
        return Pipeline(pipeline, source, target)

    def info(self, path="pathant.png", pipelines_to_highlight=None):
        import pylab as plt
        pylab.rcParams['figure.figsize'] = 20, 20

        dG = self.G.copy()

        nx.set_edge_attributes(dG, 0, 'color')
        nx.set_edge_attributes(dG, " ", 'label')

        if pipelines_to_highlight:
            for  color, pipeline in enumerate(pipelines_to_highlight):
                pipe_path = self.make_path(dG, pipeline.source, pipeline.target)
                edges = pairwise(pipe_path)
                for u, v in edges:
                    dG[u][v]['color'] = color + 1
                for n in pipe_path:
                    dG.nodes[n]['label'] =  str(pipeline)



        edge_colors = nx.get_edge_attributes(dG, 'color').values()

        for (u, v, d) in dG.edges(data=True):
            d["functional_object"] = d['functional_object'].__class__.__name__

        pos = nx.nx_agraph.graphviz_layout(dG)  #nx.kamada_kawai_layout(dG)

        edge_labels = {(u,v): f"{a['functional_object']} " + ("(needs also " + (", ".join(a['implicite'])) +')' if 'implicite' in a else "")  for u, v, a in dG.edges(data=True)}


        nx.draw_networkx_edge_labels(dG, pos, edge_labels=edge_labels, rotate=False)
        nx.draw(dG, pos, node_color="blue",
                font_weight='bold',
                edge_color = edge_colors,
                edge_labels=False,
                arrowsize=20, label='Path Ant',
                node_size=150, edge_cmap=plt.cm.plasma)


        pos_attrs = {}
        for node, coords in pos.items():
            pos_attrs[node] = coords[0] + 0.08, coords[1]


        nx.draw_networkx_labels(dG, pos_attrs)
        pylab.savefig(path)
        plt.legend(scatterpoints = 1)
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
        from TestArchitecture.NLP.nlp_blub import NLPBlub
        from TestArchitecture.NLP.topicape import TopicApe
        from layouteagle.LayoutReader.HTML2PDF import PrintToFile
        from layouteagle.LayoutReader.feature2features import Feature2Features
        from layouteagle.LayoutModel.layoutmodel import LayoutModeler
        from TestArchitecture.publisher import NLPPublisher, TopicPublisher


        ant = PathAnt()

        #pipe = ant("url", "tex")
        #result = list(pipe("http://arxiv.org"))

        model_pipe = ant("arxiv.org", "keras")
        prediction_pipe = ant("html", "apache")

        ant.info(pipelines_to_highlight=[model_pipe, prediction_pipe])
        list(pipe("https://arxiv.org"))



if __name__=="__init__":
    unittest()


