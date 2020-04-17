import logging
import os
import string

import pandas

from layouteagle import config
from layouteagle.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.helpers.cache_tools import persist_to_file, file_persistent_cached_generator
from pathant.Converter import converter
from pathant.PathSpec import PathSpec


@converter("features", "layoutprediction")
class FeatureMaker(TrueFormatUpmarkerPDF2HTMLEX, PathSpec):
    def __init__(self, debug=True, *args, labels='column_labels', **kwargs):
        super().__init__(*args, **kwargs)
        self.labels = labels
        self.debug = debug

    @file_persistent_cached_generator(config.cache + 'collected_features.json')
    def __call__(self, feature_dfs, layoutmodel, ):
        layoutmodel = next(layoutmodel)
        for feature_df in feature_dfs:
            feature_df[self.labels] = layoutmodel.predict(feature_df)
            pandas_pickle_path = labeled_pdf_path + self.path_spec._to
            pdf_doc.features.divs = pdf_doc.features.divs.astype(str)

            pdf_doc.features.to_pickle(pandas_pickle_path)
            yield pandas_pickle_path