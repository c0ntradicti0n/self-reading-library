import datetime
import uuid
import time
from threading import Thread
import ibis
import pandas

# Threadsafe/processsafe replacement for queues, that will not sync in forked processes
from helpers.cache_tools import compressed_pickle, decompress_pickle

ibis.options.interactive = True

class Queue:
    connection = None

    def __init__(self, service_id):
        self.row_id = None
        self.service_id = self.id2tablename(service_id)
        if not Queue.connection:
            Queue.connection = ibis.postgres.connect(
                url='postgresql://python:python@localhost:5432/postgres'
            )

        sc = ibis.schema([
            ('doc_id', 'string'),
            ('date', 'date'),
            ('value', 'bytes'),
            ('row_id', 'string')
        ])

        try:
            self.table = self.connection.table(self.service_id)

        except:
            Queue.connection.create_table(self.service_id, schema=sc)
            self.table = self.connection.table(self.service_id)


    def id2tablename(self, id):
        return f"queue_{id}".lower()

    def timeout(self, f, timeout=None):
        # Database polling until value appeared or not
        result = None
        while not result:
            try:
                result = f()
            except Exception as e:
                time.sleep(1)

                continue

        #print (f"got {result}")
        return result

    def get(self, id, timeout=None):
        if timeout:
            return self.timeout(lambda : self.get(id), timeout=timeout)

        item = self.table.filter(self.table["doc_id"] == id).sort_by("date").limit(10).execute()
        self.row_id = item.iloc[0].row_id
        return decompress_pickle(item.iloc[0]['value'])

    def print(self):
        for table in self.connection.list_tables():
            self.print_table(table)
    def print_table(self, table=None):
        print(f"TABLE {self.service_id}")
        print(self.connection.table(self.service_id if not table else table).limit(10000).execute())

    def task_done(self, id=None):
        self.connection.con.execute(f"DELETE from {self.service_id} where row_id = '{self.row_id if not id else id}'")

    def queue_done(self, id=None):
        self.connection.con.execute(f"DELETE from {self.service_id} where doc_id = '{id}'")


    def put(self, id, item, timeout=None):
        df_item = pandas.DataFrame([
            (id, datetime.datetime.now(), compressed_pickle(item), uuid.uuid4().hex)],
            columns=['doc_id', 'date', 'value', 'row_id']
        )
        self.connection.insert(self.service_id, df_item)



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


    Thread(target=q.get, args=("None",), kwargs={"timeout":30}).start()
    Thread(target=q.put, args=("None", ("bla", {"k": "v"}))).start()

    time.sleep(2)
    q.task_done()
    q.task_done()
    q.queue_done("1")
    q.queue_done("2")

    q.print()

