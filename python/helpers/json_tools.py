import gzip
import json

import numpy as np


def json_file_update(path, update={}):
    with open(path) as f:
        content = json.load(f)
    if update:
        content.update(update)
        with open(path, "w") as f:
            f.write(json.dumps(content))
    return content


# conmak @ https://stackoverflow.com/a/65151218
def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()


def dump_json_gzip(meta, path_gzip_json):
    with gzip .open(
            path_gzip_json,
            "wt",
            encoding="ascii",
    ) as zipfile:
        json.dump(meta, zipfile, default=np_encoder)


def load_json_gzip(path_gzip_json):
    with gzip.open(
            path_gzip_json,
            "rt",
            encoding="ascii",
    ) as zipfile:
        return json.load(zipfile)
