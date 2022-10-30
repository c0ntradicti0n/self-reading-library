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
