import itertools
import json
import logging
import os
import time
from functools import reduce
from textwrap import wrap

from franz.openrdf.repository import Repository
from franz.openrdf.sail import AllegroGraphServer
from more_itertools import pairwise, flatten

from config import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from helpers.cache_tools import configurable_cache
from helpers.list_tools import unique, nest
from helpers.time_tools import timeit_context
from language.span.DifferenceSpanSet import SUBJECT, Span, DifferenceSpanSet


@converter(
    "span_annotation.collection.linked",
    "span_annotation.collection.graph_db",
)
class GraphDB(PathSpec):
    conn = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        while not self.conn:
            try:
                self.login()
            except:
                logging.error("Trying to login into graph db again", exc_info=True)
            time.sleep(1)

    def login(self):
        self.server = AllegroGraphServer(
            host=os.environ.get("GDB_HOST", "localhost"),
            port=10035,
            user=os.environ.get("GDB_USER", "ich"),
            password=os.environ.get("GDB_PASSWORD", "qwertz"),
        )
        catalog = self.server.openCatalog()
        with catalog.getRepository("difference", Repository.ACCESS) as repository:
            repository.initialize()
            self.conn = repository.getConnection()

    def __call__(self, prediction_metas, *args, **kwargs):
        for i, (path, meta) in enumerate(prediction_metas):
            with timeit_context(f"Inserting set no {i} into db"):
                span_sets: DifferenceSpanSet = meta["span_set"]
                span_sets.add_graph_db(self.conn)

                identity_links = meta["identity_links"]
                for a, b in itertools.permutations(identity_links, 2):
                    a.add_link("equal", b, self.conn)

                analysed_links = meta["analysed_links"]
                for a1, a2, as1, as2, c1, c2, l1, l2 in analysed_links:
                    as1.add_link("forward_difference", c1, self.conn)
                    as2.add_link("forward_difference", c2, self.conn)

                yield path, meta

    def all_subjects(self):
        with timeit_context("looking up subjects"):
            values = []
            query = self.conn.prepareTupleQuery(
                query=f"""
                    select ?wt where{{
                            ?s <{Span.SUBJECTS_URI}> ?o .
                            ?s <{Span.WORD_TAGS}> ?wt
                    }}"""
            )

            with query.evaluate() as result:
                for bindings in result:
                    values.append(
                        Span(
                            SUBJECT, word_tags=json.loads(bindings.getValue("wt").label)
                        )
                    )
            return values

    def all_spansets(self):
        with timeit_context("looking up all spansets"):
            values = []
            query = self.conn.prepareTupleQuery(
                query=f"""
                    select distinct ?wt where{{
                            ?s <{DifferenceSpanSet.DIFFERENCE}> ?o .
                            ?s <{DifferenceSpanSet.SPAN_SETS}> ?wt
                    }}  """
            )
            with query.evaluate() as result:
                for bindings in result:
                    values.append(
                        DifferenceSpanSet(json.loads(bindings.getValue("wt").label))
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