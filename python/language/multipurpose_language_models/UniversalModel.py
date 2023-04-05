import logging
import os


from core.microservice import microservice
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from helpers.cache_tools import shelve_it
from helpers.os_tools import o
from helpers.time_tools import timeit_context
import shelve


@microservice
@converter("instruction", "something")
class UniversalModel(PathSpec):
    Dockerfile = os.path.dirname(os.path.abspath(__file__))
    volumes = ["../../../ggml-alpaca-7b-q4.bin"]

    @shelve_it(Dockerfile + "/cache")
    def __call__(self, instruction, text, *args, **kwargs):
        return self.predict(instruction, text)

    def predict(self, instruction, text):
        logging.info(f"{instruction=} {text=}")
        with open("prompt", "w") as f:
            f.write(
                f"""### INSTRUCTION
                {instruction}
                
                ### INPUT
                {text}
                
                ### RESPONSE
                """
            )
        with timeit_context("universal model predict"):
            response = o(
                "./alpaca.cpp/chat -f prompt -m /volumes/ggml-alpaca-7b-q4.bin",
                err_out=False,
            ).strip()
        logging.info(f"{response=}")
        return response

    def load(self):
        pass


if __name__ == "__main__":
    os.environ["INSIDE"] = "no_update"
    print(
        UniversalModel(
            "Find a title for this text",
            """Seit über sieben Jahren erzählen sich die Historiker Daniel Meßner und Richard Hemmer Woche für Woche eine Geschichte aus der Geschichte. Das Besondere daran: der eine weiß nie, was der andere ihm erzählen wird. Dabei geht es um vergessene Ereignisse, außergewöhnliche Persönlichkeiten und überraschende Zusammenhänge der Geschichte aus allen Epochen.""",
        )
    )
