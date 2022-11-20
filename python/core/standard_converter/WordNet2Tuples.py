from nltk.corpus import wordnet as wn

from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec


@converter(
    "annotation",
    "antonyms",
)
class AnnotatorUnpacker(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, prediction_metas, *args, **kwargs):
        for path, meta in prediction_metas:
            annotation = meta["annotation"]
            words = [t[0] for t in annotation]
            antonyms = []
            synonyms = []

            for w in words:
                for s in wn.synsets(w):
                    antonyms.extend(s.lemmas()[0].antonyms())
                    synonyms.extend(s.synonyms())

            meta["antonyms"] = antonyms
            meta["synonyms"] = synonyms
            yield from wn.all_synsets("n")
