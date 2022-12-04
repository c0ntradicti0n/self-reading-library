import os
from functools import reduce
from textwrap import wrap

from more_itertools import pairwise

from config import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from helpers.cache_tools import configurable_cache


@converter(
    "span_annotation.collection.analysed",
    "span_annotation.collection.analysed.filter",
)
class Filter(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, prediction_metas, *args, **kwargs):

        for i, (path, meta) in enumerate(prediction_metas):
            if self.flags["search"] in meta["span_set"]:
                yield path, meta
