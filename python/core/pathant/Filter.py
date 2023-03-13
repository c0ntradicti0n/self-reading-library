import logging
import os
from glob import glob
from typing import Callable, Iterable

from config import config
from core.event_binding import q, d
from core.pathant.PathSpec import PathSpec
from helpers.os_tools import filename_only
from helpers.time_tools import timeit_context


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
            os.path.basename(p) for p in q[self.flags["service_id"]].get_doc_ids()
        ]
        + [os.path.basename(p) for p in d[self.flags["service_id"]].get_doc_ids()],
    ]


def not_exists(extension):
    def decorator(gen_after):
        def _(self, gen_before, *args, **kwargs):

            for path, meta in gen_after(self, gen_before):

                msg = "Sieve of existence"
                blacklist = []
                _filter_path_glob = existing_in_dataset_or_database(extension)

                with timeit_context(msg, logger=logging.info):
                    for i, p in enumerate(_filter_path_glob):
                        if isinstance(p, Callable):
                            result = p(self)
                            if isinstance(result, str):
                                _filter_path_glob[i] = result
                            elif isinstance(result, Iterable):
                                result = [filename_only(r) for r in result]
                                blacklist.extend(result)
                                _filter_path_glob[i] = None
                            else:
                                logging.error(
                                    f"dont know how to handle filter return type, {result}"
                                )
                msg = f"Cache glob blacklist"
                with timeit_context(msg, logger=logging.info):
                    blacklist += [
                        filename_only(os.path.basename(fp))
                        for path in _filter_path_glob
                        if path
                        for fp in glob(path)
                    ]

                if path not in blacklist:
                    logging.info(f"Does not exist {path=}")
                    yield path, meta
                else:
                    logging.info("Sieve of existence did something")

        return _

    return decorator


class Filter(PathSpec):
    def __init__(self, f, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.f = f

    def __call__(self, x_ms, *args, **kwargs):
        for x_m in x_ms:
            if self.f(x_m):
                print(self.f(x_m))
                yield x_m
