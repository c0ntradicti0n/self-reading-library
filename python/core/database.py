import datetime
import logging
import os
import uuid
import time
from threading import Thread
import pandas
import rdflib
from addict import Dict
from SPARQLWrapper import SPARQLWrapper, JSON, POST
from rdflib import Graph, Literal
from rdflib.term import Node

from config import config

URL = "http://polarity.science"
BASE = f"{URL}"
# Threadsafe/processsafe replacement for queues, that will not sync in forked processes
from helpers.cache_tools import compressed_pickle, decompress_pickle


def login(db_name):
    while True:
        try:
            conn_str = f"http://{os.environ.get('DB', 'localhost:12345')}/blazegraph/namespace/difference/sparql"
            logging.info(conn_str   )
            server = SPARQLWrapper(conn_str )
            server.setMethod(POST)
            server.conn_str= conn_str

            server.setReturnFormat(JSON)

            user = os.environ.get("DB_USER", "ich")
            password = os.environ.get("DB_PASSWORD", "qwertz")

            server.setCredentials(user, password)

            def do(q):

                server.setQuery(q)

                logging.warning(server.conn_str)

                return server.queryAndConvert()

            server.executeUpdate = do

            return server
        except Exception:
            logging.error(f"retrying graph db connection for {db_name}", exc_info=True)
        time.sleep(1)


