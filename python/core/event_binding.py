import gc
import multiprocessing
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
from helpers.hash_tools import hashval
from helpers.json_tools import np_encoder
from helpers.os_tools import touch
from helpers.time_tools import timeout

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


def init_queues(service_id, id=None):
    global q
    global d
    # samples to take from
    Q = RatingQueue

    q[service_id] = Q(service_id)
    # samples edited by user
    d[service_id] = Q(service_id)
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
    try:
        obj, meta = obj_meta
    except TypeError:
        return obj_meta
    if "human_image_path" in meta and not "human_image" in meta:
        if isinstance(meta["human_image_path"], (numpy.ndarray, list)):
            meta["human_image_path"] = meta["human_image_path"][0]
        meta["human_image"] = Image.open(meta["human_image_path"])
    if "image_path" in meta and not "image" in meta:
        if isinstance(meta["image_path"], (numpy.ndarray, list)):
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


def long_request(f):
    def _(self, req, resp, *args, **kwargs):
        hash = hashval(req.uri) + (hashval(req.media) if req.method != "GET" else "")
        path = config.REST_WORKING + "-" + hash + ".wip"
        if not os.path.exists(path):
            touch(path)

            @timeout(3)
            def finish():
                try:
                    res = f(self, req, resp, *args, **kwargs)
                finally:
                    os.remove(path)
                return res

            try:
                res = finish()
                return res
            except multiprocessing.context.TimeoutError:
                resp.status = falcon.HTTP_503
                resp.retry_after = "7"
        else:
            resp.status = falcon.HTTP_503
            resp.retry_after = "7"

    return _


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
        init_queues(service_id)
        self.update_data = update_data
        self.work_on_upload = work_on_upload

    workbook = {}

    def get(self, id, get_other=True):

        data = q[self.service_id].get(id)

        if not data and get_other:
            logging.info(f"No file prepared for {id}, getting default")

            data = q[self.service_id].get(None)

        try:
            data = data[0], dict(
                map(
                    lambda kv: (kv[0], list(kv[1]))
                    if isinstance(kv[1], numpy.ndarray)
                    else kv,
                    data[1].items(),
                )
            )
        except:
            pass
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

    def discard(self, id):
        try:
            logging.info(f"Discarding {id}")
            q[self.service_id].rate(id, score=-1)
            self.ok(id)
        except Exception as e:
            raise e

    @long_request
    def on_get(self, req, resp):
        # get value from before
        path_url = req.get_param("id", default=None)
        data = self.get(path_url, get_other=not path_url)

        if not data and path_url:
            doc_id, url = path_or_url_encoded(path_url)

            logging.info(f"Annotate new document {doc_id=} {url=}")
            init_queues(self.service_id, path_url)
            data = self.work_on_upload(doc_id, service_id=path_url, url=url)
            q[self.service_id].put(path_url, data)

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
        if "doc_id" in req.params:
            id = req.params["doc_id"]
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

    def on_post(self, req, resp, id=None, *args, **kwargs):

        if isinstance(req.media, str):
            doc_id = req.media
            doc_id, url = path_or_url_encoded(doc_id)

            logging.info(f"Annotate new document {doc_id=} {id=} {url=}")
            init_queues(self.service_id, id)
            self.work_on_upload(doc_id, service_id=id, url=url)
        else:
            logging.info(f"Ok for annotation {id=}")
            if "doc_id" in req.params:
                id = req.params["doc_id"]
            q[self.service_id].rate(id, score=10)

            self.ok(id)

        item = self.get(id)
        if item:
            resp.text = jsonify(encode(item))
            resp.status = falcon.HTTP_OK
        else:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({})

    def on_delete(self, req, resp, id=None):
        doc_id = req.media[0]
        self.discard(doc_id)


def queue_put(service_id, gen):
    global q

    for val in gen:
        q[service_id].put(service_id, val)


def queue_iter(service_id, gen, single=False):
    global q, d

    for i in range(5):
        if len(q[service_id]) < 8:
            try:
                gc.collect()
            except:
                logging.error("gc failed", exc_info=True)

            try:
                new_val = next(gen)
                if new_val:
                    q[service_id].put(service_id, new_val)
                else:
                    logging.error(f"Pipeline gave {new_val=}")

            except Exception as e:
                logging.error(
                    f"Error on putting new sample into queue {service_id=}",
                    exc_info=True,
                )
                raise

    logging.info(f"Inserted samples in the queue {service_id}")

    while True:
        # polling the q... TODO: make q blocking again
        try:
            result = d[service_id].get_ready(None, timeout=5)
        except Exception as e:
            raise

        if not result:
            continue

        logging.debug("Yielding")
        yield result
        logging.debug("Yielded")

        for i in range(1):
            if len(q[service_id]) < config.captcha_queue_size:
                logging.debug("Inserting some new sample in the queue")
                gc.collect()

                try:
                    new_val = next(gen)
                    if new_val:
                        q[service_id].put(service_id, new_val)
                    else:
                        logging.error(f"Pipeline gave {new_val=}")
                except Exception as e:
                    logging.error(e, exc_info=True)

    print("The End")


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
