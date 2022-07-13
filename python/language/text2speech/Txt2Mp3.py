import os
from pprint import pprint

from ant import Ant
from core import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import cache_flow

import torchaudio
from speechbrain.pretrained import Tacotron2
from speechbrain.pretrained import HIFIGAN

# Intialize TTS (tacotron2) and Vocoder (HiFIGAN)
tacotron2 = Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech", savedir="tmpdir_tts")
hifi_gan = HIFIGAN.from_hparams(source="speechbrain/tts-hifigan-ljspeech", savedir="tmpdir_vocoder")


@converter('reading_order.page', 'mp3')
class Txt2Mp3(Ant):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, cached=cache_flow.iterate, **kwargs)
        self.n = n
        self.debug = debug

    def __call__(self, iterator, *args, **kwargs):
        for id, meta in iterator:
            text = meta["text"]
            path = meta["html_path"]
            audio_path = f'{path}.{config.audio_format}'

            # Running the TTS
            mel_output, mel_length, alignment = tacotron2.encode_text(text)

            # Running Vocoder (spectrogram-to-waveform)
            waveforms = hifi_gan.decode_batch(mel_output)

            # Save the waverform
            torchaudio.save(audio_path, waveforms.squeeze(1), 22050)

            yield



if __name__ == "__main__":
    from core.pathant.PathAnt import PathAnt
    from layout.model_helpers import find_best_model
    from helpers.list_tools import metaize

    ant = PathAnt()
    print (ant.graph())
    model_path = model_pat=find_best_model()[0]
    pipe = ant("pdf", "mp3")
    res = list(pipe(metaize(["./../test/glue.pdf"]), model_path=model_path))
    pprint(res)
    os.popen(f"mplayer {res[0][0]}").read()




