import os

from texttable import Texttable

from config import config
from core.pathant.PathSpec import PathSpec
from helpers.best_model_tools import find_best_model

from helpers.conll_tools import annotation2conll_file
from helpers.hash_tools import hashval
from helpers.model_tools import BEST_MODELS
from helpers.random_tools import chance
from language.span.DifferenceSpanSet import DifferenceSpanSet

from queue import Queue, Empty

q2 = {}
q1 = {}


class ElmoPredict(PathSpec):
    def __init__(self, *args, elmo_config=None, train_output_dir, **kwargs):
        super().__init__(*args, **kwargs)
        self.elmo_config = elmo_config

        self.CSS = {
            (span_letter + "-" + tag) if tag != "O" else tag: css
            for span_letter in ["L", "I", "B", "U"]
            for tag, css in self.CSS_SIMPLE.items()
        }

    def init_queues(self):
        global q1
        global q2
        service_id = self.flags["service_id"]
        q2[service_id] = Queue()
        q1[service_id] = Queue()

    def __call__(self, feature_meta, *args, **kwargs):
        self.init_queues()

        for pdf_path, meta in feature_meta:

            q1[self.flags["service_id"]].put(0)

            while True:
                if "words" in meta:
                    words = meta["words"]
                else:
                    try:
                        try:
                            words, meta = q2[self.flags["service_id"]].get(timeout=9)
                            q2[self.flags["service_id"]].task_done()

                        except StopIteration:
                            self.logger.info("Finished predicting (on stop of queue)")
                            self.init_quees()
                            break
                    except Empty:
                        self.logger.info(
                            "Text windowing stopped with length 0 of window 0"
                        )
                        m = {}
                        m["doc_id"] = "finito"
                        m["annotation"] = []
                        yield pdf_path, m
                        break

                    if words is None:
                        self.logger.info("Finished predicting (on words is None)")
                        m = {}
                        m["doc_id"] = "finito"
                        m["annotation"] = []
                        yield pdf_path, m
                        break

                try:
                    annotation = None
                    while annotation is None:
                        annotation = self.predict(words, pdf_path)
                        if annotation is None:
                            self.logger.error("retrying to annotate document")
                except Exception as e:

                    raise

                if "words" in meta:
                    meta["annotation"] = annotation
                    yield pdf_path, meta
                    break
                else:
                    try:
                        try:

                            # rfind of not "O"
                            consumed_tokens = next(
                                i
                                for i, (tag, word) in list(enumerate(annotation))[::-1]
                                if tag != "O"
                            )
                        except StopIteration as e:
                            consumed_tokens = len(words)
                        except TypeError as e:
                            consumed_tokens = len(words)
                            self.logger.error(
                                "Error annotating document", exc_info=True
                            )

                        if consumed_tokens == 0:
                            consumed_tokens = 100
                            self.logger.info("empty prediction")
                        q1[self.flags["service_id"]].put(consumed_tokens)

                        yield pdf_path, {
                            **meta,
                            "annotation": annotation,
                            "CSS": self.CSS,
                            "consumed_i2": consumed_tokens,
                        }

                        q1[self.flags["service_id"]].put(consumed_tokens)

                    except Exception as e:
                        self.logger.error(
                            "Could not process " + str(words), exc_info=True
                        )
                        raise

            self.init_queues()

    def predict(self, words, path):
        annotation = self.predictor.predict_json({"sentence": words})

        subj_annotation = [(t, w) for t, w in annotation if "SUBJ" in t]
        self.info(subj_annotation)

        if chance(0.5) and DifferenceSpanSet(annotation):
            self.logger.info("Randomly saving annotation to dataset " + str(words))
            new_folder = config.ELMO_DIFFERENCE_COLLECTION_PATH + "/"
            print(f"{path=} {config.tex_data=}")
            filename = (
                path.replace(config.tex_data.replace("//", "/"), "")
                + "."
                + hashval(words)
                + ".conll"
            )
            annotation2conll_file(annotation, filename, new_folder)

        return annotation

    def load(self):
        from allennlp.common import Params
        from allennlp.predictors import Predictor
        from allennlp.models.model import Model
        from allennlp_models.tagging.models import crf_tagger

        self.logger.info("Loading difference model")
        self.model = Model.load(
            config=Params.from_file(params_file=self.elmo_config),
            serialization_dir=find_best_model(
                config.ELMO_DIFFERENCE_MODEL_PATH,
                lambda path: os.path.exists(path + "/vocabulary"),
            )[0],
        )
        self.logger.info("Loading predictor")
        self.default_predictor = Predictor.from_path(
            BEST_MODELS["difference"]["best_model_path"]
        )
        self.logger.info("Loading tagger_model")
        from language.transformer.difference_predictor.difference_predictor import (
            DifferenceTaggerPredictor,
        )

        self.predictor = DifferenceTaggerPredictor(
            self.default_predictor._model,
            dataset_reader=self.default_predictor._dataset_reader,
        )
        self.logger.info("Model loaded")

    def info(self, annotation):
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["c", "l", "r"])
        table.add_rows(
            [["i", "tag", "subj"]] + [[i, t, w] for i, (t, w) in enumerate(annotation)]
        )
        print(table.draw())
