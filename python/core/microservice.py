import importlib
import inspect
import json
import logging
import os
import sys

import addict as addict
import requests
import ruamel.yaml

from helpers.list_tools import metaize


class microservice:
    def __init__(self, converter, *args, **kwargs):
        name = converter.__class__.__name__
        self.service_name = "micro_" + name.lower()
        self.converter = converter

        f = converter.predict
        def p(*args, **kwargs):
            return f(*args, **kwargs)
        self.p = p
        self.converter.predict= self.remote_call

        if not os.environ.get("INSIDE", False):
            self.converter = converter
            self.imports = inspect.getmembers(sys.modules[__name__], inspect.isclass)
            try:
                with open("../docker-compose.override.yaml") as f:
                    compose = f.read()
            except FileNotFoundError:
                compose = ""

            compose = addict.addict.Dict(ruamel.yaml.load(compose))
            full_path = converter.__class__.__module__
            full_path = full_path.replace("python.", "")
            compose.update(
                {
                    "services": {
                        self.service_name: {
                            "container_name": self.service_name,
                            "image": "full_python",
                            "build": "python",
                            "ports": ["7777:7777"],
                            "entrypoint": f"uwsgi  --py-autoreload=1 --http 0.0.0.0:7777 --module {full_path}:application   --memory-report --enable-threads -b 32768  --gevent 40 --gevent-monkey-patch",
                            "environment": {"INSIDE": "true",
                                            "LC_ALL": "en_US.UTF-8",
                                            "LANG": "en_US.UTF - 8",
                                            "LANGUAGE": "en_US.UTF-8"
                                            },
                            "volumes": [
                                "$CWD/python:/home/finn/Programming/self-reading-library/python"
                            ],
                        }
                    }
                }
            )
            compose = compose.to_dict()
            with open("../docker-compose.override.yaml", "w") as f:
                ruamel.yaml.dump(compose, f)



        else:
            self.app = {self.service_name: self}
            import falcon

            application = falcon.App()
            application.add_route("/" + self.service_name, self)
            print ("Service at /" +  self.service_name)

            importlib.import_module(self.converter.__module__).application = application

            converter.load()

    def remote_call(self,  *args, **kwargs):
        send_data = json.dumps((args, kwargs))
        resp = requests.post(
            "http://localhost:7777/" + self.service_name, send_data
        )
        if not resp.status_code == 200:
            logging.error(f"Error on microservice request {resp.text}")
        else:
            return json.loads(resp.text)

    def on_post(self, req, resp):
        try:
            print(req.media)
            args, kwargs = req.media

            res = self.p(*args, **kwargs)
            print(res)
            resp.text = json.dumps(res)
            resp.status = "200"
            print(resp)
        except Exception as e:
            print (e)
            logging.error("Could not calculate result", exc_info=True)
            resp.status = "500"
            resp.text = str(e)
        resp.status = "200"

    def __call__(self, *args, **kwargs):
        return self.converter(*args, **kwargs)

