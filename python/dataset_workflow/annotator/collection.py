import unittest
from python.layouteagle.pathant.PathSpec import PathSpec
from python.layouteagle.pathant.Converter import converter
from layouteagle.RestPublisher.RestPublisher import RestPublisher
from layouteagle.RestPublisher.RestPublisher import Resource
from layouteagle.RestPublisher.react import react
import pandas as pd
import uuid
from itertools import islice
from  python.layouteagle import config
import types
from pprint import pprint
import os

def load_all_annotations(path):
    all_files = glob.glob(
        os.path.join(path, "*.pandas"))  # advisable to use os.path.join as this makes concatenation OS independent

    df_from_each_file = (pd.read_pickle(f) for f in all_files)
    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
    return concatenated_df

@converter("annotation", "annotation.collection")
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