class Queue:
    @staticmethod
    def uri_wrap(u):
        return u

    def __init__(self, service_id):
        self.db = f"http://{os.environ.get('DB', 'localhost:12345')}/blazegraph"
        self.conn = login(service_id)

        self.namespace = BASE  # + service_id
        self.service_id = service_id
        self.graph = f"GRAPH {self.u(self.service_id)} "
        self.from_graph = f"FROM {self.u(self.service_id)} "

        self.Graph = self.uu(self.service_id)

        self.Value = self.u("is")
        self.Node = self.u(self.uri_wrap("node"))
        self.UserId = self.u(self.uri_wrap("user"))
        self.Date = self.u(self.uri_wrap("date"))
        self.RowId = self.u(self.uri_wrap("row"))

        self.links = [self.Value, self.RowId, self.RowId, self.UserId]
        self.row_id = None

    @staticmethod
    def uu(v):
        return rdflib.URIRef(
            Queue.uri_wrap(((BASE + "/") if not v.startswith("http") else "") + v)
        )

    def u(self, v):
        return "<" + self.uu(v) + ">"

    def clear(self):
        self.conn.executeUpdate(
            f"""
           DROP {self.graph}

            """
        )

    def reset_old(self):
        self.conn.clear(contexts=[self.namespace])

    def id2tablename(self, id):
        return f"queue_{id}".lower()

    def query2tuples(self, query):
        res = self.conn.executeUpdate(query)
        return res["results"]["bindings"]

    def query2values(self, q):
        return [{k: v["value"] for k, v in val.items()} for val in self.query2tuples(q)]

    def get_doc_ids(self):
        q = f"""select ?doc_id where {{
               "{self.service_id}"  {self.Node} ?doc_id 
        }}"""
        return [r["doc_id"] for r in self.query2tuples(q)]

    def timeout(self, f, timeout=None):
        # Database polling until value appeared or not
        result = None
        n = 0
        while not result:
            n += 1
            if n > timeout:
                break
            result = f()
            if result:
                break
            time.sleep(1)

        return result

    def get(
        self, id, timeout=None, extra_q="", extra_v="", default=None, special_info=None
    ):
        if timeout:
            return self.timeout(
                lambda: Queue.get(
                    self,
                    id,
                    extra_q=extra_q,
                    extra_v=extra_v,
                    default=default,
                    special_info=special_info,
                ),
                timeout=timeout,
            )
        if special_info:
            print(special_info + ": " + str(id))
        result = self._get_df(id, extra_q=extra_q, extra_v=extra_v)
        if special_info:
            print(special_info + ":'" + str(result))
        if not result:
            return default
        item = result[0]

        try:
            return decompress_pickle(bytes.fromhex(item["value"]["value"]))
        except Exception as e:
            raise

    def determine_doc(self, user_id, doc_id):
        return f"""
            bind( {self.u(doc_id)} as ?doc_id) 
            {self.u(self.service_id)} {self.Node} ?doc_id . 
        """
        return f"""{{{{bind( {self.u(doc_id)} as ?doc_id)
        {self.u(self.service_id)}
        {self.Node} ?doc_id}} union
        {{
        ?doc_id
        {self.UserId}
        "{user_id}".
        }}"""

    def _get_df(self, id, row_id=None, limit=1, extra_q="", extra_v=""):

        if not id:
            q = f"""
                        select distinct ?doc_id ?user_id ?date ?row_id ?value  {extra_v} {self.from_graph} where {{
                             ?doc_id {self.Value} ?value.     
                             ?doc_id {self.Value} ?value.     
                             ?doc_id  {self.Date} ?date.      
                             ?doc_id  {self.RowId} ?row_id.      
                             ?doc_id  {self.UserId} ?user_id.  

                             {extra_q}
                            }} ORDER BY UUID() limit {limit}
                        """
        else:

            q = f"""
            select distinct ?doc_id ?user_id ?date ?row_id ?value  {extra_v} {self.from_graph} where {{
                 {self.u(id)} {self.Value} ?value.     
                  ?doc_id {self.Value} ?value.     
                 {self.u(id)}  {self.Date} ?date.      
                 {self.u(id)}  {self.RowId} ?row_id.      
                 {self.u(id)}  {self.UserId} ?user_id.  
                 {extra_q}
                }} limit {limit}
            """

        return self.query2tuples(q)

    def get_all_by_id(self, id):
        res = self.query2tuples(
            f"""
        
            select distinct  ?p ?o   {self.from_graph} where {{ {self.u(id)} ?p ?o }}
        """
        )
        return {r["p"]["value"].replace(BASE + "/", ""): r["o"]["value"] for r in res}

    def print(self):

        self.print_table()

    def print_table(self, limit=100000):
        with pandas.option_context("display.max_rows", 100, "display.max_columns", 10):
            print(f"TABLE {self.service_id}")
            q = f"""
                 select distinct ?doc_id ?user_id ?date ?row_id ?value {self.from_graph} {{
                 ?doc_id {self.Value} ?value.     
                 ?doc_id {self.Date} ?date.      
                 ?doc_id {self.RowId} ?row_id.      
                 ?doc_id {self.UserId} ?user_id.      
                }} limit {limit}
            """
            result = [
                {k: v["value"] for k, v in val.items()} for val in self.query2tuples(q)
            ]
            df = pandas.DataFrame.from_records(result)
            print(df)

    def task_done(self, id):
        q = f"""
        delete {{ {self.graph} {{ 
             {self.u(id)} ?p ?o
        }} }} where {{ {self.graph} {{
             values ?p {{ {' '.join([str(uri) for uri in self.links])} }}
             {self.u(id)} ?p ?o
            }}
        }}
        """
        self.conn.executeUpdate(q)

    def queue_done(self, id=None):
        q = f"""
                delete {{
                            ?id ?p ?o
                }} where {{
                           {self.determine_doc(id, id)}
                }}
                """
        res = self.conn.executeUpdate(q)
        print(res)

    def put(self, user_id, item, extra_q="", timeout=None):
        if isinstance(item, tuple):
            doc_id = item[0]
        else:
            raise ValueError(f"item must be a tuple of id and value! {item}")

        date = datetime.datetime.utcnow()
        data = compressed_pickle(item).hex()
        row_id = uuid.uuid4().hex
        q = f"""  
        delete {{ {self.graph} {{
           ?doc_id ?p ?o 
        }} }} where {{ {self.graph} {{
                bind ({self.u(doc_id)} as ?doc_id)
                values ?p {{ {self.Value} {self.Date}  {self.UserId}  {self.RowId} }}.
                           {self.u(doc_id)} ?p ?o .
        }} }};
        insert data
        {{ {self.graph} {{
          {extra_q}
          {self.u(self.service_id)} {self.Node} {self.u(doc_id)} .
          {self.u(doc_id)} {self.Value} "{data}" .
          {self.u(doc_id)} {self.Date} "{date}" .
          {self.u(doc_id)} {self.UserId} "{user_id}" .
          {self.u(doc_id)}  {self.RowId} "{row_id}" .
        }}  }}
        """
        try:
            res = self.conn.executeUpdate(q)
            if not res:
                raise RuntimeError("Could not update database!!!")
        except Exception as e:
            raise
            raise ValueError("wrong datatype for table!") from e

    def update(self, user_id, item):
        Queue.put(self, user_id, item)

    def __len__(self):
        q = f"""
        select (count(distinct ?o) as ?c) {self.from_graph} {{ ?s {self.Value} ?o . }}
        """
        return int(self.query2tuples(q)[0]["c"]["value"])

    class _commit:
        def __init__(self, conn):
            self.q = self
            self.conn = conn
            self.u = Queue.u
            self.g = Graph()

        def __enter__(self):
            return self

        def executeUpdate(self, q):
            self.g.update(q)

        def add_triples(self, qs):
            for q in qs:
                q = self.rdf_typize(q)
                self.g.add(tuple(q))

        def rdf_typize(self, q, uri_target=False):
            q = list(q)
            for i, e in enumerate(q):
                if i in [0, 1] + ([] if not uri_target else [2]) and not isinstance(
                    e, Node
                ):
                    q[i] = self.conn.uu(e)
                elif not isinstance(e, Node):
                    q[i] = Literal(e)
            return tuple(q)

        def add_triple(self, q, uri_target=False):
            q = self.rdf_typize(q, uri_target=uri_target)
            self.g.add(tuple(q))

        def add_triples(self, qs):
            for q in qs:
                q = self.rdf_typize(q)
                self.g.add(tuple(q))

        def __exit__(self, exc_type, exc_val, exc_tb):
            g_str = self.g.serialize()
            with open(f"{config.hidden_folder}/{self.conn.service_id}.ttl", "w") as f:
                f.write(g_str)
            os.system(
                f"""curl -D- -H 'Content-Type: text/turtle' --upload-file {config.hidden_folder}/{self.conn.service_id}.ttl -X POST '{self.conn.db}/namespace/{self.conn.service_id}/sparql?context-uri={self.conn.Graph}'"""
            )

    @property
    def commit(self):
        return Queue._commit(self)


