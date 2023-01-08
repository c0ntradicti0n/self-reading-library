import datetime
import json
import logging
import os
import uuid
import time
from threading import Thread
import pandas
import numpy
from franz.openrdf.repository import Repository
from franz.openrdf.sail import AllegroGraphServer
from addict import Dict
from regex import regex

from config import config

URL = "http://polarity.science"
BASE = f"{URL}/knowledge/"
# Threadsafe/processsafe replacement for queues, that will not sync in forked processes
from helpers.cache_tools import compressed_pickle, decompress_pickle


def login(db_name):
    while True:
        try:
            server = AllegroGraphServer(
                host=os.environ.get("GDB_HOST", "localhost"),
                port=10035,
                user=os.environ.get("GDB_USER", "ich"),
                password=os.environ.get("GDB_PASSWORD", "qwertz"),
            )
            catalog = server.openCatalog()
            with catalog.getRepository(db_name, Repository.ACCESS) as repository:
                repository.initialize()
                conn = repository.getConnection()
                conn.setDuplicateSuppressionPolicy("spo")
                return conn
        except Exception:
            logging.error(f"retrying graph db connection for {db_name}", exc_info=True)
        time.sleep(1)


class Queue:
    def __init__(self, service_id):
        self.conn = login(service_id)
        self.namespace = BASE + service_id
        self.service_id = service_id

        self.Value = self.conn.createURI(self.namespace + "/is")
        self.Node = self.conn.createURI(self.namespace)
        self.UserId = self.conn.createURI(self.namespace + "/user")
        self.Date = self.conn.createURI(self.namespace + "/date")
        self.RowId = self.conn.createURI(self.namespace + "/row")

        self.links = [self.Value, self.RowId, self.RowId, self.UserId]
        self.row_id = None

    def reset_old(self):
        self.conn.clear(contexts=[self.namespace])

    def id2tablename(self, id):
        return f"queue_{id}".lower()

    def query2tuples(self, query):
        res = self.conn.executeTupleQuery(query)
        return list(
            map(
                lambda b: Dict(
                    (v, str(b.getValue(v)).strip('"')) for v in b.variable_names
                ),
                res,
            )
        )

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

    def get(self, id, timeout=None, extra_q="", extra_v="", default=None):
        if timeout:
            return self.timeout(
                lambda: Queue.get(
                    self, id, extra_q=extra_q, extra_v=extra_v, default=default
                ),
                timeout=timeout,
            )
        result = self._get_df(id, extra_q=extra_q, extra_v=extra_v)
        if not result:
            return default
        item = result[0]

        try:
            return decompress_pickle(bytes.fromhex(item["value"]))
        except Exception as e:
            raise

    def determine_doc(self, user_id, doc_id):
        return f"""
            bind("{doc_id}" as ?doc_id) 
            "{self.service_id}" {self.Node} ?doc_id . 
        """
        return f"""{{{{bind("{doc_id}" as ?doc_id)
        "{self.service_id}"
        {self.Node} ?doc_id}} union
        {{
        ?doc_id
        {self.UserId}
        "{user_id}".
        }}"""

    def _get_df(self, id, row_id=None, limit=1, extra_q="", extra_v=""):

        if not id:
            q = f"""
                        select distinct ?doc_id ?user_id ?date ?row_id ?value  {extra_v} where {{
                             ?doc_id {self.Value} ?value.     
                              ?doc_id {self.Value} ?value.     
                             ?doc_id  {self.Date} ?date.      
                             ?doc_id  {self.RowId} ?row_id.      
                             ?doc_id  {self.UserId} ?user_id.  

                             {extra_q}
                            }} ORDER BY RAND() limit {limit}
                        """
        else:

            q = f"""
            select distinct ?doc_id ?user_id ?date ?row_id ?value  {extra_v} where {{
                 "{id}" {self.Value} ?value.     
                  ?doc_id {self.Value} ?value.     
                 "{id}"  {self.Date} ?date.      
                 "{id}"  {self.RowId} ?row_id.      
                 "{id}"  {self.UserId} ?user_id.  
        
                 {extra_q}
                }} limit {limit}
            """

        return self.query2tuples(q)

    def print(self):

        self.print_table()

    def print_table(self, limit=100000):
        with pandas.option_context("display.max_rows", 100, "display.max_columns", 10):
            print(f"TABLE {self.service_id}")
            q = f"""
                 select distinct ?doc_id ?user_id ?date ?row_id ?value{{
                 ?doc_id {self.Value} ?value.     
                 ?doc_id {self.Date} ?date.      
                 ?doc_id {self.RowId} ?row_id.      
                 ?doc_id {self.UserId} ?user_id.      
                }} limit {limit}
            """
            with self.conn.executeTupleQuery(q) as result:
                df = result.toPandas()
            print(df)

    def task_done(self, id):
        q = f"""
        delete {{
             "{id}" ?p ?o
        }} where {{
             values ?p {{ {' '.join([str(uri) for uri in self.links])} }}
             "{id}" ?p ?o
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
        delete {{
           ?doc_id ?p ?o 
        }} where {{
                bind ("{doc_id}" as ?doc_id)
                values ?p {{ {self.Value} {self.Date}  {self.UserId}  {self.RowId} }}.
                           "{doc_id}" ?p ?o .
        }};
        insert data
        {{
          {extra_q}
          "{self.service_id}" {self.Node} "{doc_id}" .
          "{doc_id}" {self.Value} "{data}" .
          "{doc_id}" {self.Date} "{date}" .
          "{doc_id}" {self.UserId} "{user_id}" .
          "{doc_id}"  {self.RowId} "{row_id}" .
        }} 
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
        select (count(distinct ?o) as ?c)  {{ ?s {self.Value} ?o . }}
        """
        return int(regex.findall('(\d)"\^', self.query2tuples(q)[0].c)[0])


