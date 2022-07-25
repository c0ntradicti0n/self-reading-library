import logging
import unittest
from core.pathant.PathSpec import PathSpec
from core.pathant.Converter import converter
from core.RestPublisher.RestPublisher import RestPublisher
from core.RestPublisher.RestPublisher import Resource
from core.RestPublisher.react import react
import pandas as pd
import uuid
from itertools import islice

from helpers.hash_tools import bas64encode
from python.core import config
import types
from pprint import pprint
import os
import pyarrow.parquet as pq


@converter(("annotation", "upload_annotation"), "annotation.collection")
class Annotator(PathSpec):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, annotation_metas, *args, **kwargs):
        for id, meta in annotation_metas:


            try:
                df = pq.read_table(meta['df_path']).to_pandas()
                hash = bas64encode(id) + "_" + str(list(df['page_number'])[0][0])
                if not os.path.isdir(config.COLLECTION_PATH):
                    os.mkdir(config.COLLECTION_PATH)
                path = config.COLLECTION_PATH + hash + ".pickle"
                pd.to_pickle(df, path)
                meta['collection_path'] = path
                yield id, meta
            except Exception as e:
                logging.error("Error when preparing pagewise layout annotation", exc_info=True)


