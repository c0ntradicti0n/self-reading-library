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
from config.config import BASE

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
                return repository.getConnection()
        except Exception as e:
            logging.error(f"retrying graph db connection for {db_name}", exc_info=True)
        time.sleep(1)


class Queue:
    def __init__(self, service_id):
        self.conn = login(config.DB_NAME)
        self.namespace = BASE + "Queue"
        self.service_id = service_id

        self.Value = self.conn.createURI(self.namespace + "/is")
        self.Node = self.conn.createURI(self.namespace)
        self.UserId = self.conn.createURI(self.namespace + "/user")
        self.Date = self.conn.createURI(self.namespace + "/date")
        self.RowId = self.conn.createURI(self.namespace + "/row")

        self.row_id = None

    def reset_old(self):
        self.conn.clear(contexts=[self.namespace])

    def id2tablename(self, id):
        return f"queue_{id}".lower()

    def query2tuples(self, query):
        res = self.conn.executeTupleQuery(query)
        return list(map(lambda b: Dict((v,str(b.getValue(v)).strip('"')) for v in b.variable_names), res))

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
            try:
                result = f()
            except Exception as e:
                time.sleep(1)

                continue
        return result

    def get(self, id, timeout=None):
        if timeout:
            return self.timeout(lambda: self.get(id), timeout=timeout)

        item = self._get_df(id)[0]
        if item is None:
            return item
        try:
            return decompress_pickle(bytes.fromhex(item["value"]))
        except Exception as e:
            raise
            raise ValueError(f"Strange value in {self.service_id}, {item}") from e

    def _get_df(self, id, row_id=None, limit=1, extra_q = "", extra_v= ""):
        if row_id:
            row = f"""
            values ?r {{{row_id}}}
            {self.Node} ?{self.row_id} ?t.
            """
        else:
            row = ""
        q = f"""
        select distinct ?doc_id ?user_id ?date ?row_id ?value  {extra_v} where {{
            
            {row}
            {{ "{id}" {self.Value} ?value }} union
            {{ ?doc_id {self.UserId} "{id}" }}.
             ?doc_id {self.Value} ?value.     
             ?doc_id {self.Date} ?date.      
             ?doc_id {self.RowId} ?row_id.      
             ?doc_id {self.UserId} ?user_id.      
             {extra_q}
            }} limit {limit}
        """
        return self.query2tuples(q)

    def print(self):

        self.print_table()

    def print_table(self, limit = 100000):
        with pandas.option_context('display.max_rows', 100, 'display.max_columns', 10):
            print(f"TABLE {self.service_id}")
            q= f"""
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
                    ?id ?p ?o
        }} where {{
                   {{ bind("{id}" as ?id)  "{self.service_id}"  {self.Node}  ?id }} union
                   {{  ?id {self.UserId} "{id}" }}.
                                   values ?p {{ {self.Value} {self.Date}  {self.UserId}   {self.RowId} }}

        }}
        """
        res = self.conn.executeUpdate(q)
        print (res)

    def delete_task(self, id=None):
        self.connection.conn.execute(
            f"DELETE from {self.service_id} where user_id = '{self.row_id if not id else id}'"
        )

    def queue_done(self, id=None):
        q = f"""
                delete {{
                            ?id ?p ?o
                }} where {{
                           {{ bind("{id}" as ?id) ?id {self.Node}  ?s }} .
                }}
                """
        res = self.conn.executeUpdate(q)
        print (res)

    def put(self, id, item, extra_q = "", timeout=None):
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
        }} where
               {{ {{  bind ("{doc_id}" as ?doc_id)
                            "{self.service_id}" {self.Node} ?doc_id }} union {{
                        ?doc_id  <http://polarity.science/knowledge/Queue/user> "{id}".
                }} .
                values ?p {{ {self.Value} {self.Date}  {self.UserId}   {self.RowId} }}
        }};
        insert data
        {{
          "{self.service_id}" {self.Node} "{doc_id}".
          {extra_q}
          "{doc_id}" {self.Value} "{data}" .
          "{doc_id}" {self.Date} "{date}" .
          "{doc_id}" {self.UserId} "{id}" .
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

    def update(self, id, item):
        Queue.put(self, id, item)

    def __len__(self):
        q = f"""
        SELECT (count(distinct ?s) as ?c)  {{ ?s {self.Value} ?o . }}
        """
        return int(regex.findall('(\d)\"\^', self.query2tuples(q)[0].c)[0])


class RatingQueue(Queue):
    def __init__(self, *args, **kwargs):
        super(RatingQueue, self).__init__(*args, **kwargs)
        self.Trial = self.conn.createURI(self.namespace + "/trial")
        self.Score = self.conn.createURI(self.namespace + "/score")

    def get(self, id, timeout=None):
        try:
            result = Queue.get(self, id, timeout=timeout)
        except Exception as e:
            raise

        if not result:
            return None
        else:
            db_id, meta = result

        scored = self.scores(id, row_id=self.row_id)

        meta["rating_trial"] = (
            scored.trial
        )
        meta["rating_score"] = (
            scored.score
        )

        return db_id, meta

    def put(self, id, item, timeout=None):
        doc_id, meta = item

        rating_trial = meta.get("rating_trial", 0)
        rating_score = meta.get("rating_score", 0)
        extra_q = f"""
                  "{doc_id}" {self.Trial} "{rating_trial}" .
                  "{doc_id}" {self.Score} "{rating_score}" .
        """
        super(RatingQueue, self).put(id, item, extra_q)


    def rate(self, user_id, score, new_trial=True):
        scores = self.scores(id)

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

    def scores(self, id, row_id=None):
        q = f"""
        select ?score ?trial ?doc_id where {{
              ?doc_id {self.UserId} "{id}".
                  ?doc_id {self.Trial} ?trial . 
                  ?doc_id {self.Score} ?score . 
                }}
                """

        return self.query2tuples(q)[0]


if __name__ == "__main__":
    def new_id (pref=""):
        return pref  + "_" + str(uuid.uuid4())
    doc_id = "1123_123"

    q = Queue("123_234")
    q.conn.clear()
    q.put(doc_id, ("bla", {"k": "v"}))
    q.get(doc_id)
    q.task_done(doc_id)

    doc_id = "abcd"

    q = Queue("test")
    q.queue_done("None")
    q.queue_done(doc_id)

    q.put("1", ("bla", {"k": "v"}))
    q.put("2", ("bla", {"k": "v"}))

    q.put(doc_id, ("bla", {"k": "v"}))
    item = q.get(doc_id)
    print(item)
    q.task_done(item[0])
    q.put(doc_id, ("bla", {"k": "v"}))
    q.put(doc_id, ("blo", {"g": "f"}))
    q.put(doc_id, ("bli", {"c": "w"}))

    q.get(doc_id)

    Thread(target=q.get, args=("None",), kwargs={"timeout": 30}).start()
    Thread(target=q.put, args=("None", ("bla", {"k": "v"}))).start()

    time.sleep(2)
    item = q.get(doc_id)

    q.task_done(item[0])
    item = q.get(doc_id)

    q.task_done(item[0])
    q.queue_done("1")
    q.queue_done("2")

    q.print()

    r = RatingQueue("rating_queue_TEST")
    r.put("1", ("bla", {"k": "v"}))

    id = str(uuid.uuid4())
    r.put(id, ("bla", {"k": "v", "labels": [1, 1, 0, 1]}))
    r.rate(id, 0.123)
    r.rate(id, 0.567)
    r.rate(id, 0.789)

    scored = r.scores(id)
    assert scored.trial == "3"
    assert scored.score == "0.789"

    id2 = str(uuid.uuid4())
    r.put(id2, (new_id(), {"k": "v", "rating_score": 0.1234}))
    scored = r.scores(id2)

    assert scored.trial == "0"
    assert scored.score == "0.1234"

    scored = r.scores(id)
    assert scored.trial == "3"
    assert scored.score == "0.789"

    doc_id, meta = r.get(id2)
    assert meta["rating_score"] == "0.1234"
    assert meta["rating_trial"] == "0"

    r.update(id2, (id2, {}))
    doc_id, meta = r.get(id2)
    print(meta)
    assert meta == {"rating_trial": "0", "rating_score": "0.1234"}

    assert len(r) > 2

    print(q.get_doc_ids())
    print(r.get_doc_ids())

