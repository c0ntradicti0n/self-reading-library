from core.pathant.Converter import converter
from core.pathant.train_on import train_on
from language.transformer.ElmoTrain import ElmoTrain
from config import config

@train_on
@converter(None, "elmo_model.difference")
class ElmoDifferenceTrain(ElmoTrain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            elmo_config=config.difference_model_config,
            train_output_dir=config.difference_model_train_output,
            collection_path=config.ELMO_DIFFERENCE_COLLECTION_PATH,
            **kwargs
        )

    on = config.GOLD_SPAN_SET
    training_rate_mode = "ls"
    model_dir = config.ELMO_DIFFERENCE_MODEL_PATH
    service_id = "difference"


    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)


if __name__ ==  "__main__":
    ElmoDifferenceTrain.wait_for_change()