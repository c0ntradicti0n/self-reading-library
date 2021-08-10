import itertools
import logging
import os
from typing import List, Tuple

import networkx as nx
import pylab
from more_itertools import pairwise

from helpers.list_tools import flatten_optional_list_pair, flatten_optional_list_triple
from layouteagle.StandardConverter.Dict2Graph import Dict2Graph
from helpers.os_tools import make_dirs_recursive
from layouteagle.pathant.MatchDescription import match, list_or_values
from layouteagle.pathant.Pipeline import Pipeline
from layouteagle.pathant.converters import converters
from regex import regex, Regex


class PathAnt:
    def __init__(self, necessary_paths={".layouteagle":["tex_data", "cache", "log"]}):
        make_dirs_recursive(necessary_paths)
        self.G = nx.DiGraph()

        for _from, _to, functional_object in converters:

            self.add_edge(_from, _to, functional_object)
            self.add_starred(_from, _to, functional_object, converters)
            functional_object.ant = self

        for (_froms1, _tos1, functional_object1), \
            (_froms2, _tos2, functional_object2)  \
                in itertools.permutations(converters, 2):

            for (_to1, _from1, _to2, _from2) in list_or_values(_tos1, _froms1,_tos2, _froms2) :
                try:
                    if match(_to1, _from2):
                        self.add_edge(_to1, regex.sub(_from2+'$', _to2, _to1), functional_object2)
                    if match(_to2, _from1):
                        self.add_edge(_to2, regex.sub(_from1+'$', _to1, _to2), functional_object1)
                except Exception as e:
                    logging.error(f"_to1 = {_to1}")
                    logging.error(f"failing to compare {_to1} and {_to2} and {_from1} and {_from2} as regexes because {e}")


    def realize_node(self, node):
        os.system(f"mkdir {node.dir}")

    def make_path(self, G, source, target):
        try:
            return nx.shortest_path(G, source, target)
        except:
            self.info()
            raise

    def __call__(self, source, target, *args, via=None, **kwargs):
        if via:
            if isinstance(via, str):
                return self.__call__(source, via, *args) + self.__call__(via, target, **kwargs)


        converters_path = self.make_path(self.G, source, target)
        converters_implications = {uv: [_a for _a in a if _a not in converters_path ]
                                   for uv, a in nx.get_edge_attributes(self.G, 'implicite').items()
                                   if uv[1] in converters_path
                                      and [_a for _a in a if _a not in converters_path ] }
        extra_paths = {self.lookup(edge[0],edge[1]):
                           [self.estimate_targeting_paths(intermediate_target)  for intermediate_target in intermediate_targets]
               for edge, intermediate_targets in converters_implications.items()
                      }

        logging.info(f"Found path: {'⇾'.join(converters_path)}")
        pipeline = [self.lookup(*_from_to) for _from_to in pairwise(converters_path)]
        return Pipeline(pipeline, source, target, extra_paths, **kwargs)

    def info(self, path="pathant.png", pipelines_to_highlight=None):
        import pylab as plt
        pylab.rcParams['figure.figsize'] = 20, 20

        dG = self.G.copy()

        nx.set_edge_attributes(dG, "#CCCCFF", 'color')
        nx.set_edge_attributes(dG, "", 'label')

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

        pos = nx.nx_agraph.graphviz_layout(dG, prog= "dot")

        edge_labels = {(u,v):
                           f"{a['functional_object']} " +
                           ("(needs also " + (", ".join(a['implicite'])) +')' if 'implicite' in a else "")
                       for u, v, a in dG.edges(data=True)}


        nx.draw_networkx_edge_labels(dG, pos, edge_labels=edge_labels, rotate=False)
        nx.draw(dG, pos, node_color="blue",
                font_weight='bold',
                edge_color = edge_colors,
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

            functional_object.ant = self

            self.G.add_edge(froms,tos, functional_object=functional_object, **kwargs)

    def lookup(self, _from, _to, attr='functional_object'):
        return self.G[_from][_to][attr]

    def estimate_targeting_paths(self, intermediate_target):
        for possible_path in nx.single_target_shortest_path(self.G, intermediate_target).values():
            if len(possible_path) == 2:
                return self.lookup(*possible_path)

    def graph(self):
        d2g = Dict2Graph


        return list(d2g([nx.to_dict_of_dicts(self.G, edge_data=[])]))[0]

    def add_starred(self, _from1, _to1, functional_object, converters):
        if "*" in _from1:

                other_things = [(f,t) for f,t, o in converters]
                new_things_regex = Regex("^" + _from1.replace("*", r"(\w+)") + "$")

                for _from2,_to2 in flatten_optional_list_pair(other_things):
                    m = new_things_regex.match(_to2)
                    if m:
                        new_from = _to1.replace("*", m.group(1))
                        self.add_edge(_to2, new_from, functional_object)
                        self.add_starred_from_converters(_to2, new_from, functional_object, converters)

    def add_starred_from_converters(self, _from1, _to1, functional_object, converters):
        other_things = [(f, t, functional_object2) for f, t, functional_object2 in converters]
        for _from2, _to2, functional_object2 in flatten_optional_list_triple(other_things):
            if "*" in _to2:

                other_things_regex = Regex("^" + _from2.replace("*", r"(\w+)") + "$")
                m = other_things_regex.match(_to1)

                if m:
                    new_to = _to2.replace("*", m.group(1))

                    new_from = _to2.replace("*", m.group(1))
                    self.add_edge(_to1, new_from, functional_object2)

import unittest

class TestPathAnt(unittest.TestCase):
    """
    from layout.ScienceTexScraper.scrape import ScienceTexScraper
    from layout.LatexReplacer.latex_replacer import LatexReplacer
    from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
    from layout.LayoutReader.feature_prediction import LayoutPrediction
    from layout.LayoutReader.MarkupDocument import MarkupDocument
    from layout.LayoutReader.feature2features import Feature2Features
    from layout.LayoutModel.layouttrain import LayoutTrainer
    from layout.LayoutModel.layoutpredict import LayouPredictor

    from layout.LayoutReader.HTML2PDF import HTML2PDF
    from layout.LayoutReader.PDF2HTML import PDF2HTML

    from TestArchitecture.publisher import NLPPublisher, TopicPublisher
    from TestArchitecture.NLP.nlp_blub import NLPBlub
    from TestArchitecture.NLP.topicape import TopicApe
    """
    def setUp(self):
        self.ant = PathAnt()
        self.model_pipe = self.ant("arxiv.org", "keras")
        self.prediction_pipe = self.ant("pdf", "layout.html")


    def test_make_model(self):
        model_pipe = self.ant("arxiv.org", "keras")
        list(model_pipe("https://arxiv.org"))

    def test_info(self):
        self.ant.info(pipelines_to_highlight=[self.model_pipe, self.prediction_pipe])

    def test_prediction(self):
        self.ant.info()

        pdfs = [".layouteagle/tex_data/2adf47ffbf65696180417ca86e91eb90//crypto_github_preprint_v1.pdf",
                ".layouteagle/tex_data/2922d1d785d9620f9cdf8ac9132c59a8//ZV_PRL_rev.pdf",
                ".layouteagle/tex_data/9389d5a6fd9fcc41050f32bcb2a204ef//Manuscript.tex1.labeled.pdf"]
        list(self.prediction_pipe([(pdf, {}) for pdf in pdfs]))


if __name__=="__init__":
    unittest()


