# Import the necessary libraries
import urllib
from pprint import pprint

import requests
from franz.openrdf.repository import Repository
from franz.openrdf.sail import AllegroGraphServer
from franz.openrdf.vocabulary import RDF

from helpers.list_tools import metaize
from helpers.nested_dict_tools import flatten
from language.knowledge.GraphDB import GraphDB
from language.knowledge.GraphDBSearch import GraphDBSearch
from language.knowledge.NodeEdges import NodeEdges
from language.span.DifferenceSpanSet import DifferenceSpanSet, Span

base = "http://polarity.science/knowledge/"
server = AllegroGraphServer(host="localhost", port=10035, user="ich", password="qwertz")
catalog = server.openCatalog()


v = {
    0: [
        (
            "CONTRAST",
            [
                ["believes", "B", "CONTRAST", 14],
                ["in", "I", "CONTRAST", 15],
                ["an", "I", "CONTRAST", 16],
                ["omnipresent", "I", "CONTRAST", 17],
                [",", "I", "CONTRAST", 18],
                ["omnipotent", "I", "CONTRAST", 19],
                ["God", "I", "CONTRAST", 20],
                [",", "I", "CONTRAST", 21],
                ["the", "I", "CONTRAST", 22],
                ["Almighty", "I", "CONTRAST", 23],
                ["Father", "L", "CONTRAST", 24],
            ],
        ),
        ("SUBJECT", [["Catholicism", "U", "SUBJECT", 13]]),
    ],
    1: [
        (
            "CONTRAST",
            [
                ["does", "B", "CONTRAST", 28],
                ["not", "I", "CONTRAST", 29],
                [".", "I", "CONTRAST", 30],
                ["The", "I", "CONTRAST", 31],
                ["closest", "I", "CONTRAST", 32],
                ["thing", "I", "CONTRAST", 33],
                ["to", "I", "CONTRAST", 34],
                ["God", "I", "CONTRAST", 35],
                ["would", "I", "CONTRAST", 36],
                ["be", "I", "CONTRAST", 37],
                ["Siddhartha", "I", "CONTRAST", 38],
                ["Gautama", "I", "CONTRAST", 39],
                [",", "I", "CONTRAST", 40],
                ["the", "I", "CONTRAST", 41],
                ["first", "I", "CONTRAST", 42],
                ["Buddha", "I", "CONTRAST", 43],
                ["to", "I", "CONTRAST", 44],
                ["achieve", "I", "CONTRAST", 45],
                ["spiritual", "I", "CONTRAST", 46],
                ["enlightenment", "L", "CONTRAST", 47],
            ],
        ),
        ("SUBJECT", [["Buddhism", "U", "SUBJECT", 27]]),
    ],
}
dss = DifferenceSpanSet(v)
with catalog.getRepository("difference", Repository.ACCESS) as repository:
    repository.initialize()
    with repository.getConnection() as conn:
        #conn.clear()
        dss.add_graph_db(conn)

        conn.createFreeTextIndex("index1", tokenizer="japanese", predicates=Span.FTS_Uris, wordFilters=[], stopWords=[])

        config = conn.getFreeTextIndexConfiguration("index1")
        for key, value in config.items():
            if isinstance(value, list):
                value = ", ".join(str(x) for x in value)
            print("{key}: {value}".format(key=key, value=value))

        pprint(GraphDBSearch.search("premise"))
        pprint(list(NodeEdges(GraphDBSearch(metaize(["premise"])))))
        pprint(list(NodeEdges(GraphDBSearch(metaize(["sex"])))))

