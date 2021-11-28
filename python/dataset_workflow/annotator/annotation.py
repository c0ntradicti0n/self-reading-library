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
from dataset_workflow.model_helpers import repaint_image_from_labels
import logging



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
        for prediction_meta, meta in prediction_metas:
            try:
                for _p_m in queue_iter((p_m for p_m in prediction_meta)):
                    yield _p_m
            except RuntimeError as e:
                logging.info("annotating next document")


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