class RatingQueue(Queue):
    def __init__(self, *args, **kwargs):
        super(RatingQueue, self).__init__(*args, **kwargs)
        self.Trial = self.u("trial")
        self.Score = self.u("score")
        self.links += [self.Trial, self.Score]

    def get(self, doc_id, timeout=None, extra_q="", default=None):
        try:
            result = Queue.get(
                self,
                doc_id,
                timeout=timeout,
                extra_q=extra_q,
                extra_v="?score ?trial",
                default=default,
            )
        except Exception as e:
            raise

        if not result:
            return default
        else:
            db_id, meta = result

        scored = self.scores(doc_id if doc_id else db_id, row_id=self.row_id)

        meta["rating_trial"] = scored.trial
        meta["rating_score"] = scored.score

        return db_id, meta

    def get_ready(self, doc_id, timeout=None):
        return self.get(
            doc_id,
            extra_q=f"""
        ?doc_id {self.Trial} ?trial.
        filter(?trial >= "{config.MIN_CAPTCHA_TRIALS}")
        """,
            timeout=timeout,
            default=[],
        )

    def put(self, user_id, item, timeout=None):
        doc_id, meta = item

        if not isinstance(meta, dict):
            logging.error(f"Meta is null in db update?\n{doc_id=}\n{meta=}")
            return

        rating_trial = meta.get("rating_trial", 0)
        rating_score = meta.get("rating_score", 0)
        extra_q = f"""
                  {self.u(doc_id)}  {self.Trial} "{rating_trial}" .
                  {self.u(doc_id)} {self.Score} "{rating_score}" .
        """
        super(RatingQueue, self).put(user_id, item, extra_q)

    def rate(self, doc_id, score, new_trial=True):
        scores = self.scores(doc_id)

        q = f"""
                delete {{ {self.graph} {{
                   {self.u(doc_id)} {self.Score} ?score .
                   {self.u(doc_id)} {self.Trial} ?trial . 
                }} }} where {{ {self.graph} {{
                   {self.u(doc_id)} {self.Score} ?score .
                   {self.u(doc_id)} {self.Trial} ?trial .
                }} }};
                insert data {{ {self.graph}
                {{
                  {self.u(doc_id)} {self.Score} "{score}" .
                  {self.u(doc_id)} {self.Trial} "{int(scores['trial']) +1}".
                }} }}
                """
        self.conn.executeUpdate(q)

    def scores(self, doc_id, row_id=None):
        q = f"""
            select ?score ?trial ?doc_id {self.from_graph} where {{ {self.graph} {{
                  values ?doc_id {{ {self.u(doc_id)} }} .
                  
                  optional {{{self.u(doc_id)} {self.Trial} ?trial_r }} .
                  bind(coalesce(?trial_r, "0") as ?trial).

                  optional {{{self.u(doc_id)} {self.Score} ?score_r }}.
                  bind(coalesce(?score_r, "0") as ?score).

        }} }}
        """
        r = self.query2tuples(q)

        try:
            r = r[0]
            return Dict({k: v["value"] for k, v in r.items()})
        except:
            raise


