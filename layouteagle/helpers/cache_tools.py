import inspect
import json
import logging
import os


def persist_to_file(file_name):

    def decorator(original_func):

        try:
            cache = json.load(open(file_name, 'r'))
        except (IOError, ValueError):
            cache = {}

        def new_func(*param):

            hash = str(list(
                {
                    k if any(isinstance(k, t) for t in [int, str, float]) else type(k):
                        v if any(isinstance(v, t) for t in [int, str, float]) else type(v)
                    for k, v in kv.__dict__.items()} if hasattr(kv, "__dict__") else str(kv)
                for kv in param))

            if hash not in cache:
                logging.info(f"Saving {hash} to cache file {file_name}" )
                #try:
                cache[hash] = original_func(*param)
                #except Exception:
                #    os.system(f"rm {file_name}")
                #    raise
                json.dump(cache, open(file_name, 'w'))

            return cache[hash]

        return new_func

    return decorator