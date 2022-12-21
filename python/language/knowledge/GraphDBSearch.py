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
from core.database import login
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from helpers.cache_tools import configurable_cache
from helpers.list_tools import unique, nest
from helpers.time_tools import timeit_context
from language.knowledge.GraphDB import GraphDB
from language.span.DifferenceSpanSet import SUBJECT, Span, DifferenceSpanSet


@converter(
    "text",
    "span_annotation.collection.graph_db",
)
class GraphDBSearch(PathSpec):
    conn = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = login("difference")
        self.conn.createFreeTextIndex(
            "index1",
            tokenizer="japanese",
            predicates=Span.FTS_Uris,
            wordFilters=[],
            stopWords=[],
        )

    def __call__(self, prediction_metas, *args, **kwargs):
        for i, (search, meta) in enumerate(prediction_metas):
            meta["search"] = self.search(search)

            yield search, meta

    def search(self, search_string, limit=100):
        query = self.conn.prepareTupleQuery(
            query=f"""
                        prefix : <http://polarity.science/knowledge/>

            select distinct(count(?mid) as ?distance) ?super ?s1 ?s2 ?text1 ?text2 ?p  {{
              ?s fti:match "{search_string}"  .
              ?super :difference* ?mid .
{{ ?mid :difference ?s1 }} Union {{ ?mid :equal ?s1 }}Union {{ ?mid :SUBJECT ?s1 }} Union {{ ?mid :explains ?s1 }}  Union {{ ?mid :CONTRAST ?s1 }}.
              ?super ?q ?s .
              VALUES ?p {{ :SUBJECT :CONTRAST :explains :equal :forward_difference }}
                      ?s1 ?p ?s2 .
                      ?s1 :text ?text1 .
                      ?s2 :text ?text2 .
            }}
            group by ?distance ?super ?s1 ?s2 ?text1 ?text2 ?p
        """
        )
        result = query.evaluate()
        return result
