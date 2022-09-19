import builtins
import hashlib
import itertools
import logging
import operator
import os

from allennlp.predictors import Predictor
from regex import regex as re

from helpers.list_tools import threewise
from language.transformer.core.corpus import Corpus
from language.transformer.difference_predictor.difference_predictor import (
    MoreVersatileTaggerPredictor,
)


def split_list_on_lambda(l, lam):
    """split a list of anything based on a lambda, so that the splitting element is the first of each group"""
    groups = (list(g) for k, g in itertools.groupby(l[::-1], lam))
    reversed_groups = list(itertools.starmap(operator.add, zip(*[groups] * 2)))
    return [l[::-1] for l in reversed_groups[::-1]]


import pickle


def pickle_cached(fun):
    cache_dir = "cache/predictions/"

    def wrapper(*args):
        hash = pickle.dumps(str(args))
        md5sum = hashlib.md5(str(hash).encode("utf-8")).hexdigest()
        path = cache_dir + md5sum + ".dump"

        if os.path.isfile(str(path)):
            with open(path, "rb") as config_dictionary_file:
                return pickle.load(config_dictionary_file)
        else:
            try:
                results = fun(*args)
                with open(path, "wb") as f:
                    pickle.dump(results, f)
                return results
            except builtins.KeyError:
                logging.error(f"{args} could not be {str(fun)}")
                return []
            except IndexError:
                return []

    return wrapper


class Model:
    def __init__(self, model_path):
        self.default_predictor = Predictor.from_path(model_path)
        self.model = MoreVersatileTaggerPredictor(
            self.default_predictor._model,
            dataset_reader=self.default_predictor._dataset_reader,
        )

    allowed_chars = sorted(
        """ !?$%&()+,-.\ 0123456789:;?ABCDEFGHIJKLMNOPQRSTUVWXYZ()[]_`abcdefghijklmnopqrstuvwxyz‘’“”\n"""
    )

    def clean(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        text = "".join([c for c in text if c in self.allowed_chars])
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @pickle_cached
    def predict_tokens(self, tokens: str):
        prediction = self.model.predict_tokens(tokens)
        return self.post_process_prediction(prediction)

    @pickle_cached
    def predict_sentence(self, sentence: str):
        prediction = self.model.predict_json({"sentence": sentence})
        return self.post_process_prediction(prediction)

    def post_process_prediction(self, prediction):
        tags = list(Corpus.bioul_to_bio(prediction["tags"]))
        tags = self.clean_intermediate_beginnings(tags)
        return list(zip(prediction["words"], tags))

    def clean_intermediate_beginnings(self, tags):
        for (i1, t1), (i2, t2), (i3, t3) in threewise(enumerate(tags)):
            if t1[0] == "I" and t2[0] == "B" and t3[0] == "I":
                tags[i2] = "I" + tags[i2][1:]
        return tags
