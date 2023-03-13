import itertools
import json
import logging
import time
from functools import reduce

from core.database import login, Queue
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from helpers.time_tools import timeit_context
from language.span.DifferenceSpanSet import SUBJECT, Span, DifferenceSpanSet


@converter(
    "span_annotation.collection.linked",
    "span_annotation.collection.graph_db",
)
class GraphDB(PathSpec, Queue):
    conn = None

    def __init__(self, *args, **kwargs):
        PathSpec.__init__(self, *args, **kwargs)
        Queue.__init__(self, "difference")

    def __call__(self, prediction_metas, *args, **kwargs):
        with self.commit as record:

            for i, (path, meta) in enumerate(prediction_metas):
                # with timeit_context(f"Inserting set no {i} into db"):
                span_set: DifferenceSpanSet = meta["span_set"]
                span_set.add_graph_db(record)

                identity_links = meta["identity_links"]
                for a, b in itertools.permutations(identity_links, 2):
                    a.add_link("equal", b, record)
                    self.logger.info("=")

                analysed_links = meta["analysed_links"]
                for a1, a2, as1, as2, c1, c2, l1, l2 in analysed_links:
                    as1.add_link("forward_difference", c1, record)
                    as2.add_link("forward_difference", c2, record)
                    self.logger.info("!=")

                if i % 10 == 0:
                    self.logger.info(f"added {i} samples to graph")

                yield path, meta

    def all_subjects(self):
        with timeit_context("looking up subjects"):
            values = []
            result = self.query2tuples(
                query=f"""
                    select ?wt {self.from_graph} where {{ {self.graph} {{
                            ?s <{self.uu(Span.SUBJECTS_URI)}> ?o .
                            ?s <{self.uu(Span.WORD_TAGS)}> ?wt
                    }} }}"""
            )

            for bindings in result:
                values.append(
                    Span(SUBJECT, word_tags=json.loads(bindings.get("wt")["value"]))
                )
            return values

    def all_spansets(self):
        with timeit_context("looking up all span_sets"):
            values = []
            result = self.query2tuples(
                query=f"""
                    select ?wt {self.from_graph} where {{ {self.graph} {{
                            ?s <{self.uu(DifferenceSpanSet.DIFFERENCE)}> ?o .
                            ?s <{self.uu(DifferenceSpanSet.SPAN_SETS)}> ?wt
                    }} }} """
            )
            for bindings in result:
                values.append(
                    DifferenceSpanSet(json.loads(bindings.get("wt")["value"]))
                )
            return values

    @staticmethod
    def tags2_words(annotation_slice):
        return [t[0] for t in annotation_slice]

    @staticmethod
    def merge_nested(dicts):
        def merge(acc, d):
            return {k: v + (acc[k] if k in acc else []) for k, v in d.items()}

        return reduce(merge, dicts, {})
