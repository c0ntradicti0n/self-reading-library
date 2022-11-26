import traceback
from collections import defaultdict
import json
import logging
from queue import Empty

import numpy
from PIL import Image

from core.database import Queue, RatingQueue
from helpers import hash_tools
from helpers.encode import jsonify
from helpers.json_tools import np_encoder

logging.getLogger().setLevel(logging.INFO)
import os
import sys
import logging

sys.path.append("../")
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import config
import base64
import io
from jsonpath_ng import parse
from pprint import pprint
import falcon
import threading

q = {}
d = {}


def init_queues(service_id, id=None, rated_queue=False):
    global q
    global d
    # samples to take from
    if rated_queue:
        Q = RatingQueue
    else:
        Q = Queue
    q[service_id] = Q(service_id + "_q")
    # samples edited by user
    d[service_id] = Q(service_id + "_d")
    # session dependent queue
    if id:
        q[id] = Q(id + "_id")


def encode_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=75)
    byte_object = buffer.getbuffer()
    return byte_object


def round_double_list(bbox):
    return [[round(c, 2) for c in box] for box in bbox]


funs = defaultdict(
    lambda x: x,
    {
        "layout_predictions": lambda x: None,
        "df": lambda x: None,
        "human_image": lambda x: base64.b64encode(encode_base64(x)).decode("utf-8"),
        "image": lambda x: base64.b64encode(encode_base64(x)).decode("utf-8"),
        "bbox": lambda x: round_double_list(x),
    },
)


def encode_some(k, v):
    if isinstance(v, dict) and isinstance(list(v.keys())[0], tuple):
        v = list(v.values())[0]
    if isinstance(v, numpy.ndarray):
        v = list(v)
    return funs[k]((v)) if k in funs else v


def encode(obj_meta):
    obj, meta = obj_meta
    if "human_image_path" in meta and not "human_image" in meta:
        if isinstance(meta["human_image_path"], numpy.ndarray):
            meta["human_image_path"] = meta["human_image_path"][0]
        meta["human_image"] = Image.open(meta["human_image_path"])
    if "image_path" in meta and not "image" in meta:
        if isinstance(meta["image_path"], numpy.ndarray):
            meta["image_path"] = meta["image_path"][0]
        meta["image"] = Image.open(meta["image_path"])
    if isinstance(meta, dict):
        meta = {k: encode_some(k, v) for k, v in meta.items()}
    return obj, meta


all_rest_queues = []


def path_or_url_encoded(path_url):
    is_url = path_url.startswith("http")
    url = path_url if is_url else None
    doc_id = (
        f"{config.hidden_folder}pdfs/{hash_tools.hashval(path_url)}.pdf"
        if is_url
        else path_url
    )
    return doc_id, url


