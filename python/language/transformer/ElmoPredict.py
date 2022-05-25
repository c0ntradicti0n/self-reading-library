from allennlp.common import Params
from allennlp.predictors import Predictor
from texttable import Texttable
from core.pathant.PathSpec import PathSpec
from allennlp.models.model import Model
from language.transformer.difference_predictor.difference_predictor import DifferenceTaggerPredictor
from queue import Queue

q2 = Queue()
q1 = Queue()


class ElmoPredict(PathSpec):
    def __init__(self, *args, elmo_config=None, train_output_dir, **kwargs):
        super().__init__(*args, **kwargs)
        self.elmo_config = elmo_config
        self.config = Params.from_file(params_file=elmo_config)
        self.model = None
        self.CSS = {
            (span_letter + "-" + tag) if tag != 'O'

            else tag

            :

                css

            for span_letter in ['L', 'I', 'B', 'U']
            for tag, css in self.CSS_SIMPLE.items()
        }

    def init_quees(self):
        global q1
        global q2
        q2 = Queue()
        q1 = Queue()

    def __call__(self, feature_meta, *args, **kwargs):


        for _ in feature_meta:

            q1.put(0)

            while True:
                try:  # https://stackoverflow.com/questions/51700960/runtimeerror-generator-raised-stopiteration-every-time-i-try-to-run-app
                    words, meta = q2.get()
                    q2.task_done()

                except StopIteration:
                    self.logger.info("finished predicting")
                    self.init_quees()
                    break

                if words == None:
                    self.logger.info("finished predicting")
                    break

                try:
                    if not self.model:
                        self.model = Model.load(config=self.config, serialization_dir=self.flags['difference_model_path'])
                        self.default_predictor = Predictor.from_path(self.flags['difference_model_path'])
                        self.predictor = DifferenceTaggerPredictor(
                            self.default_predictor._model,
                            dataset_reader=self.default_predictor._dataset_reader
                        )
                    annotation = self.predictor.predict_json({"sentence": words})
                    self.info(annotation)
                except Exception as e:
                    self.logger.error("Faking annotation because of error " + str(e),  stack_info=True)
                    annotation = [('O', w) for w in words]
                    self.init_quees()
                    continue


                try:
                    try:
                        # rfind of not "O"
                        consumed_tokens = next(i for i, (tag, word) in list(enumerate(annotation))[::-1] if tag != 'O')
                    except StopIteration as e:
                        consumed_tokens = len(words)

                    q1.put(consumed_tokens)

                    yield annotation, {
                        **meta,
                        'CSS': self.CSS,
                        "consumed_i2": consumed_tokens,
                    }

                    q1.put(consumed_tokens)



                except Exception as e:
                    self.logger.error(e.__repr__())
                    self.logger.error("Could not process " + str(words), e)
                    raise

            self.init_quees()

    def info(self, annotation):
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["c", "l", "r"])
        table.add_rows([['i', 'tag', 'word']] + [[i, t, w] for i, (t, w) in enumerate(annotation)])
        print(table.draw())
