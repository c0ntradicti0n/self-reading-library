import unittest
from core.pathant.PathSpec import PathSpec
from core.pathant.Converter import converter
from core.RestPublisher.RestPublisher import RestPublisher
from core.RestPublisher.RestPublisher import Resource
from core.RestPublisher.react import react
import pandas as pd
import uuid
from itertools import islice
from  python.core import config
import types
from pprint import pprint
import os

def load_all_annotations(path):
    all_files = glob.glob(
        os.path.join(path, "*.pandas"))  # advisable to use os.path.join as this makes concatenation OS independent

    df_from_each_file = (pd.read_pickle(f) for f in all_files)
    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
    return concatenated_df

@converter(("annotation", "upload_annotation"), "annotation.collection")
class Annotator(PathSpec):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, annotation_metas, *args, **kwargs):
        for annotation, meta in annotation_metas:
            df = annotation['df']
            hash = meta['html_path'].replace("/", '-') + "_" + str(df['page_number'][0][0])
            df['LABEL'] = df['LABEL'].astype(object)
            df['LABEL'] = [annotation['labels']]
            if not os.path.isdir(config.COLLECTION_PATH):
                os.mkdir(config.COLLECTION_PATH)
            path = config.COLLECTION_PATH + hash + ".pickle"
            pd.to_pickle(df, path)