class RestQueue:
    def __init__(
        self,
        service_id,
        update_data=lambda x: x,
        work_on_upload=None,
        rated_queue=False,
    ):
        global all_rest_queues
        all_rest_queues.append(self)
        self.service_id = service_id
        init_queues(service_id, rated_queue=rated_queue)
        self.update_data = update_data
        self.work_on_upload = work_on_upload

    workbook = {}

    def get(self, id, get_other=True):

        data = q[self.service_id].get(id)

        if not data and get_other:
            logging.info(f"No file prepared for {id}, getting default")

            data = q[self.service_id].get(self.service_id)

            if data:
                q[self.service_id].task_done()
                q[self.service_id].put(id, data)

        return data

    def change(self, id, item, path, value):
        self.apply(item, path, value)
        values = self.update_data(item)
        q[self.service_id].update(id, item)
        return values

    def apply(self, item, path, value):
        jsonpath_expr = parse(path)
        jsonpath_expr.find(item)
        jsonpath_expr.update(item, value)

    def ok(self, id):
        logging.info(f"Ok {id}")
        item = q[id if id in q else self.service_id].get(id)
        d[self.service_id].put(id, item)
        q[id if id in q else self.service_id].task_done()

    def discard(self, id):
        try:
            print("Discarding")
            q[self.service_id].rate(id, score=-1)
            self.ok(id)
        except Exception as e:
            raise e

    def on_get(self, req, resp, id=None):
        # get value from before
        path_url = req.get_param("id", default=None)
        data = self.get(id, get_other=not path_url)

        if not data and path_url:
            doc_id, url = path_or_url_encoded(path_url)

            logging.info(f"Annotate new document {doc_id=} {id=} {url=}")
            init_queues(self.service_id, id)
            data = self.work_on_upload(doc_id, service_id=id, url=url)
            q[self.service_id].put(id, data)

        if not data:
            logging.info("Returning No Content")
            resp.status = falcon.HTTP_204
            return

        data = encode(data)
        resp.text = jsonify(data)
        resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, id=None):  # edit, update image
        result = req.media
        path, value = result
        item = self.get(id)
        if path:
            if isinstance(path, str):
                item = self.change(id, item, path, value)
            elif isinstance(path, list):
                for p in path:
                    item = self.change(id, item, p, value)
            else:
                logging.error(f"'{path}' has no compatible type")
                resp.text = json.dumps(
                    encode(item), ensure_ascii=False, default=np_encoder
                )
                resp.status = falcon.HTTP_400
        resp.text = json.dumps(encode(item), ensure_ascii=False, default=np_encoder)
        resp.status = falcon.HTTP_OK

    def on_patch(self, req, resp, id=None):
        pprint(req)

        file_part = req.get_param("file")

        # Read image as binary

        if not file_part.file:
            resp.media = {"status": "missing file"}
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

            t = threading.Thread(
                target=self.work_on_upload, args=(path,), name="fill on upload"
            )
            t.start()

        logging.info(f"Started task {self.work_on_upload} after upload")

        resp.media = {"status": "ok"}
        resp.status = falcon.HTTP_OK

    # ok or use one existing file
    def on_post(self, req, resp, id=None, *args, **kwargs):
        if isinstance(req.media, str):
            doc_id = req.media
            doc_id, url = path_or_url_encoded(doc_id)

            logging.info(f"Annotate new document {doc_id=} {id=} {url=}")
            init_queues(self.service_id, id)
            self.work_on_upload(doc_id, service_id=id, url=url)
        else:
            logging.info(f"Add annotation to collection {id=}")

            self.ok(id)

        item = self.get(id)
        if item:
            resp.text = jsonify(encode(item))
            resp.status = falcon.HTTP_OK
        else:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({})

    def on_delete(self, req, resp, id=None):
        self.discard(id)


def queue_put(service_id, gen):
    global q

    for val in gen:
        q[service_id].put(service_id, val)


def queue_iter(service_id, gen, single=False):
    global q, d

    for i in range(5):
        if len(q[service_id]) < 5:

            try:
                new_val = next(gen)
                q[service_id].put(service_id, new_val)

            except Exception as e:
                if not single:
                    raise e
                else:
                    break
        else:
            logging.info("Not adding new samples, enough in queue")

    logging.info(f"Inserted samples in the queue {service_id}")

    while True:
        # polling the q... TODO: make q blocking again
        try:
            r = d[service_id].get(None, timeout=30)
        except Exception as e:
            r = None
            logging.info("Pulse", exc_info=True)

        if r:
            logging.debug("Yielding")
            yield r
            logging.debug("Yielded")

            if r:
                try:

                    d[service_id].task_done()
                    logging.info("Task done")

                except Exception as e:
                    logging.debug("Was the task already done?", exc_info=True)

            for i in range(3):
                if len(q[service_id]) < 5:
                    logging.debug("Inserting some new sample in the queue")
                    try:
                        new_val = next(gen)
                        q[service_id].put(service_id, new_val)

                    except Exception as e:
                        traceback.print_exc()
                        # or
                        print(sys.exc_info()[2])
                        logging.error(e, exc_info=True)
                else:
                    logging.info("Not adding new samples, enough in queue")

    print("ende")


if __name__ == "__main__":

    def fibonacciGenerator(min, max=1000):
        a = 0
        b = 1
        for i in range(max):
            if i >= min:
                yield b
            a, b = b, a + b

    def worker():
        logging.info("yielding")

        fib1 = fibonacciGenerator(0, 3)
        fib2 = fibonacciGenerator(10, 13)

        for fib in [fib1, fib2]:

            try:

                for e in queue_iter("test", fib):
                    print(f"yielded {e}")
            except RuntimeError as e:
                print("end...")

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
