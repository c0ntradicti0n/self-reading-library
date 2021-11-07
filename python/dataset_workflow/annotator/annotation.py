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
from helpers.event_binding import queue_iter
import itertools

def close_pil_image():
    # hide image
    for proc in psutil.process_iter():
        if proc.name() == "display":
            proc.kill()

@converter("prediction", "annotation")
class Annotator(RestPublisher, react):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="Annotator",
            type="annotation",
            path="annotation",
            route="annotation",
            access={"fetch": True, "read": True, "upload": True, "correct": True, "delete": True}))


    q = queue.Queue()
    in_workshop = {}

    def on_get(self, req):
        self.item = Annotator.q.get()
        print(f'Working on {item}')
        self.in_workshop[req.ip] = item
        return item

    def on_post(self, req):
        print(f'Worked on {item}')

        Annotator.q.task_done()

    def on_put(self, req):
        print(f'Working on {item}')
        diff = JSON.parse(req.data)
        self.apply(self.item, diff)

    def apply(self, item, diff):
        jsonpath_expr = parse(diff["path"])
        jsonpath_expr.find(item)[0].value['test'] = diff["value"]



    def __call__(self, prediction_metas, *args, **kwargs):
        yield from queue_iter((p_m for p_m in itertools.islice(prediction_metas, 3)))

        """
        
            while True:

                prediction['human_image'].show()
                pprint(
                    dict(
                        zip(
                            list(
                                enumerate(
                                    prediction['labels']
                                )
                            ),
                            prediction['bbox']
                        )
                    )
                )

                yn = input("Is this prediction correct?")

                close_pil_image()

                if yn.startswith("y"):
                    yield prediction, meta
                    break
                else:
                    if yn.startswith("n"):
                        break
                    else:
                        continue
            """

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
