import logging

from PIL import Image

from core.pathant.PathSpec import PathSpec
from core.pathant.Converter import converter
from core.rest.RestPublisher import RestPublisher
from core.rest.RestPublisher import Resource
from core.rest.react import react
import pandas as pd

from helpers.hash_tools import bas64encode
from config import config
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
                hash = bas64encode(id) + "_" + str(meta['page_number'])
                if not os.path.isdir(config.COLLECTION_PATH):
                    os.mkdir(config.COLLECTION_PATH)
                path = config.COLLECTION_PATH + hash + ".pickle"
                pd.to_pickle(df, path)
                meta['collection_path'] = path
                meta['image'] = Image.open(meta['image_path'])
                meta['human_image'] = Image.open(meta['human_image_path'])

                yield id, meta
            except Exception as e:
                logging.error("Error when preparing pagewise layout annotation", exc_info=True)
