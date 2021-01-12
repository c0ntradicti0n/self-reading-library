from python.layouteagle import config
from python.layouteagle.pathant.Converter import converter
from python.layouteagle.pathant.PathSpec import PathSpec
from python.nlp.TransformerStuff.core.corpus import Corpus
from python.nlp.TransformerStuff.core.model import Model
from python.nlp.TransformerStuff.core.textsplitter import TextSplitter


class ElmoPredict(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    corpus_first = Corpus(path=config.corpus_conll)
    model_first = Model(model_path="server/models/model_first.tar.gz")

    textsplitter = TextSplitter(model_first, None)

    def __call__(self, feature_meta, *args, **kwargs):
        for wordi, meta in feature_meta:
            css = "?"
            yield css, meta
