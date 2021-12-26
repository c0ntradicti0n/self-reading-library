from overrides import overrides

from allennlp.common.util import JsonDict
from allennlp.data import DatasetReader, Instance, Token
from allennlp.data.tokenizers.spacy_tokenizer import SpacyTokenizer
from allennlp.models import Model
from allennlp.predictors.predictor import Predictor


from beautifultable import BeautifulTable

@Predictor.register('difference_predictor')
class DifferenceTaggerPredictor(Predictor):
    """
    Predictor for any model that takes in a sentence and returns
    a single set of tags for it.  In particular, it can be used with
    the :class:`~allennlp.models.crf_tagger.CrfTagger` model
    and also
    the :class:`~allennlp.models.simple_tagger.SimpleTagger` model.
    """
    def __init__(self, model: Model, dataset_reader: DatasetReader, language: str = 'en_core_web_sm') -> None:
        super().__init__(model, dataset_reader)
        self._tokenizer = SpacyWordSplitter(language=language, pos_tags=True)
        self.model =  model

    @overrides
    def predict_json(self, inputs: JsonDict) -> JsonDict:
        instance = self._json_to_instance(inputs)
        #self.model.vocab.extend_from_instances(self.model., instances=[instance])
        #self.model.extend_embedder_vocab(embedding_sources_mapping)
        output = self.predict_instance(instance)
        output = list(zip(output['tags'], output['words']))
        return  output

    @overrides
    def _json_to_instance(self, json_dict: JsonDict) -> Instance:
        """
        Expects JSON that looks like ``{"sentence": "..."}``.
        Runs the underlying model, and adds the ``"words"`` to the output.
        """
        sentence = json_dict["sentence"]
        tokens = [Token(token) for token in sentence]
        return self._dataset_reader.text_to_instance(tokens)