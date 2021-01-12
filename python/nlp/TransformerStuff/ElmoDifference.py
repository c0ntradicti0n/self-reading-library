from python.layouteagle.pathant.Converter import converter
from python.nlp.TransformerStuff.ElmoPredict import ElmoPredict


@converter("wordi.page", 'wordi.page.difference')
class ElmoDifference(ElmoPredict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, feature_meta, *args, **kwargs):
        for wordi, meta in feature_meta:
            css = "?"
            yield css, meta
