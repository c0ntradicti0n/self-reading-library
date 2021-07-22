import sys
sys.path.append(".")

from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.pathant.Converter import converter


@converter("feature", 'assigned.feature')
class FeatureAssigner(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, feature_meta, *args, **kwargs):
        for feature_df, meta in feature_meta:
            self.assign_labels_from_div_content(feature_df=feature_df)
            feature_df.text = feature_df.text.astype(str)
            feature_df_path = meta['filename'] + self.path_spec._to
            feature_df.to_pickle(feature_df_path)
            yield feature_df_path, meta

