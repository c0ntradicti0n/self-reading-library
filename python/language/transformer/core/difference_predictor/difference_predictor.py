from overrides import overrides

from allennlp.common.util import JsonDict
from allennlp.data import DatasetReader, Instance
from allennlp.data.tokenizers.word_splitter import SpacyWordSplitter
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
        self.model.vocab.extend_from_instances(None, instances=[instance])
        #self.model.extend_embedder_vocab(embedding_sources_mapping)
        output = self.predict_instance(instance)
        print ('predict json',output)

        table = BeautifulTable(max_width=120)
        table.set_style(BeautifulTable.STYLE_RST)
        table.append_column('words', output['words'])
        table.append_column('tags', output['tags'])
        table.append_column('logits', [" ".join([str(round(f, 1)) for f in l]) for l in output['logits']])


        print ('predict json',output)
        output = list(zip(output['tags'], output['words']))
        return str(table).replace('\n', '<br />')

        return list(zip(result['tags'], result['words']))

    @overrides
    def _json_to_instance(self, json_dict: JsonDict) -> Instance:
        """
        Expects JSON that looks like ``{"sentence": "..."}``.
        Runs the underlying model, and adds the ``"words"`` to the output.
        """
        print ("HALLO json")
        print (json_dict)

        sentence = json_dict["sentence"]
        tokens = self._tokenizer.split_words(sentence)
        return self._dataset_reader.text_to_instance(tokens)