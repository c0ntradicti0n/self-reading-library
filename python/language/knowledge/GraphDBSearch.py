import itertools
import json
import os
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
from language.knowledge.GraphDB import GraphDB
from language.span.DifferenceSpanSet import SUBJECT, Span, DifferenceSpanSet


@converter(
    "text",
    "span_annotation.collection.graph_db",
)
class GraphDBSearch(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        for i, (search, meta) in enumerate(prediction_metas):
            meta["search"] = self.search(search)

            yield search, meta

    def search(self, search_string, limit=100):
        query = self.conn.prepareTupleQuery(
            query=f"""
            prefix : <http://polarity.science/knowledge/> 
            
            select ?super ?sub (count(?mid) as ?distance)  {{ 
              ?s fti:match "{search_string}"  .
              ?super :difference* ?mid .
              ?mid :difference+ ?sub .            
              ?super ?q ?s .
            }}
            group by ?super ?sub 
            order by ?super ?sub
        """
        )
        result = query.evaluate()
        nl = "\n"
        ids = list(map(lambda x: x[1], result.string_tuples))
        result = self.conn.prepareTupleQuery(
            query=f"""
                prefix : <http://polarity.science/knowledge/> 

                select  ?s1 ?s2 ?text1 ?text2  ?p  {{ 
                      VALUES ?p {{ :SUBJECT :CONTRAST :explains :equal :forward_difference }}
                      VALUES ?s1 {{ {nl.join(ids)} }}
                      ?s1 ?p ?s2 .
                      ?s1 :text ?text1 .
                      ?s2 :text ?text2 .
                }}
        """
        ).evaluate()
        return result
