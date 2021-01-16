from allennlp.common import Params
from allennlp.predictors import Predictor

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

    # textsplitter = TextSplitter(model_first, None)

    def __call__(self, feature_meta, *args, **kwargs):
        for wordi, meta in feature_meta:
            annotation = self.predictor.predict_json({"sentence":str(wordi)})
            yield annotation, meta
