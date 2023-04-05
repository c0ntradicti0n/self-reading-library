import importlib
import inspect
import json
import logging
import os
import sys

import addict as addict
import falcon
import requests
import ruamel.yaml


class microservice:
    def __init__(self, converter, *args, **kwargs):
        name = converter.__class__.__name__
        self.service_name = "micro_" + name.lower()
        self.converter = converter

        docker_kwargs = (
            {} if not hasattr(converter, "docker_kwargs") else converter.docker_kwargs
        )

        g = converter.predict

        def p(*args, **kwargs):
            return g(*args, **kwargs)

        self.p = p
        self.converter.predict = self.remote_call

        if not os.environ.get("INSIDE", False) and not (
            os.environ.get("INSIDE", False) == "no_update"
        ):
            self.converter = converter
            self.imports = inspect.getmembers(sys.modules[__name__], inspect.isclass)
            try:
                with open("../docker-compose.override.yaml") as f:
                    compose = f.read()
            except Exception:
                compose = ""

            compose = addict.addict.Dict(ruamel.yaml.safe_load(compose))
            full_path = converter.__class__.__module__
            full_path = full_path.replace("python.", "")
            service_def = {
                "container_name": self.service_name,
                "logging": {
                    "driver": "json-file",
                    "options": {"max-file": "5", "max-size": "10m"},
                },
                "image": "full_python",
                **(
                    {
                        "build": {
                            "context": "python",
                            "dockerfile": "$CWD" + converter.Dockerfile.replace(
                                    os.getcwd(), ""
                                ) + "/Dockerfile",
                            "args": {
                                "CONTEXT": full_path.replace(".", "/"),
                                "OUTSIDE_CONTEXT": converter.Dockerfile.replace(
                                    os.getcwd(), ""
                                ),
                            },
                        }
                    }
                    if hasattr(converter, "Dockerfile")
                    else {
                        "build": "python",
                    }
                ),
                "restart": "unless-stopped",
                "entrypoint": f"python3 -c 'from {full_path} import {name}; from wsgiref import simple_server; simple_server.make_server(\"0.0.0.0\", 7777, {name}.application).serve_forever()'",
                "environment": {
                    "INSIDE": "true",
                    "LC_ALL": "en_US.UTF-8",
                    "LANG": "en_US.UTF - 8",
                    "LANGUAGE": "en_US.UTF-8",
                    "GDB_PASSWORD": "${GDB_PASSWORD}",
                    "GDB_HOST": "gdb",
                },
                "networks": ["db"],
                "volumes": [
                    "$CWD/python:/home/finn/Programming/self-reading-library/python",
                    *(
                        [
                            "$CWD/python"
                            + converter.Dockerfile.replace(os.getcwd(), "")
                            + "/"
                            + v
                            + ":/volumes/"
                            + v.replace("../", "")
                            for v in converter.volumes
                        ]
                        if hasattr(converter, "volumes")
                        else []
                    ),
                ],
                **docker_kwargs,
            }
            compose.update({"services": {self.service_name: service_def}})
            compose = compose.to_dict()
            try:
                with open("../docker-compose.override.yaml", "w") as f:
                    ruamel.yaml.dump(compose, f)
            except Exception as e:
                logging.error("Could not update docker-compose.override!")

        else:
            self.app = {self.service_name: self}
            import falcon
            from falcon_cors import CORS

            cors = CORS(
                allow_origins_list=["*"],
                allow_all_origins=True,
                allow_all_headers=True,
                allow_credentials_all_origins=True,
                allow_all_methods=falcon.HTTP_METHODS,
            )

            from falcon_multipart.middleware import MultipartMiddleware

            application = falcon.App(
                middleware=[cors.middleware, MultipartMiddleware()]
            )
            application.add_route("/" + self.service_name, self)
            logging.debug("Service at /" + self.service_name)

            importlib.import_module(self.converter.__module__).application = application
            converter.application = application
            self.application = application

            converter.load()

    def remote_call(self, *args, **kwargs):

        send_data = json.dumps((args, kwargs))

        if os.environ.get("INSIDE", False) == False:
            return self.p(*args, **kwargs)

        resp = requests.post(
            f"http://{self.service_name}:7777/{self.service_name}",
            send_data,
            headers={"origin": "localhost", "content-Type": "application/json"},
        )
        if not resp.status_code == 200:
            logging.error(
                f"Error on microservice request {self.service_name} {resp.text}"
            )
        else:
            return json.loads(resp.text)

    def on_post(self, req, resp):
        try:
            args, kwargs = req.media
            res = self.p(*args, **kwargs)
            resp.text = json.dumps(res)
            resp.status = falcon.HTTP_200
        except Exception as e:
            print(e)
            logging.error("Could not calculate result", exc_info=True)
            resp.status = falcon.HTTP_500
            resp.text = str(e)

    def __call__(self, *args, **kwargs):
        return self.converter(*args, **kwargs)
