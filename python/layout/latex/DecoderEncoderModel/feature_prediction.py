from pprint import pprint

from latex.LayoutReader.trueformatpdf2htmlEX import PDF_AnnotatorTool
from core.pathant.Converter import converter


@converter(("feature", "encoder_decoder_predictor"), 'predicted.feature')
class LayoutPrediction(PDF_AnnotatorTool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, feature_meta, keras, *args, **kwargs):
        model = next(keras)
        self.debug = True
        for feature_df, meta in feature_meta:
            prediction = model.predict(feature_df)
            feature_df['LABEL'] = model.label_lookup.ids_to_tokens(prediction)
            meta['label_lookup'] = model.label_lookup
            yield feature_df, meta
