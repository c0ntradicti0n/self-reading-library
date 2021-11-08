import unittest
from python.layouteagle.pathant.Converter import converter
from layouteagle.RestPublisher.RestPublisher import RestPublisher
from layouteagle.RestPublisher.RestPublisher import Resource
from layouteagle.RestPublisher.react import react
import uuid
from itertools import islice
import types
import psutil
from pprint import pprint
import threading, queue
from helpers.event_binding import queue_iter, RestQueue
import itertools

def close_pil_image():
    # hide image
    for proc in psutil.process_iter():
        if proc.name() == "display":
            proc.kill()



AnnotationRest = RestQueue(update_data=repaint_image_from_labels)



@converter("prediction", "annotation")
class Annotator(RestPublisher, react):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="Annotation",
            type="annotation",
            path="annotation",
            route="annotation",
            access={"add_id": True, "fetch": True, "read": True, "upload": True, "correct": True, "delete": True}))


    in_workshop = {}


    def __call__(self, prediction_metas, *args, **kwargs):
        yield from queue_iter((p_m for p_m in itertools.islice(prediction_metas, 3)))


class TestAnnotator(unittest.TestCase):
    def test_generator(self):
        a = Annotator
        incoming_gen = ((str(i), {}) for _ in range(10))

        gen = a.store_few(incoming_gen)
        # next(gen)

        h, q = gen.send(("ask", None))

        l = []

        for x in gen:
            l.append(x)

        h, q = gen.send(("ask", None))

        l = []

        for x in gen:
            l.append(x)
