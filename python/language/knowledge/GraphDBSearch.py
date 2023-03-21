from config import config
from core.database import Queue
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec

from helpers.time_tools import timeit_context
from language.knowledge.GraphDB import GraphDB
from language.span.DifferenceSpanSet import SUBJECT, Span, DifferenceSpanSet


@converter(
    "text",
    "span_annotation.collection.graph_db",
)
class GraphDBSearch(PathSpec, Queue):
    conn = None

    def __init__(self, *args, **kwargs):
        PathSpec.__init__(self, *args, **kwargs)
        Queue.__init__(self, "difference")

    def __call__(self, prediction_metas, *args, **kwargs):
        for i, (lookup, meta) in enumerate(prediction_metas):
            self.wikidata_search(lookup)
            if "expand" in self.flags:
                meta["search"] = self.search(lookup)
            else:
                meta["search"] = self.search(lookup)
            yield lookup, meta

    def search(self, search_string, limit=100):
        query = self.query2tuples(
            query=f"""
            prefix bds: <http://www.bigdata.com/rdf/search#>
            prefix : <http://polarity.science/>
  

            select distinct(count(?mid) as ?distance) ?d ?super ?s1 ?s2 ?text1 ?text2 ?p
             where  {{ {self.graph}  {{
                ?s bds:search "{search_string}"  .
              ?super :difference* ?mid .
              {{ ?mid :difference ?s1 }} Union {{ ?mid :equal ?s1 }} Union {{ ?mid :SUBJECT ?s1 }} Union {{ ?mid :explains ?s1 }}  Union {{ ?mid :CONTRAST ?s1 }}.
              ?super ?q ?s .
              values ?p {{ :SUBJECT :CONTRAST :explains :equal :forward_difference }}.
              values ?x {{ :difference }}.

               ?s1 ?p ?s2 .
               ?d ?x  ?s1.
               ?d ?x  ?s2.
               ?s1 :text ?text1 .
               ?s2 :text ?text2 .
            }} }}
            group by ?d ?distance ?super ?s1 ?s2 ?text1 ?text2 ?p
        """
        )
        result = [{k: v["value"] for k, v in val.items()} for val in query]
        return result

    def wikidata_search(self, search_term):
        with timeit_context("searched on wikidata"):
            q = f"""
                    PREFIX       wdt:  <http://www.wikidata.org/prop/direct/>
    PREFIX        wd:  <http://www.wikidata.org/entity/>
    PREFIX        bd:  <http://www.bigdata.com/rdf#>
    PREFIX  wikibase:  <http://wikiba.se/ontology#>
    PREFIX      rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX    schema: <http://schema.org/>
    PREFIX        ps: <http://polarity.science/>
    PREFIX     mwapi: <https://www.mediawiki.org/ontology#API/>
    
    select
    *
    WHERE {{
        SERVICE <https://query.wikidata.org/sparql> {{
            SELECT * {{
            
            {{select * where {{
                          SERVICE wikibase:mwapi {{
                bd:serviceParam wikibase:endpoint "www.wikidata.org";
                wikibase:api "EntitySearch";
                    mwapi:search "{search_term}";
                mwapi:language "en".
                ?concept1 wikibase:apiOutputItem mwapi:item.
                ?num wikibase:apiOrdinal true.
            }}
            ?concept1  (wdt:P279) ?class .
            ?concept2  (wdt:P279) ?class .
              }}  order by ?num  limit 20 }}


    
                SERVICE wikibase:label {{
                    bd:serviceParam wikibase:language "en".
                    ?concept1 rdfs:label ?concept1_label.
                    ?concept1 schema:description ?concept1_description.
    
                    ?concept2 rdfs:label ?concept2_label.
                    ?concept2 schema:description ?concept2_description.
    
                    ?class rdfs:label ?class_label.
                }}
                FILTER ( ?concept1_label != ?class_label ).
                FILTER ( ?concept2_label != ?class_label ).
                FILTER ( ?concept2_label != ?concept1_label ).
    
                FILTER (!regex(?concept2_label, "Q\\\\d+","i")) .
                FILTER (STRLEN(?concept2_description) != 0)  .
                FILTER (!regex(?concept1_label, "Q\\\\d+","i")) .
                FILTER (STRLEN(?concept1_description) != 0)  .
    
                BIND (MD5(?concept1_description) AS ?c1)
                BIND( IRI(CONCAT(STR(ps:), ?c1)) as ?contrast1)
                BIND (MD5(?concept2_description) AS ?c2)
                BIND( IRI(CONCAT(STR(ps:), ?c2)) as ?contrast2)
    
            }} LIMIT 10000
        }}
    }}
    """
            with self.commit as com:

                qs = self.query2values(q)
                for i, q in enumerate(qs):
                    DifferenceSpanSet(wikidata=q).add_graph_db(com)

    def expand(self, node_id, limit=100):
        query = self.query2tuples(
            query=f"""
            prefix : <http://polarity.science/>
            
            select distinct(count(?mid) as ?distance) ?super ?s1 ?s2 ?text1 ?text2 ?p
             where  {{ {self.graph}  {{
               values ?s {{ <{node_id}> }}  .
              ?super :difference* ?mid .
              {{ ?mid :difference ?s1 }} Union {{ ?mid :equal ?s1 }} Union {{ ?mid :SUBJECT ?s1 }} Union {{ ?mid :explains ?s1 }}  Union {{ ?mid :CONTRAST ?s1 }}.
              ?super ?q ?s .
              values ?p {{ :SUBJECT :CONTRAST :explains :equal :forward_difference }}
                      ?s1 ?p ?s2 .
                      ?s1 :text ?text1 .
                      ?s2 :text ?text2 .
            }} }}
            group by ?distance ?super ?s1 ?s2 ?text1 ?text2 ?p
        """
        )
        result = [{k: v["value"] for k, v in val.items()} for val in query]
        return result
