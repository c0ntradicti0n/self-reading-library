import datetime
import json
import logging
import uuid
import time
from threading import Thread
import ibis
import pandas
import numpy

from config import config

# Threadsafe/processsafe replacement for queues, that will not sync in forked processes
from helpers.cache_tools import compressed_pickle, decompress_pickle

ibis.options.interactive = True


class Queue:
    connection = None

    schema = [
        ("doc_id", "string"),
        ("user_id", "string"),
        ("date", "date"),
        ("value", "string"),
        ("row_id", "string"),
    ]

    def __init__(self, service_id):
        self.row_id = None
        self.service_id = self.id2tablename(service_id)
        connection_str = f"postgresql://python:python@{config.DB_HOST}:5432/postgres"
        if not Queue.connection:
            Queue.connection = ibis.postgres.connect(url=connection_str)
        sc = ibis.schema(self.schema)

        self.table = None
        while self.table is None:
            try:

                self.table = self.connection.table(self.service_id)

            except Exception as e:
                try:
                    logging.error(f"Table '{self.service_id}' does not exist?")
                    Queue.connection.create_table(self.service_id, schema=sc)
                    self.table = self.connection.table(self.service_id)
                except:
                    logging.error(f"Table '{self.service_id}' could not be created.")

    def id2tablename(self, id):
        return f"queue_{id}".lower()

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

        item = self._get_df(id)
        try:
            return decompress_pickle(bytes.fromhex(item.iloc[0]["value"]))
        except Exception as e:
            raise ValueError(f"Strange value in {self.service_id}, {item}") from e

    def _get_df(self, id):
        item = (
            self.table.filter(self.table["doc_id"] == id)
            .sort_by("date")
            .limit(10)
            .execute()
        )
        if item.empty:
            item = (
                self.table.filter(self.table["user_id"] == id)
                .sort_by("date")
                .limit(10)
                .execute()
            )
        self.row_id = item.iloc[0].row_id
        return item

    def print(self):
        for table in self.connection.list_tables():
            self.print_table(table)

    def print_table(self, table=None):
        print(f"TABLE {self.service_id}")
        print(
            self.connection.table(self.service_id if not table else table)
            .limit(10000)
            .execute()
        )

    def task_done(self, id=None):
        self.connection.con.execute(
            f"DELETE from {self.service_id} where row_id = '{self.row_id if not id else id}'"
        )

    def queue_done(self, id=None):
        self.connection.con.execute(
            f"DELETE from {self.service_id} where doc_id = '{id}'"
        )

    def put(self, id, item, timeout=None):
        if isinstance(item, tuple):
            doc_id = item[0]
        else:
            raise ValueError(f"item must be a tuple of id and value! {item}")
        df_item = pandas.DataFrame(
            [
                (
                    doc_id,
                    id,
                    datetime.datetime.now(),
                    compressed_pickle(item).hex(),
                    uuid.uuid4().hex,
                )
            ],
            columns=["doc_id", "user_id", "date", "value", "row_id"],
        )
        try:
            self.connection.insert(self.service_id, df_item)
        except Exception as e:
            raise ValueError("wrong datatype for table!") from e

    def __len__(self):
        # Idiots invented an incompatible IntegerScalar
        return int(str(self.table.count()))


class RatingQueue(Queue):
    schema = Queue.schema + [
        ("rating_trial", "int32"),
        ("rating_score", "float"),
        ("version", "json"),
    ]

    def get(self, id, timeout=None):
        db_id, meta = Queue.get(self, id, timeout=timeout)
        rating_trial, rating_score, version = self.scores(id)

        meta["rating_trial"] = (
            float(rating_trial) if rating_trial and not numpy.isnan(trials) else 0
        )
        meta["rating_score"] = (
            float(rating_score) if not numpy.isnan(rating_score) else 0.0
        )
        meta["version"] = version if version else []

        return db_id, meta

    def put(self, id, item, timeout=None):
        db_id, meta = item
        Queue.put(self, id, item, timeout=timeout)
        if score := meta.get("rating_score"):
            self.rate(db_id if not id else id, score, None, new_trial=False)

    def rate(self, id, score, version, new_trial=True):
        if version:
            version_update = f"version= coalesce(version::jsonb, '[]'::jsonb)  || '[{json.dumps(version)}]'::jsonb,"
        else:
            version_update = ""
        self.connection.con.execute(
            f"UPDATE {self.service_id} set  {version_update} rating_score = {score}, rating_trial = {'COALESCE(rating_trial, 0) + 1' if new_trial else 'COALESCE(rating_trial, 0)'} where doc_id = '{self.row_id if not id else id}' or user_id = '{self.row_id if not id else id}'"
        )

    def scores(self, id):
        item = self._get_df(id)
        if len(item) != 1:
            logging.warning(f"Multiple items with the same id in {self.service_id}")
        trials, scores, version = (
            item["rating_trial"][0],
            item["rating_score"][0],
            item["version"][0],
        )

        return (
            float(trials) if trials and not numpy.isnan(trials) else 0,
            float(scores) if not numpy.isnan(scores) else 0.0,
            version if version else [],
        )


if __name__ == "__main__":
    doc_id = "1123_123"

    q = Queue("123_234")
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
    q.task_done()
    q.put(doc_id, ("bla", {"k": "v"}))
    q.put(doc_id, ("blo", {"g": "f"}))
    q.put(doc_id, ("bli", {"c": "w"}))

    q.get(doc_id)

    Thread(target=q.get, args=("None",), kwargs={"timeout": 30}).start()
    Thread(target=q.put, args=("None", ("bla", {"k": "v"}))).start()

    time.sleep(2)
    q.task_done()
    q.task_done()
    q.queue_done("1")
    q.queue_done("2")

    q.print()

    r = RatingQueue("rating_queue_TEST")
    r.put("1", ("bla", {"k": "v"}))

    id = str(uuid.uuid4())
    r.put(id, ("bla", {"k": "v", "labels": [1, 1, 0, 1]}))
    r.rate(id, 0.123, [0, 1, 1, 0])
    r.rate(id, 0.567, [0, 1, 1, 2])
    r.rate(id, 0.789, [3, 1, 1, 0])

    trial, score, version = r.scores(id)
    assert trial == 3
    assert score == 0.789

    id2 = str(uuid.uuid4())
    r.put(id2, ("bla", {"k": "v", "rating_score": 0.1234}))
    trial, score, version = r.scores(id2)
    assert trial == 0
    assert score == 0.1234

    trial, score, version = r.scores(id)
    assert trial == 3
    assert score == 0.789
    assert version == [[0, 1, 1, 0], [0, 1, 1, 2], [3, 1, 1, 0]]

    doc_id, meta = r.get(id2)
    assert meta["rating_score"] == 0.1234
    assert meta["rating_trial"] == 0
    assert meta["version"] == []

    assert len(r) > 2
