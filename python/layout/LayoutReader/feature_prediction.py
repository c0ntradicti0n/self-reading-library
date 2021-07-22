from pprint import pprint

from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.pathant.Converter import converter


@converter(("feature", "predictor"), 'predicted.feature')
class LayoutPrediction(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, feature_meta, keras, *args, **kwargs):
        model = next(keras)
        self.debug = True
        for feature_df, meta in feature_meta:

            feature_df['layoutlabel'] = model.predict(feature_df)
            feature_df['layoutlabel'] = model.label_lookup.ids_to_tokens(feature_df['layoutlabel'])
            print(feature_df)
            pprint (list(feature_df['layoutlabel']))
            meta['label_lookup'] = model.label_lookup
            yield feature_df, meta
