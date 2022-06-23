import itertools
import logging
import os
from typing import List, Tuple

import networkx as nx
import pylab
import matplotlib
from more_itertools import pairwise

from core import config
from helpers.list_tools import flatten_optional_list_pair, flatten_optional_list_triple
from core.StandardConverter.Dict2Graph import Dict2Graph
from helpers.os_tools import make_dirs_recursive
from core.pathant.MatchDescription import match, list_or_values
from core.pathant.Pipeline import Pipeline
from core.pathant.converters import ____CONVERTERS____
from regex import regex, Regex
from core.pathant.Filter import Filter

OUT_OF_THE_BOX = "OUT_OF_THE_BOX"
class PathAnt:
    def __init__(self, necessary_paths={config.hidden_folder: ["tex_data", "cache", "log", "topics"]}):
        make_dirs_recursive(necessary_paths)
        self.G = nx.MultiDiGraph()

        for _from, _to, functional_object in ____CONVERTERS____:
            self.add_edge(_from, _to, functional_object)
            self.add_starred(_from, _to, functional_object, ____CONVERTERS____)
            functional_object.ant = self

        for (_froms1, _tos1, functional_object1), \
            (_froms2, _tos2, functional_object2) \
                in itertools.permutations(____CONVERTERS____, 2):

            for (_to1, _from1, _to2, _from2) in list_or_values(_tos1, _froms1, _tos2, _froms2):
                if _from1 == None:
                    _from1 =  OUT_OF_THE_BOX
                if _from2 == None:
                    _from2 =  OUT_OF_THE_BOX

                try:
                    if match(_to1, _from2):
                        self.add_edge(_to1, regex.sub(_from2 + '$', _to2, _to1), functional_object2)
                    if match(_to2, _from1):
                        self.add_edge(_to2, regex.sub(_from1 + '$', _to1, _to2), functional_object1)
                except Exception as e:
                    logging.error(f"_to1 = {_to1}")
                    logging.error(
                        f"failing to compare {_to1} and {_to2} and {_from1} and {_from2} as regexes because {e}")

    def realize_node(self, node):
        os.system(f"mkdir {node.dir}")

    def make_path(self, G, source, target, via=None):
        if source == None:
            source = OUT_OF_THE_BOX

        try:
            if via:
                if isinstance(via, str):
                    return self.make_path(G, source=source, target=via) \
                           + self.make_path(G, source=via, target=target)[1:]
                if isinstance(via, list):
                    raise NotImplemented("Needs to be implemented to have different signs on the way")

            return nx.shortest_path(G, source, target)
        except:
            self.info()
            raise

    def __call__(self, source, target, *args, via=None, filter={}, **kwargs):

        converters_path = self.make_path(self.G, source, target, via=via)
        converters_implications = {uv: [_a for _a in a if _a not in converters_path]
                                   for uv, a in nx.get_edge_attributes(self.G, 'implicite').items()
                                   if uv[1] in converters_path
                                   and [_a for _a in a if _a not in converters_path]}
        extra_paths = {self.lookup(edge[0], edge[1]):
                           [self.estimate_targeting_paths(intermediate_target) for intermediate_target in
                            intermediate_targets]
                       for edge, intermediate_targets in converters_implications.items()
                       }

        logging.info(f"Found path: {' ⇾ '.join(converters_path)}")
        pipeline = [self.lookup(*_from_to) for _from_to in pairwise(converters_path)]
        for i, step in enumerate(pipeline[::-1]):
            step_key = step.path_spec._to.replace(".", "")
            if step_key in filter:
                f_step = filter[step_key]
                from core.pathant.Converter import converter

                pipeline.insert(len(pipeline) - i,
                                converter('filter-' + step_key, 'filter-' + step_key, f_step)(
                                    Filter))
        return Pipeline(pipeline, source, target, extra_paths, via=via, **kwargs)

    def info(self, path="pathant.png", pipelines_to_highlight=None):
        import pylab as plt
        pylab.rcParams['figure.figsize'] = 20, 20

        dG = self.G.copy()
        dG = nx.MultiDiGraph(dG, directed=True)
        if pipelines_to_highlight:
            cmap = plt.cm.get_cmap("nipy_spectral", len(pipelines_to_highlight)+3)

        nx.set_edge_attributes(dG, "#CCCCFF", 'color')
        nx.set_edge_attributes(dG, "", 'label')

        if pipelines_to_highlight:
            for color, pipeline in enumerate(pipelines_to_highlight):
                pipe_path = self.make_path(dG, pipeline.source, pipeline.target, via=pipeline.via)
                edges = pairwise(pipe_path)
                for u, v in edges:
                    rgba = cmap(color+1)
                    attrs = dict(dict(dG[u][v])[0])
                    attrs['color'] = matplotlib.colors.rgb2hex(rgba)
                    dG.add_edge(u, v, **attrs)
                for n in pipe_path:
                    dG.nodes[n]['label'] = str(pipeline)

        edge_colors = nx.get_edge_attributes(dG, 'color').values()

        for (u, v, d) in dG.edges(data=True):
            d["functional_object"] = d['functional_object'].__class__.__name__

        pos = nx.nx_agraph.graphviz_layout(dG, prog="dot")

        edge_labels = {(u, v):
                           f"{a['functional_object']} " +
                           ("(needs also " + (", ".join(a['implicite'])) + ')' if 'implicite' in a else "")
                       for u, v, a in dG.edges(data=True)}

        color_map = []

        for node in dG:
            color_map.append((1, 1, 0))

        nx.draw_networkx_edge_labels(dG, pos, edge_labels=edge_labels, rotate=False)


        nx.draw_networkx_nodes(
            dG, pos
        )

        ax = plt.gca()
        for e, ea in zip(dG.edges, dG.edges(data=True)):
            ax.annotate(
                "",
                xy=pos[e[0]], xycoords='data',
                xytext=pos[e[1]], textcoords='data',
                arrowprops=dict(
                    linewidth=5,
                    arrowstyle="<-", color=ea[2]['color'],
                    shrinkA=5, shrinkB=5,
                    patchA=None, patchB=None,
                    connectionstyle="arc3,rad=rrr".replace(
                        'rrr', str(0.3 * e[2])
                    ),
                ),
            )

        pos_attrs = {}
        for node, coords in pos.items():
            pos_attrs[node] = coords[0] + 0.08, coords[1]

        nx.draw_networkx_labels(dG, pos_attrs)
        pylab.savefig(path)
        plt.legend(scatterpoints=1)
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
                self.add_edge(froms, _to, functional_object, **kwargs)
        else:
            if froms == None:
                froms = OUT_OF_THE_BOX

            functional_object.path_spec._from = "." + froms
            functional_object.path_spec._to = "." + tos

            functional_object.ant = self

            self.G.add_edge(froms, tos, functional_object=functional_object, **kwargs)

    def lookup(self, _from, _to, attr='functional_object'):
        try:
            if 0 in self.G[_from][_to]:
                return self.G[_from][_to][0][attr]
            return self.G[_from][_to][attr]
        except KeyError as e:
            print(self.G[_from][_to])
            raise e
        except Exception as e:
            raise e


    def estimate_targeting_paths(self, intermediate_target):
        for possible_path in nx.single_target_shortest_path(self.G, intermediate_target).values():
            if len(possible_path) == 2:
                return self.lookup(*possible_path)

    def graph(self):
        d2g = Dict2Graph

        return list(d2g([nx.to_dict_of_dicts(self.G, edge_data=[])]))[0]

    def add_starred(self, _from1, _to1, functional_object, converters):

        if _from1 == None:
            _from1 = OUT_OF_THE_BOX

        if "*" in _from1:

            other_things = [(f, t) for f, t, o in converters]
            new_things_regex = Regex("^" + _from1.replace("*", r"(\w+)") + "$")

            for _from2, _to2 in flatten_optional_list_pair(other_things):
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
   from latex.Scraper.Scraper import Scraper
    from latex.LatexReplacer.latex_replacer import LatexReplacer
    from latex.LayoutReader.trueformatpdf2htmlEX import PDF_AnnotatorTool
    from latex.LayoutReader.feature_prediction import LayoutPrediction
    from latex.LayoutReader.MarkupDocument import MarkupDocument
    from latex.LayoutReader.feature2features import Feature2Features
    from latex.LayoutModel.layouttrain import LayoutTrainer
    from latex.LayoutModel.layoutpredict import LayouPredictor

    from latex.LayoutReader.HTML2PDF import HTML2PDF
    from latex.LayoutReader.PDF2HTML import PDF2HTML

    from TestArchitecture.publisher import NLPPublisher, TopicPublisher
    from TestArchitecture.NLP.nlp_blub import NLPBlub
    from TestArchitecture.NLP.topicape import TopicApe
    """

    def setUp(self):
        self.ant = PathAnt()
        self.model_pipe = self.ant(itertools.cycle(["arxiv.org"]), "keras")
        self.prediction_pipe = self.ant("pdf", "latex.html")

    def test_make_model(self):
        model_pipe = self.ant(itertools.cycle(["arxiv.org"]), "keras")
        list(model_pipe("https://arxiv.org"))

    def test_info(self):
        self.ant.info(pipelines_to_highlight=[self.model_pipe, self.prediction_pipe])

    def test_prediction(self):
        self.ant.info()

        pdfs = [".core/tex_data/2adf47ffbf65696180417ca86e91eb90//crypto_github_preprint_v1.pdf",
                ".core/tex_data/2922d1d785d9620f9cdf8ac9132c59a8//ZV_PRL_rev.pdf",
                ".core/tex_data/9389d5a6fd9fcc41050f32bcb2a204ef//Manuscript.tex1.labeled.pdf"]
        list(self.prediction_pipe([(pdf, {}) for pdf in pdfs]))


if __name__ == "__init__":
    unittest()