class RatingQueue(Queue):
    def __init__(self, *args, **kwargs):
        super(RatingQueue, self).__init__(*args, **kwargs)
        self.Trial = self.conn.createURI(self.namespace + "/trial")
        self.Score = self.conn.createURI(self.namespace + "/score")
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

        scored = self.scores(doc_id, row_id=self.row_id)

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

        if isinstance(meta, dict):
            logging.error(f"Meta is null in db update?\n{doc_id=}\n{meta=}")
            return

        rating_trial = meta.get("rating_trial", 0)
        rating_score = meta.get("rating_score", 0)
        extra_q = f"""
                  "{doc_id}" {self.Trial} "{rating_trial}" .
                  "{doc_id}" {self.Score} "{rating_score}" .
        """
        super(RatingQueue, self).put(user_id, item, extra_q)

    def rate(self, doc_id, score, new_trial=True):
        scores = self.scores(doc_id)

        q = f"""
                delete data {{
                   "{scores['doc_id']}" {self.Score} "{scores['score']}" .
                   "{scores['doc_id']}" {self.Trial} "{scores['trial']}" 
                }};
                insert data
                {{
                  "{scores['doc_id']}" {self.Score} "{score}" .
                  "{scores['doc_id']}" {self.Trial} "{int(scores['trial']) +1}".
                }}
                """
        self.conn.executeUpdate(q)

    def scores(self, doc_id, row_id=None):
        q = f"""
            select ?score ?trial ?doc_id where {{
                  values ?doc_id {{ "{doc_id}" }} .
                  
                  optional {{"{doc_id}" {self.Trial} ?trial_r }} .
                  bind(coalesce(?trial_r, "0") as ?trial).

                  optional {{"{doc_id}" {self.Score} ?score_r }}.
                  bind(coalesce(?score_r, "0") as ?score).

        }}
        """
        r = self.query2tuples(q)

        try:
            return r[0]
        except:
            raise


if __name__ == "__main__":

    def new_id(pref=""):
        return pref + "_" + str(uuid.uuid4())

    user_id = "user_1"
    document_id_1 = "document_1"

    q = Queue("Q")
    q.conn.clear()
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
    q.task_done(item[0])

    q.put(user_id, (document_id_1, {"k": "v"}))
    q.put(user_id, ("blo", {"g": "f"}))
    q.put(user_id, ("bli", {"c": "w"}))

    q.get(document_id_1)

    Thread(target=q.get, args=("None",), kwargs={"timeout": 30}).start()
    Thread(target=q.put, args=("None", (document_id_1, {"k": "v"}))).start()

    time.sleep(2)
    item = q.get(document_id_1)

    q.task_done("blo")
    item = q.get(document_id_1)

    q.task_done("bli")
    q.queue_done("1")
    q.queue_done("2")

    q.print()

    r = RatingQueue("RQ")
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
