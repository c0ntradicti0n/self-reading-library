import itertools
import os
from functools import reduce
from textwrap import wrap

from more_itertools import pairwise

from config import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from helpers.cache_tools import configurable_cache
from helpers.list_tools import unique
from language.span.DifferenceSpanSet import SUBJECT


@converter(
    "span_annotation.collection.graph_db",
    "span_annotation.collection.nodes_edges",
)
class NodeEdges(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, prediction_metas, *args, **kwargs):
        for i, (path, meta) in enumerate(prediction_metas):
            result = meta["search"]
            nodes_edges = self.generate_nodes_edges(result)
            res = NodeEdges.merge_nested(nodes_edges)
            res["nodes"] = unique(res["nodes"], key=lambda n: str(n["id"]))
            res["edges"] = unique(res["edges"], key=lambda n: str(n["id"]))

            yield path, res

    def generate_nodes_edges(self, result):
        nodes = []
        edges = []
        for j, (binding_set) in enumerate(result):
            nodes.append(
                {
                    "id": binding_set.get("s1"),
                    "label": binding_set.get("text1"),
                    "parent": binding_set.get("s1"),
                }
            )
            nodes.append(
                {
                    "id": binding_set.get("s2"),
                    "label": binding_set.get("text2"),
                    "parent": binding_set.get("s1"),
                }
            )
            edges.append(
                {
                    "id": str(binding_set.get("s1")) + "-" + str(binding_set.get("s2")),
                    "source": binding_set.get("s1"),
                    "target": binding_set.get("s2"),
                    "label": binding_set.get("p"),
                }
            )

        yield {
            "nodes": nodes,
            "edges": edges,
        }

    @staticmethod
    def merge_nested(dicts):
        def merge(acc, d):
            return {k: v + (acc[k] if k in acc else []) for k, v in d.items()}

        return reduce(merge, dicts, {})
