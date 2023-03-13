import json
import numpy as np
from franz.openrdf.model import URI, Literal


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, URI):
            return str(obj.uri)
        if isinstance(obj, Literal):
            return str(obj.label)
        return super(NpEncoder, self).default(obj)


def jsonify(data):
    return json.dumps(data, ensure_ascii=False, cls=NpEncoder)
