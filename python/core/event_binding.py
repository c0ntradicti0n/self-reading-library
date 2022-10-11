import traceback
from collections import defaultdict
import json
import logging

import numpy
from PIL import Image

from core.database import Queue, RatingQueue
from helpers import hash_tools
from helpers.encode import jsonify

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
    return (obj, meta)


all_rest_queues = []


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

    def get(self, id):

        try:
            self.workbook[id] = q[id if id else self.service_id].get(
                id if id else self.service_id, timeout=10
            )
            logging.info("Get new")

        except Exception as e:
            logging.error("Queue not ready, give old thing", exc_info=True)
            if id in self.workbook:
                return self.workbook[id]
            else:
                return None

    def change(self, item, path, value):
        self.apply(item, path, value)
        values = self.update_data(item)
        return values

    def apply(self, item, path, value):
        jsonpath_expr = parse(path)
        jsonpath_expr.find(item)
        jsonpath_expr.update(item, value)

    def ok(self, id):
        try:
            logging.info(f"Ok {id}")
            self.workbook.get(id)
            item = self.workbook.pop(id)
            d[self.service_id].put(id, item)
            q[id if id else self.service_id].task_done()
        except Exception as e:
            print("Ok, but end of gen")

            logging.error(f"Could not remove ${id} from {self.workbook}")

    def discard(self, id):
        try:
            print("Discarding")

            item = self.workbook.pop(id)
            q[self.service_id].task_done()
        except Exception as e:
            print("Discarding error")

            logging.error(f"ould not remove ${id} from {self.workbook}")

    def on_get(self, req, resp, id=None):  # get image
        data = self.workbook.get(id)
        if not data:
            logging.info(f"No file prepared for {id}, getting default")
            data = self.get(self.service_id)

        if not data:
            resp.status = falcon.HTTP_300
            return
        data = encode(data)
        resp.text = jsonify(data)
        resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, id=None):  # edit, update image
        pprint(req)

        result = req.media
        path, value = result
        item = self.workbook[id]

        item = self.change(item, path, value)
        resp.text = json.dumps(encode(item), ensure_ascii=False)
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
            is_url = doc_id.startswith("http")
            url = doc_id if is_url else None
            doc_id = (
                f"{config.hidden_folder}pdfs/{hash_tools.hashval(doc_id)}.pdf"
                if is_url
                else doc_id
            )

            logging.info(f"Annotate new document {doc_id=} {id=} {url=}")
            init_queues(self.service_id, id)
            self.work_on_upload(doc_id, service_id=id, url=url)
        else:
            logging.info(f"Add annotation to collection {id=}")

            self.ok(id)

        self.get(id)
        if self.workbook.get(id):
            resp.text = jsonify(encode(self.workbook[id]))
            resp.status = falcon.HTTP_OK
        else:
            resp.status = falcon.HTTP_OK
            resp.text = json.dumps({})

    def on_delete(self, req, resp, id=None):
        print(req, resp)
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
        try:
            r = d[service_id].get(None, timeout=3)
            print(".", end="")

        except Exception as e:
            r = None
            logging.debug("Pulse", exc_info=True)

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
