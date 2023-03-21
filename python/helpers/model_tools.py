import os

import regex

from config import config
from core.event_binding import queue_iter
from helpers.best_model_tools import find_best_model
from helpers.json_tools import json_file_update


model_regex = r"(?P<shape>\d+)_(?P<f1>0,?\d*)_(?P<epoch>\d+)"
import logging
from pprint import pprint


TRAINING_RATE = {}

BEST_MODELS = config.BEST_MODELS


def model_in_the_loop(
    model_dir,
    collection_path,
    on_train,
    service_id,
    on_predict,
    training_rate_mode="ls",
    training_rate_file=None,
    trigger_service=None,
):
    global BEST_MODELS
    if not os.path.isdir(model_dir):
        os.makedirs(model_dir)
    if not os.path.isdir(collection_path):
        os.makedirs(collection_path)

    loops = []

    while True:

        TRAINING_RATE["service_id"] = service_id
        samples_files = os.listdir(
            config.GOLD_DATASET_PATH
            + "/"
            + (trigger_service if trigger_service else service_id)
            + "/"
        )

        if training_rate_mode == "ls":
            n_samples = len(samples_files)

        if training_rate_mode == "size":
            n_samples = os.path.getsize(training_rate_file)

        best_model_path, scores = find_best_model(model_dir)
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

        BEST_MODELS[service_id] = args
        BEST_MODELS = json_file_update(config.BEST_MODELS_PATH, update=BEST_MODELS)

        logging.info(f"Having {training_rate = }")
        if training_rate > 0.8 or not full_model_path:
            # let's train

            model_meta = on_train(
                {"samples_files": samples_files, "training_rate": len(samples_files)}
            )
            pprint(model_meta)
            model_path = model_meta[0][0]
        else:
            # let's make more samples

            logging.debug(f"Prediction args = {args=}")

            try:
                results = list(
                    queue_iter(
                        service_id=service_id,
                        gen=on_predict(args, service_id=service_id),
                    )
                )
                pprint(results)

            except KeyboardInterrupt as e:

                exit = input("Exit? [y]/n")

                if exit.startswith("n"):
                    continue
                else:
                    break
