from core.pathant.Converter import converter
from language.transformer.ElmoPredict import ElmoPredict
from config import config


@converter(["reading_order.page", "reading_order.filter_align_text"], 'reading_order.page.difference')
class ElmoDifferencePredict(ElmoPredict):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            elmo_config=config.difference_model_config,
            train_output_dir=config.difference_model_train_output,
            **kwargs)
        pass

    CSS_SIMPLE = {
           'O': 'color: #123',
           'SUBJECT': 'background-color: #FFDC00 ' ,
           'CONTRAST': 'background-color: #F012BE '
    }

