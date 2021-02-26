from python.layouteagle.pathant.Converter import converter
from python.nlp.TransformerStuff.ElmoPredict import ElmoPredict
from python.layouteagle import config

@converter("wordi.page", 'wordi.page.difference')
class ElmoDifference(ElmoPredict):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            config=config.difference_model_config,
            train_output_dir=config.difference_model_train_output,
            **kwargs)
        pass

    CSS_SIMPLE = {
           'O': 'color: #123',
           'SUBJECT': 'background-color: #FFDC00 ' ,
           'CONTRAST': 'background-color: #F012BE '
    }

