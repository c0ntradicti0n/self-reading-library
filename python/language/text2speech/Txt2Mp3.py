import logging
import os

from ant import Ant
from config import config
from core.microservice import microservice

from core.pathant.Converter import converter
from core.pathant.PathSpec import cache_flow
from helpers.cache_tools import configurable_cache
from language.transformer.Pager import preprocess_text


def generate_audio(id, text):
    out_path = get_audio_path(id)

    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    except:
        logging.error(f"Could not make audio directory {out_path}", exc_info=True)

    with open(f"{id}.txt", "w") as f:
        f.write(text)
    real_path = os.path.dirname(os.path.realpath(__file__))

    os.system(f"python3 {real_path}/tts.py -i {id}.txt {out_path}.ogg ")

    return out_path


def get_audio_path(id):
    out_path = (
        config.audio_path + id.replace(config.hidden_folder, "") + config.audio_format
    )
    return out_path


@microservice
@converter("reading_order", "audio")
class Txt2Mp3(Ant):
    docker_kwargs = {
        "volumes": [
            "$CWD/python:/home/finn/Programming/self-reading-library/python",
            f"$CWD/{config.audio_path}:/home/finn/Programming/self-reading-library/python/.layouteagle/audio/language/text2speech/",
        ]
    }

    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, cached=cache_flow.iterate, **kwargs)

        self.n = n
        self.debug = debug

    def load(self):
        logging.info("loading tts!")
        real_path = os.path.dirname(os.path.realpath(__file__))
        logging.info(real_path)

        generate_audio(
            "language/text2speech/test_text",
            "Hallo du dumme Sau. Sprich mir einen schönen Text.",
        )

    def predict(self, id, text):
        return generate_audio(id, text)

    @configurable_cache(
        filename=config.cache + os.path.basename(__file__),
    )
    def __call__(self, iterator, *args, **kwargs):
        for id, meta in iterator:
            text = (
                " ".join(preprocess_text(meta["enumerated_texts"])).replace("/n", " ")
                + "\n"
            )
            audio_path = self.predict(id, text)
            meta["audio_path"] = audio_path
            yield id, meta


if __name__ == "__main__":
    list(
        Txt2Mp3(
            [
                (
                    "test",
                    {
                        "text": "Emissions data from three companies, Bit Digital, Greenidge and Stronghold, indicated their operations create 1.6m tons of CO2 annually, an amount produced by nearly 360,000 cars. Their environmental impact is significant despite industry claims about clean energy use and climate commitments, the lawmakers wrote.\n"
                    },
                )
            ]
        )
    )
