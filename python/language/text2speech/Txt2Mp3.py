import logging
import os

from ant import Ant
from core import config

from core.pathant.Converter import converter
from core.pathant.PathSpec import cache_flow
from helpers.cache_tools import configurable_cache
from language.transformer.Pager import preprocess_text


def generate_audio(id, text):
    out_path = config.audio_path + id.replace(config.hidden_folder, "") + config.audio_format

    try:
        os.makedirs(os.path.dirname(out_path))
    except:
        logging.error(f"Could not make audio directory {out_path}", exc_info=True)
    with open(f"{id}.txt", "w") as f:
        f.write(text)

    os.system(f". ../tts/venv/bin/activate &&  python ../tts/tts.py -i {id}.txt {out_path}.ogg ")

    return out_path


@converter('reading_order', 'audio')
class Txt2Mp3(Ant):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, cached=cache_flow.iterate, **kwargs)
        self.n = n
        self.debug = debug

    @configurable_cache(
        filename=config.cache + os.path.basename(__file__),
    )
    def __call__(self, iterator, *args, **kwargs):
        for id, meta in iterator:
            text = " ".join(preprocess_text(meta["enumerated_texts"])).replace("/n", " ") + "\n"

            audio_path = generate_audio(id, text)

            meta["audio_path"] = audio_path
            yield id, meta


if __name__ == "__main__":
    list(
        Txt2Mp3(
            [
                ("test",
                 {
                     "text": "Emissions data from three companies, Bit Digital, Greenidge and Stronghold, indicated their operations create 1.6m tons of CO2 annually, an amount produced by nearly 360,000 cars. Their environmental impact is significant despite industry claims about clean energy use and climate commitments, the lawmakers wrote.\n"
                 }
                 )
            ]
        )
    )
