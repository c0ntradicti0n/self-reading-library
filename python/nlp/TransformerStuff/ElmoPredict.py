from allennlp.common import Params
from allennlp.predictors import Predictor
from texttable import Texttable

from python.layouteagle.pathant.PathSpec import PathSpec

from allennlp.models.model import Model

from python.nlp.TransformerStuff.difference_predictor.difference_predictor import DifferenceTaggerPredictor
import python.nlp.TransformerStuff.attentivecrftagger.attentivecrftagger



class ElmoPredict(PathSpec):
    def __init__(self, *args, config=None, train_output_dir, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = Params.from_file(params_file=config)
        self.model = Model.load(config=self.config, serialization_dir=train_output_dir)
        self.default_predictor = Predictor.from_path(train_output_dir)
        self.predictor = DifferenceTaggerPredictor(
            self.default_predictor._model,
            dataset_reader=self.default_predictor._dataset_reader)

        self.CSS = {
            (span_letter + "-" + tag) if tag != 'O'
                else tag

                    :
                        css

            for span_letter in ['L', 'I', 'B', 'U']
            for tag, css in self.CSS_SIMPLE.items()
        }

    def __call__(self, feature_meta, *args, **kwargs):
        consumed_tokens = 0

        while True:
            try: # https://stackoverflow.com/questions/51700960/runtimeerror-generator-raised-stopiteration-every-time-i-try-to-run-app
                next(feature_meta)
            except StopIteration:
                return

            wordi, meta = feature_meta.send(consumed_tokens)
            try:
                annotation = self.predictor.predict_json({"sentence": [w.text for w in wordi]})
                self.info(annotation)


                # rfind of not "O"
                consumed_tokens = next(i for i, (tag, word) in list(enumerate(annotation))[::-1] if tag != 'O')
                if consumed_tokens == 0:
                    consumed_tokens = len(wordi)

                yield annotation, {
                    **meta,
                    'CSS': self.CSS,
                    "consumed_i1": meta["i2_to_i1"][consumed_tokens],
                    "consumed_i2": consumed_tokens,
                }

            except StopIteration as e:
                pass
            except Exception as e:
                self.logger.error("Could not process " + str(wordi))
                raise e

    def info(self, annotation):
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["c", "l", "r"])
        table.add_rows([['i', 'tag', 'word']] + [[i, t, w ] for i, (t, w) in enumerate(annotation)])
        print (table.draw())
