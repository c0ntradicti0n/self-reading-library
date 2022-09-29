import os
from threading import Thread

import pandas

from config import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from core.event_binding import queue_iter, RestQueue, queue_put
from helpers.cache_tools import configurable_cache
from layout.model_helpers import changed_labels
import logging


AnnotatedToGoldQueueRest = RestQueue(
    service_id="gold_annotation", update_data=changed_labels
)


@converter(
    "annotation.collection",
    "annotation.collection.silver",
)
class AnnotationLoader(PathSpec):
    @configurable_cache(
        config.cache + os.path.basename(__file__),
        from_path_glob=config.COLLECTION_PATH + "/*.pickle",
    )
    def __call__(self, prediction_metas, *args, **kwargs):
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
            df["bbox"] = df.apply(lambda x: list(zip(*df.x0, *df.y0, *df.x1, *df.y1)), axis=1)
            df["labels"] = df["LABEL"].apply(list)
            yield pickle_path, df.to_dict(orient='records')[0]
