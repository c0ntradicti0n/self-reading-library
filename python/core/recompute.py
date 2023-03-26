import os

from config import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from helpers.cache_tools import configurable_cache


@converter(["*", "*.*", "*.*.*"], "recompute")
class Recompute(PathSpec):
    def __init__(self, timout_sec=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout_sec = timout_sec

    def __call__(self, arg_meta, *args, **kwargs):
        for doc_id, meta in arg_meta:
            if doc_id.endswith(".tex"):
                if pdf_path := self.compiles(doc_id):
                    yield pdf_path, meta
            elif doc_id.endswith(".pdf"):
                yield doc_id, meta
            else:
                self.logger.error("dont know how to handle file " + doc_id)
