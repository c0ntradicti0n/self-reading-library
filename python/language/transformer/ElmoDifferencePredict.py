from core.microservice import microservice
from core.pathant.Converter import converter
from language.transformer.ElmoPredict import ElmoPredict
from config import config


#if __name__ == "__main__":
#    import os
#    os.environ["INSIDE"] = "True"

@microservice
@converter(
    ["reading_order.page", "reading_order.filter_align_text"],
    "reading_order.page.difference",
)
class ElmoDifferencePredict(ElmoPredict):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            elmo_config=config.difference_model_config,
            train_output_dir=config.difference_model_train_output,
            **kwargs
        )
        pass

    CSS_SIMPLE = {
        "O": "color: #123",
        "SUBJECT": "background-color: #FFDC00 ",
        "CONTRAST": "background-color: #F012BE ",
    }

if __name__ == "__main__":

    from wsgiref import simple_server

    simple_server.make_server("0.0.0.0", 7777, ElmoDifferencePredict.converter.application).serve_forever()