if __name__ == "__main__":

    def new_id(pref=""):
        return pref + "_" + str(uuid.uuid4())

    user_id = "user_1"
    document_id_1 = "document_1"

    q = Queue("Q")
    g = Graph()

    u = q.uu("xxx")
    g.add((u, rdflib.Literal("789"), rdflib.Literal("2")))
    g.serialize()

    q.clear()
    q.put(user_id, (document_id_1, {"k": "v"}))
    q.get(document_id_1)
    q.task_done(document_id_1)

    user_id_2 = "user_2"
    user_id_3 = "user_3"
    user_id_4 = "user_4"

    q = Queue("Q2")
    q.queue_done(user_id)

    q.put(user_id_3, (document_id_1, {"k": "v"}))
    q.put(user_id_4, (document_id_1, {"k": "v"}))
    q.put(user_id, (document_id_1, {"k": "v"}))

    item = q.get(document_id_1)
    print(item)
    assert item
    q.task_done(item[0])

    q.put(user_id, (document_id_1, {"k": "v"}))
    q.put(user_id, ("blo", {"g": "f"}))
    q.put(user_id, ("bli", {"c": "w"}))

    q.get(document_id_1)

    def check_get(val):
        assert q.get(val, timeout=30, special_info="X")

    Thread(target=check_get, args=(None,)).start()
    Thread(target=q.put, args=(None, (document_id_1, {"k": "v"}))).start()

    time.sleep(2)
    item = q.get(document_id_1)

    q.task_done("blo")
    item = q.get(document_id_1)

    q.task_done(document_id_1)
    item = q.get(document_id_1)
    assert not item

    item = q.get(None)
    assert item
    q.task_done(item[0])
    item = q.get(None)
    assert not item
    q.put(user_id, (document_id_1, {"k": "v"}))
    q.put(user_id, ("blo", {"g": "f"}))
    q.put(user_id, ("bli", {"c": "w"}))

    q.queue_done("1")
    q.queue_done("2")

    q.print()

    r = RatingQueue("RQ")

    def check_get_ready(val):
        print("get_READY", x := r.get_ready(val, timeout=30))
        assert x

    Thread(target=check_get_ready, args=(None,)).start()
    r.put("1", (document_id_1, {"k": "v"}))

    id = str(uuid.uuid4())
    r.put(id, ("other_doc", {"k": "v", "labels": [1, 1, 0, 1]}))
    r.put(id, ("another_doc", {"k": "v", "labels": [1, 1, 0, 1]}))

    r.put("other_doc", (document_id_1, {"k": "v", "labels": [1, 1, 0, 1]}))
    r.rate("other_doc", 0.123)
    r.rate("other_doc", 0.567)
    r.rate("other_doc", 0.789)

    scored = r.scores("other_doc")
    assert scored.trial == "3"
    assert scored.score == "0.789"

    rq_username_2 = str(uuid.uuid4())
    document_id_2 = new_id()
    r.put(rq_username_2, (document_id_2, {"k": "v", "rating_score": 0.1234}))
    scored = r.scores(document_id_2)

    assert scored.trial == "0"
    assert scored.score == "0.1234"

    scored = r.scores("other_doc")
    assert scored.trial == "3"
    assert scored.score == "0.789"

    doc_id, meta = r.get(document_id_2)
    assert meta["rating_score"] == "0.1234"
    assert meta["rating_trial"] == "0"

    doc_id, meta = r.get(doc_id)
    assert meta["rating_score"] == "0.1234"
    assert meta["rating_trial"] == "0"

    r.update(rq_username_2, (doc_id, {}))
    user_id, meta = r.get(doc_id)
    print(meta)
    assert meta == {"rating_trial": "0", "rating_score": "0.1234"}

    assert len(r) > 2

    print(q.get_doc_ids())
    print(r.get_doc_ids())

    x = q.get(None)
    assert x

    with q.commit as conn:
        conn.add_triple(("k", "rel", "v"))

    res = q.get_all_by_id("k")
    assert res["rel"] == "v"
