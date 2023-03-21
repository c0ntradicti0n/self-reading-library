import importlib
import inspect
import json
import logging
import os
import sys
from pprint import pprint

import addict as addict
import ruamel.yaml

from config import config
from helpers.json_tools import json_file_update
from helpers.best_model_tools import find_best_model
from helpers.time_tools import wait_for_change


class trigger_on:
    def __init__(self, converter, *args, **kwargs):
        name = converter.__class__.__name__
        logging.warning(f"REGISTERING TRIGGER {name}")
        self.service_name = "trigger_" + name.lower()
        self.converter = converter

        docker_kwargs = (
            {} if not hasattr(converter, "docker_kwargs") else converter.docker_kwargs
        )

        if not os.environ.get("INSIDE", False):
            self.converter = converter
            self.imports = inspect.getmembers(sys.modules[__name__], inspect.isclass)
            try:
                with open("../docker-compose.override.yaml") as f:
                    compose = f.read()
            except Exception:
                compose = ""

            compose = addict.addict.Dict(ruamel.yaml.load(compose))
            full_path = converter.__class__.__module__
            full_path = full_path.replace("python.", "")
            service_def = {
                "container_name": self.service_name,
                "image": "full_python",
                "logging": {
                    "driver": "json-file",
                    "options": {"max-file": "5", "max-size": "10m"},
                },
                "build": "python",
                "restart": "unless-stopped",
                "entrypoint": f"python3 -c 'from {full_path} import {name};  {name}.wait_for_change()'",
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
                    "$CWD/python:/home/finn/Programming/self-reading-library/python"
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

    def wait_for_change(self):
        wait_for_change(self.converter.on, self.prepare_and_train)

    mutext_affix = ""

    def prepare_and_train(self):
        global BEST_MODELS
        if not os.path.isdir(self.converter.model_dir):
            os.makedirs(self.converter.model_dir)
        if not os.path.isdir(self.converter.on):
            os.makedirs(self.converter.on)

        loops = []

        samples_files = os.listdir(self.converter.on)

        if self.converter.training_rate_mode == "ls":
            n_samples = len(samples_files)
        elif self.converter.training_rate_mode == "size":
            n_samples = os.path.getsize(self.converter.training_rate_file)
        else:
            raise AttributeError("Model needs to have 'training_rate_mode' attribute")

        best_model_path, scores = find_best_model(self.converter.model_dir)
        full_model_path = best_model_path

        if scores:
            training_rate = n_samples / int(scores.groups()[0])
        else:
            training_rate = 1

        loops.append(training_rate)

        if loops.count(training_rate) > 2:
            logging.info("Training did not change, staying prediction loop")

        args = {
            "best_model_path": best_model_path,
            "training_rate": training_rate,
            "layout_model_path": config.layout_model_path,
        }

        BEST_MODELS[self.converter.service_id] = args
        BEST_MODELS = json_file_update(config.BEST_MODELS_PATH, update=BEST_MODELS)

        logging.info(f"Having {training_rate = }")

        mutext_path = config.hidden_folder + self.mutext_affix
        if (
            training_rate > 1.1
            or not full_model_path
            and not os.path.exists(mutext_path)
        ):
            os.system(f"touch {mutext_path}")
            try:
                model_meta = self.converter.on_train(samples_files, len(samples_files))
                pprint(model_meta)
            finally:
                os.system(f"rm {mutext_path}")

    def __call__(self, *args, **kwargs):
        return self.converter(*args, **kwargs)
