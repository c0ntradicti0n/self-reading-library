import sys

from layout.latex.LayoutReader.trueformatpdf2htmlEX import PDF_AnnotatorTool

sys.path.append(".")

from core.pathant.Converter import converter
from helpers.cache_tools import configurable_cache
from core import config

@converter("feature", 'assigned.feature')
class FeatureAssigner(PDF_AnnotatorTool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    @configurable_cache(
        config.cache + 'labeled_features_pickled.json',
        if_cache_then_finished=True
    )
    def __call__(self, feature_meta, *args, **kwargs):
        for feature_df, meta in feature_meta:
            feature_df.text = feature_df.text.astype(str)
            feature_df_path = meta['html_path'] + meta['doc_id'] + self.path_spec._to
            feature_df.to_pickle(feature_df_path)
            yield feature_df_path, meta

