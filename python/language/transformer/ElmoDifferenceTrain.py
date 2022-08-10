from core.pathant.Converter import converter
from language.transformer.ElmoTrain import ElmoTrain
from config import config


@converter(None, 'elmo_model.difference')
class ElmoDifferenceTrain(ElmoTrain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            elmo_config=config.difference_model_config,
            train_output_dir=config.difference_model_train_output,
            collection_path= config.ELMO_DIFFERENCE_COLLECTION_PATH,
            **kwargs)
        pass

    def __call__(self, *args, **kwargs):
        super().__call__(
            *args,
            **kwargs)



