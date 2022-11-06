import json
import os
import gzip
from typing import Iterable

import pandas
import logging

from config import config
from core.pathant.Converter import converter
from core.pathant.Filter import existing_in_dataset_or_database
from core.pathant.PathSpec import PathSpec
from core.event_binding import queue_iter, RestQueue, queue_put, q, d
from helpers.cache_tools import configurable_cache
from helpers.json_tools import np_encoder
from layout.model_helpers import changed_labels


AnnotatedToGoldQueueRest = RestQueue(
    service_id="gold_annotation", update_data=changed_labels, rated_queue=True
)


@converter(
    "annotation.collection",
    "annotation.collection.silver",
)
class AnnotationLoader(PathSpec):
    @configurable_cache(
        config.cache + os.path.basename(__file__),
        from_path_glob=config.COLLECTION_PATH + "/*.pickle",
        filter_path_glob=existing_in_dataset_or_database("/*.json.gz"),
    )
    def __call__(self, prediction_metas, *args, **kwargs):
        # all annotation are comming from the cache, that is read from globbing the files
        # so nothing to do here
        pass


@converter(
    "annotation.collection.silver",
    "annotation.collection.gold",
)
class AnnotatorUnpacker(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, prediction_metas, *args, **kwargs):
        for pickle_path, meta in prediction_metas:
            df = pandas.read_pickle(pickle_path)
            df["bbox"] = df.apply(
                lambda x: list(zip(*df.x0, *df.y0, *df.x1, *df.y1)), axis=1
            )
            df["labels"] = df["LABEL"].apply(list)
            yield pickle_path, df.to_dict(orient="records")[0]


@converter(
    "annotation.collection.gold",
    "annotation.collection.platinum",
)
class AnnotatorRate(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, prediction_metas, *args, **kwargs):
        self.service = self.flags["service_id"]

        for _p_m in queue_iter(
            service_id=self.service,
            gen=(p_m for p_m in prediction_metas),
            single=False,
        ):
            id, meta = _p_m
            try:
                rating_trial, rating_score = d[self.service].scores(id)
            except Exception as e:
                rating_trial = 0
                rating_score = 0.0
                logging.error(f"Scores not found for {id}, {self.service}")

            if rating_trial > config.MIN_CAPTCHA_TRIALS:
                yield _p_m
            else:
                q[self.service].put(self.service, _p_m)
                q[self.service].rate(id, rating_score)


@converter(
    "annotation.collection.platinum",
    "annotation.collection.fix",
)
class AnnotatorSaveFinal(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def single(element):
        if not isinstance(element, Iterable):
            return element
        else:
            return element[0]

    def __call__(self, prediction_metas, *args, **kwargs):
        self.service = self.flags["service_id"]

        for path, meta in prediction_metas:
            del meta["LABEL"]
            meta["raw_dataset_pickle"] = path
            meta["image_path"] = self.single(meta["image_path"])
            meta["pickle_path"] = self.single(meta["image_path"])
            meta["page_number"] = self.single(meta["page_number"])
            meta["text"] = list(meta["text"])
            page_number = meta["page_number"]
            old_folder, fname = os.path.split(path)
            fname, endings = fname.split(".")[0], fname.split(".")[1:]

            new_folder = config.GOLD_DATASET_PATH + "/" + self.flags["service_id"] + "/"
            if meta["rating_score"] == -1:
                new_folder = (
                    config.TRASH_DATASET_PATH + "/" + self.flags["service_id"] + "/"
                )

            if not os.path.isdir(new_folder):
                os.makedirs(new_folder)
            with gzip.open(
                new_folder + fname + "." + str(page_number) + ".json.gz",
                "wt",
                encoding="ascii",
            ) as zipfile:
                json.dump(meta, zipfile, default=np_encoder)