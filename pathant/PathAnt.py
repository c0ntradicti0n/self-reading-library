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
    def __init__(self, necessary_paths={".layouteagle":["tex_data", "cache", "log"]}):
        make_dirs_recursive(necessary_paths)
        self.G = nx.DiGraph()

        for _from, _to, functional_object in converters:
            self.add_edge(_from, _to, functional_object)


    def realize_node(self, node):
        os.system(f"mkdir {node.dir}")

    def make_path(self, G, source, target):
        try:
            return nx.shortest_path(G, source, target)
        except:
            self.info()
            raise

    def __call__(self, source, target, *args, **kwargs):
        converters_path = self.make_path(self.G, source, target)
        converters_implications = {uv: [_a for _a in a if _a not in converters_path ]
                                   for uv, a in nx.get_edge_attributes(self.G, 'implicite').items()
                                   if uv[1] in converters_path
                                      and [_a for _a in a if _a not in converters_path ] }
        extra_paths = {self.lookup(edge[0],edge[1]):
                           [self.estimate_targeting_paths(intermediate_target)  for intermediate_target in intermediate_targets]
               for edge, intermediate_targets in converters_implications.items()
                      }

        logging.debug(f"found path: {converters_path}")
        pipeline = [self.lookup(*_from_to) for _from_to in pairwise(converters_path)]
        return Pipeline(pipeline, source, target, extra_paths)

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

        pos = nx.nx_agraph.graphviz_layout(dG)

        edge_labels = {(u,v):
                           f"{a['functional_object']} " +
                           ("(needs also " + (", ".join(a['implicite'])) +')' if 'implicite' in a else "")
                       for u, v, a in dG.edges(data=True)}


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

    def lookup(self, _from, _to, attr='functional_object'):
        return self.G[_from][_to][attr]

    def estimate_targeting_paths(self, intermediate_target):
        for possible_path in nx.single_target_shortest_path(self.G, intermediate_target).values():
            if len(possible_path) == 2:
                return self.lookup(*possible_path)


import unittest

class TestPathAnt(unittest.TestCase):
    from layouteagle.ScienceTexScraper.scrape import ScienceTexScraper
    from layouteagle.LatexReplacer.latex_replacer import LatexReplacer
    from layouteagle.LayoutReader.labeled_feature_maker import TrueFormatUpmarkerPDF2HTMLEX
    from layouteagle.LayoutReader.feature_label_assigner import TrueFormatUpmarkerPDF2HTMLEX
    from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
    from layouteagle.LayoutReader.feature_prediction import LayoutPrediction
    from layouteagle.LayoutReader.MarkupDocument import MarkupDocument
    from layouteagle.LayoutReader.feature2features import Feature2Features
    from layouteagle.LayoutModel.layouttrain import LayoutTrainer
    from layouteagle.LayoutModel.layoutpredict import LayouPredictor

    from layouteagle.LayoutReader.HTML2PDF import PrintToFile
    from TestArchitecture.publisher import NLPPublisher, TopicPublisher
    from TestArchitecture.NLP.nlp_blub import NLPBlub
    from TestArchitecture.NLP.topicape import TopicApe

    def setUp(self):
        self.ant = PathAnt()
        self.model_pipe = self.ant("arxiv.org", "keras")
        self.prediction_pipe = self.ant("pdf", "layout.html")


    def test_make_model(self):
        model_pipe = self.ant("arxiv.org", "keras")
        print (list(model_pipe("https://arxiv.org")))

    def test_info(self):
        self.ant.info(pipelines_to_highlight=[self.model_pipe, self.prediction_pipe])

    def test_prediction(self):
        pdfs = [".layouteagle/tex_data/2adf47ffbf65696180417ca86e91eb90//crypto_github_preprint_v1.pdf",
                ".layouteagle/tex_data/2922d1d785d9620f9cdf8ac9132c59a8//ZV_PRL_rev.pdf",
                ".layouteagle/tex_data/9389d5a6fd9fcc41050f32bcb2a204ef//Manuscript.tex1.labeled.pdf"]
        list(self.prediction_pipe((pdf, {}) for pdf in pdfs))


if __name__=="__init__":
    unittest()


