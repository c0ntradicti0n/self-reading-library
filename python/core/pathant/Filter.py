import os

from config import config
from core.event_binding import q, d
from core.pathant.PathSpec import PathSpec


def existing_in_dataset_or_database(extension):
    return [
        lambda self: config.GOLD_DATASET_PATH
        + "/"
        + self.flags["service_id"]
        + extension,
        lambda self: config.TRASH_DATASET_PATH
        + "/"
        + self.flags["service_id"]
        + extension,
        lambda self: [
            os.path.basename(p) for p in q[self.flags["service_id"]].get_doc_ids()]+[
        os.path.basename(p)
    for p in d[self.flags["service_id"]].get_doc_ids()
        ],
    ]


class Filter(PathSpec):
    def __init__(self, f, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.f = f

    def __call__(self, x_ms, *args, **kwargs):
        for x_m in x_ms:
            if self.f(x_m):
                print(self.f(x_m))
                yield x_m
