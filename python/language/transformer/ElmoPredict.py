from allennlp.common import Params
from allennlp.predictors import Predictor
from texttable import Texttable
from core.pathant.PathSpec import PathSpec
from allennlp.models.model import Model
from language.transformer.difference_predictor.difference_predictor import DifferenceTaggerPredictor
from queue import Queue, Empty

q2 = {}
q1 = {}


model = None

class ElmoPredict(PathSpec):
    def __init__(self, *args, elmo_config=None, train_output_dir, **kwargs):
        super().__init__(*args, **kwargs)
        self.elmo_config = elmo_config
        self.config = Params.from_file(params_file=elmo_config)

        self.CSS = {
            (span_letter + "-" + tag) if tag != 'O'

            else tag

            :

                css

            for span_letter in ['L', 'I', 'B', 'U']
            for tag, css in self.CSS_SIMPLE.items()
        }

    def init_queues(self):
        global q1
        global q2
        service_id = self.flags['service_id']
        q2[service_id] = Queue()
        q1[service_id] = Queue()

    def __call__(self, feature_meta, *args, **kwargs):
        self.init_queues()
        global model
        for pdf_path, meta in feature_meta:

            q1[self.flags['service_id']].put(0)

            while True:
                if "words" in meta:
                    words = meta['words']
                else:
                    try:
                        try:
                            words, meta = q2[self.flags['service_id']].get(timeout=9)
                            q2[self.flags['service_id']].task_done()

                        except StopIteration:
                            self.logger.info("Finished predicting (on stop of queue)")
                            self.init_quees()
                            break
                    except Empty:
                        self.logger.info("Text windowing stopped with length 0 of window 0")
                        m = {}
                        m['doc_id'] = "finito"
                        m['annotation'] = []
                        yield pdf_path, m
                        break

                    if words is None:
                        self.logger.info("Finished predicting (on words is None)")
                        m = {}
                        m['doc_id'] = "finito"
                        m['annotation'] = []
                        yield pdf_path, m
                        break

                try:
                    annotation = self.predict(words)
                except Exception as e:
                    self.logger.error("Faking annotation because of error " + str(e), stack_info=True)
                    annotation = [('O', w) for w in words]

                if "words" in meta:
                    meta['annotation'] = annotation
                    yield pdf_path, meta
                    break
                else:
                    try:
                        try:
                            # rfind of not "O"
                            consumed_tokens = next(i for i, (tag, word) in list(enumerate(annotation))[::-1] if tag != 'O')
                        except StopIteration as e:
                            consumed_tokens = len(words)

                        if consumed_tokens == 0:
                            consumed_tokens = 100
                            self.logger.info("empty prediction")
                        q1[self.flags['service_id']].put(consumed_tokens)

                        yield pdf_path, {
                            **meta,
                            'annotation': annotation,
                            'CSS': self.CSS,
                            "consumed_i2": consumed_tokens,
                        }

                        q1[self.flags['service_id']].put(consumed_tokens)



                    except Exception as e:
                        self.logger.error(e.__repr__())
                        self.logger.error("Could not process " + str(words), e)
                        raise

            self.init_queues()

    def predict(self, words):
        global model
        if not model or not self.predictor:
            model = Model.load(config=self.config,
                               serialization_dir=self.flags['difference_model_path'])
            self.default_predictor = Predictor.from_path(self.flags['difference_model_path'])
            self.predictor = DifferenceTaggerPredictor(
                self.default_predictor._model,
                dataset_reader=self.default_predictor._dataset_reader
            )
        annotation = self.predictor.predict_json({"sentence": words})
        subj_annotation = [(t, w) for t, w in annotation if "SUBJ" in t]
        self.info(subj_annotation)
        return annotation

    def info(self, annotation):
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["c", "l", "r"])
        table.add_rows([['i', 'tag', 'subj']] + [[i, t, w] for i, (t, w) in enumerate(annotation)])
        print(table.draw())
