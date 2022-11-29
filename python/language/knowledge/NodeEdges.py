import os
from functools import reduce
from textwrap import wrap

from more_itertools import pairwise

from config import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from helpers.cache_tools import configurable_cache


@converter(
    "span_annotation.collection.analysed",
    "span_annotation.collection.nodes_edges",
)
class AnnotationAnalyser(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @configurable_cache(
        filename=config.cache + os.path.basename(__file__),
    )
    def __call__(self, prediction_metas, *args, **kwargs):
        res = AnnotationAnalyser.merge_nested(
            self.generate_nodes_edges(prediction_metas)
        )
        yield self.flags["search"], res


    def generate_nodes_edges(self, prediction_metas):
        for i, (path, meta) in enumerate(prediction_metas):
            nodes = []
            edges = []

            span_sets = meta["span_set"]

            for j, (span_set) in enumerate(span_sets.side_sets):
                set_ids = []
                for span in span_set:
                    nodes.append(
                        {
                            "id": span.nlp_id,
                            "label": wrap(span.text),
                        }
                    )
                    set_ids.append(span.nlp_id)

                for a, b in pairwise(sorted(set_ids)):
                    edges.append(
                        {"id": f"arm-{a}-{b}", "source": a, "target": b, "label": "..."}
                    )

            for values in span_sets.kind_sets:
                for a, b in pairwise(values):
                    id_a, id_b = a.nlp_id, b.nlp_id
                    edges.append(
                        {
                            "id": f"arm-{id_a}-{id_b}",
                            "source": id_a,
                            "target": id_b,
                        }
                    )

            analysed_links = meta["analysed_links"]
            for a1, a2, c1, c2, l1, l2 in analysed_links:
                k1_id = c1.nlp_id + "krit"
                k2_id = c2.nlp_id + "krit"
                nodes.extend(
                    [
                        {
                            "id": k1_id,
                            "label": a1,
                        },
                        {
                            "id": k2_id,
                            "label": a2,
                        },
                    ]
                )
                edges.append(
                    {
                        "id": f"arm-{k1_id}-{k2_id}-krit",
                        "source": k2_id,
                        "target": k1_id,
                        "label": "krit",
                    }
                )

                edges.append(
                    {"id": f"arm-{k1_id}-{k2_id}-k1", "source": k1_id, "target": c2.nlp_id}
                )
                edges.append(
                    {"id": f"arm-{k1_id}-{k2_id}-k2", "source": k2_id, "target": c1.nlp_id}
                )

            yield {
                "nodes": nodes,
                "edges": edges,
            }

    @staticmethod
    def tags2_words(annotation_slice):
        return [t[0] for t in annotation_slice]

    @staticmethod
    def merge_nested(dicts):
        def merge(acc, d):

            return {k: v + (acc[k] if k in acc else []) for k, v in d.items()}

        return reduce(merge, dicts, {})