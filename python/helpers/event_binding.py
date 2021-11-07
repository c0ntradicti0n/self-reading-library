import random
import threading
from queue import Queue
import json
from traceback_with_variables import Format, ColorSchemes, is_ipython_global, activate_by_import
import logging
logging.getLogger().setLevel(logging.INFO)
import os
import sys
import logging
sys.path.append("../")
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from layouteagle import config
import base64
import io

fmt = Format(
    before=5,
    after=3,
    max_value_str_len=-1,
    max_exc_str_len=-1,
    ellipsis_='...',
    color_scheme=ColorSchemes.synthwave
)

q = Queue()
d = Queue()
w = Queue()
def encode_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=75)
    byte_object = buffer.getbuffer()
    return byte_object

def encode(obj_meta):
    obj, meta = obj_meta
    obj = {k: base64.b64encode(encode_base64(v)).decode('utf-8')
    if "image" in k else k for k,v in obj.items()}

    return (obj, meta)


class AnnotationRest ():
    workbook = {}

    def get(self, id):
        self.workbook[id] = q.get()

        return self.workbook[id]

    def change(self, id, e):
        self.workbook[id] = e

    def ok(self, id):
        item = self.workbook.pop(id)
        d.put(item)

    def discard(self, id):
        item = self.workbook.pop(id)
        q.put(item)

    def delete(self, id):
        self.workbook.pop(id)

    def on_get(self, req, resp, id=None): # get image
        print(req, resp)

        image = self.get(id)

        pprint(q.queue)

        image = encode(image)

        pprint(image)


        resp.body = json.dumps(image, ensure_ascii=False)


    def on_put(self, req, resp, id = None):  # edit, update image
        print(req, resp)
        self.change(id, ("whatever", i))
        return annotation

    def on_post(self, req, resp, id=None): # ok
        print(req, resp)
        self.ok(id)

def fibonacciGenerator():
    a=0
    b=1
    while(True):
        yield b
        a,b= b,a+b

obj = fibonacciGenerator()



def queue_iter (gen):
    while True:

        for i in range(1):
            q.put(next(gen))

        while True:
            k = next(gen)
            q.put(k)
            r = d.get()
            d.task_done()
            yield r


    print("ende")

if __name__ == "__main__":

    import subprocess
    import sys

    cmd_parts = ["gunicorn", "event_binding:api", "-b", "127.0.0.1:7789",
                 "-t", "90000"]
    print(" ".join(cmd_parts))
    # start the resource server with gunicorn, that it can recompile, when changed
    subprocess.check_call(cmd_parts,
                          stdout=sys.stdout, stderr=subprocess.STDOUT)


else:
    import falcon
    from pprint import pprint
    def get_all_routes(api):
        routes_list = []

        def get_children(node):
            if len(node.children):
                for child_node in node.children:
                    get_children(child_node)
            else:
                routes_list.append((node.uri_template, node.resource))

        [get_children(node) for node in api._router._roots]
        return routes_list



    publishing = {
        '/annotator/{id}': AnnotationRest()
    }

    from falcon_cors import CORS

    cors = CORS(
        allow_all_origins=True,
        allow_all_headers=True,
        allow_all_methods=True,
    )

    api = falcon.API(middleware=[cors.middleware])

    for route, module in publishing.items():
        api.add_route(route, module)

    pprint(get_all_routes(api))

    def worker():
        logging.info("yielding")


        for e in iter(obj):
            print (f"yielded {e}")


    #t = threading.Thread(target=worker)
    #t.start()




