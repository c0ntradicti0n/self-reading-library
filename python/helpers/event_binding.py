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
from jsonpath_ng import jsonpath, parse
from pprint import pprint
import falcon


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
    pprint(obj_meta)
    obj, meta = obj_meta
    obj = {k: encode_some(k, v)
           for k,v in obj.items()}
    return (obj, meta)


class RestQueue ():
    def __init__(self, update_data = lambda x: x):
        self.update_data = update_data

    workbook = {}

    def get(self, id):
        if not id in self.workbook or not self.workbook[id]:
            self.workbook[id] = q.get()

        return self.workbook[id]

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
            q.task_done()
            item = self.workbook.pop(id)
            d.put(item)
        except Exception as e:
            logging.error(f"could noit remove ${id} from {self.workbook}")
            d.put(None)

    def discard(self, id):
        item = self.workbook.pop(id)
        q.put(item)

    def delete(self, id):
        self.workbook.pop(id)

    def on_get(self, req, resp, id=None): # get image
        pprint((req, resp, self.workbook))
        data = self.get(id)
        pprint(q.queue)
        pprint(data)
        data = encode(data)
        pprint(data)

        resp.body = json.dumps(data, ensure_ascii=False)
        resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, id = None):  # edit, update image
        result = req.media
        path, value = result
        item = self.workbook[id]

        item = self.change(item, path, value)

        item = encode(item)
        resp.body = json.dumps(item, ensure_ascii=False)
        resp.status = falcon.HTTP_OK


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

            r = d.get()

            if r:
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
    pass
    """
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
    """




