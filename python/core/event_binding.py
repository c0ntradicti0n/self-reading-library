import random
import threading
import traceback
from queue import Queue, Empty
import json
from traceback_with_variables import Format, ColorSchemes, is_ipython_global, activate_by_import
import logging

from helpers.list_tools import metaize

logging.getLogger().setLevel(logging.INFO)
import os
import sys
import logging
sys.path.append("../")
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core import config
import base64
import io
from jsonpath_ng import jsonpath, parse
from pprint import pprint
import falcon
import threading


q = {}
d = {}


def init_queues(service_id):
    global q
    global d
    q[service_id] = Queue()
    d[service_id] = Queue()


def encode_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=75)
    byte_object = buffer.getbuffer()
    return byte_object


def encode_df(df):
    return None # df.to_dict()


def round_double_list(bbox):
    return [[round(c, 2 )for c in box] for box in bbox]


funs = {"image": lambda x: base64.b64encode(encode_base64(x)).decode('utf-8'),
        "df": encode_df,
        "bbox": round_double_list}


def encode_some(k, v):
    for s, f in funs.items():
        if s in k:
            return f(v)
    else:
        return v

def encode(obj_meta):
    obj, meta = obj_meta
    obj = {k: encode_some(k, v)
           for k,v in obj.items()}
    return (obj, meta)


all_rest_queues = []

class RestQueue:
    def __init__(
            self,
            service_id,
            update_data = lambda x: x,
            work_on_upload = None
    ):
        global all_rest_queues
        all_rest_queues.append(self)
        self.service_id = service_id
        init_queues(service_id)
        self.update_data = update_data
        self.work_on_upload = work_on_upload

    workbook = {}

    def get(self, id):
        print("get")

        if not id in self.workbook or not self.workbook[id]:
            print ("get new")
            try:

                self.workbook[id] = q[self.service_id].get(timeout=3)
            except Exception as e:
                #print (f"{self.workbook=}")
                logging.error("queue not ready")

        if id in self.workbook:
            print ("get old")

            return self.workbook[id]
        else:
            return None

    def change(self, item, path, value):
        self.apply(item, path, value)
        item = self.update_data(item)
        self.workbook[id] = item
        return item

    def apply(self, item, path, value):
        jsonpath_expr = parse(path)
        jsonpath_expr.find(item)
        jsonpath_expr.update(item, value)


    def ok(self, id):
        try:
            print ("ok")
            self.workbook.get(id)
            item = self.workbook.pop(id)
            d[self.service_id].put_nowait(item)
            q[self.service_id].task_done()
        except Exception as e:
            print ("ok, but end of gen")

            logging.error(f"could not remove ${id} from {self.workbook}")
            d[self.service_id].put_nowait(None)

    def discard(self, id):
        try:
            print ("discarding")

            item = self.workbook.pop(id)
            q[self.service_id].task_done()
        except Exception as e:
            print ("discarding error")

            logging.error(f"could not remove ${id} from {self.workbook}")

    def delete(self, id):
        self.workbook.pop(id)

    def get_specific(self, id):
        self.work_on_upload(id)


    def on_get(self, req, resp, id=None): # get image
        pprint(req)

        data = self.get(id)
        if not data:
            resp.status = falcon.HTTP_300
            return
        data = encode(data)
        resp.body = json.dumps(data, ensure_ascii=False)
        resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, id = None):  # edit, update image
        pprint(req)

        result = req.media
        path, value = result
        item = self.workbook[id]

        item = self.change(item, path, value)

        item = encode(item)
        resp.body = json.dumps(item, ensure_ascii=False)
        resp.status = falcon.HTTP_OK

    def on_patch(self, req, resp, id = None):
        pprint(req)

        form = req.get_media()

        file_part = req.get_param('file')
        #pprint(file_part)

        # Read image as binary

        if not file_part.file:
            resp.media = {'status': 'missing file'}
            resp.status = falcon.HTTP_400


        raw = file_part.file.read()
        file_part.file.close()

        # Retrieve filename
        filename = file_part.filename

        path = config.PDF_UPLOAD_DIR + filename
        with open(path, "wb") as f:
            f.write(raw)

        logging.info(f"Uploaded {filename=} to {config.PDF_UPLOAD_DIR} ")

        if self.work_on_upload:
            logging.info(f"starting thread! for {self.work_on_upload}")

            t = threading.Thread(target=self.work_on_upload, args=(path,), name="fill on upload")
            t.start()

        logging.info(f"Started task {self.work_on_upload} after upload")

        resp.media = {'status': 'ok'}
        resp.status = falcon.HTTP_OK

    # ok or use one existing file
    def on_post(self, req, resp, id=None):
        print(req, resp)

        if (req.media):
            # fetching one document for annotation
            path = req.media
            item = self.work_on_upload(path, req.params['id'])
            self.workbook[id] = item
            resp.body = json.dumps(item, ensure_ascii=False)
            resp.status = falcon.HTTP_OK
        elif req.params:
            item =  self.work_on_upload(req.params['id'])
            self.workbook[id] = item
            resp.body = json.dumps(item, ensure_ascii=False)
            resp.status = falcon.HTTP_OK
        else:
            # annotation positive
            self.ok(id)

    def on_delete(self, req, resp, id=None):
        print(req, resp)
        self.discard(id)


def queue_iter (service_id, gen):

    global q, d

    for i in range(5):
        try:
            new_val = next(gen)
            q[service_id].put_nowait(new_val)

        except Exception as e:
            traceback.print_exc()
            # or
            print(sys.exc_info()[2])
            logging.error(e, exc_info=True)
            raise e

    logging.info("Inserted first some samples in the queue")


    while True:

        try:
            logging.debug("Getting iterator")
            r = d[service_id].get(timeout=3)
            logging.info("Got iterator item")

            if r:
                d[service_id].task_done()
            logging.info("Task done")

        except Empty:
            r = None
            logging.debug("Pulse")

        if r:
            logging.debug("Yielding")

            yield r
            logging.debug("Yielded")

            for i in range(3):
                logging.debug("Inserting some new sample in the queue")
                try:
                    new_val = next(gen)
                    q[service_id].put_nowait(new_val)

                except Exception as e:
                    traceback.print_exc()
                    # or
                    print(sys.exc_info()[2])
                    logging.error(e, exc_info=True)

    print("ende")


if __name__ == "__main__":
    def fibonacciGenerator(min, max = 1000):
        a = 0
        b = 1
        for i in range (max):
            if i >= min:
                yield b
            a, b = b, a + b




    def worker():
        logging.info("yielding")

        fib1 = fibonacciGenerator(0, 3)
        fib2 = fibonacciGenerator(10, 13)

        for fib in [fib1, fib2]:

            try:

                for e in queue_iter("test",fib):
                    print (f"yielded {e}")
            except RuntimeError as e:
                print ("end...")


    t = threading.Thread(target=worker, name="test")
    t.start()

    rq = RestQueue(service_id="test")

    id = 123
    i = rq.get(id)
    rq.ok(id)
    i = rq.get(id)
    rq.ok(id)

    i = rq.get(id)
    rq.ok(id)


    i = rq.get(id)
    rq.ok(id)
    i = rq.get(id)
    rq.ok(id)

    i = rq.get(id)
    rq.ok(id)

    i = rq.get(id)
    rq.ok(id)
    i = rq.get(id)
    rq.ok(id)

    i = rq.get(id)
    rq.ok(id)







