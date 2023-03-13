import argparse
import concurrent
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("out", type=str, help="name of output_file")
parser.add_argument(
    "-i", "--input_file", nargs="?", type=str, help="name of input file"
)

parser.add_argument(
    "-t",
    "--tmp_dir",
    nargs="?",
    type=str,
    default="/tmp/",
    help="directory for temporary files",
)
args = parser.parse_args()
print(args)

import os
import sys
import logging

import torchaudio
from speechbrain.pretrained import Tacotron2
from speechbrain.pretrained import HIFIGAN

from sentence_split import split_into_sentences

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

tacotron2 = Tacotron2.from_hparams(
    source="speechbrain/tts-tacotron2-ljspeech", savedir="tmpdir_tts"
)
hifi_gan = HIFIGAN.from_hparams(
    source="speechbrain/tts-hifigan-ljspeech", savedir="tmpdir_vocoder"
)


def i_path(j, i, path):
    return args.tmp_dir + f"{j}_{i}_{os.path.basename(path)}.ogg"


def source():
    if not args.input_file:
        for line in sys.stdin:
            yield line
    else:
        with open(args.input_file) as f:
            yield from f.readlines()


created_temp_files = []


def generate_audio_clip(audio_path, sentence, i):
    global created_temp_files, alignment, e
    try:
        # Running the TTS
        mel_output, mel_length, alignment = tacotron2.encode_text(sentence)

        # Running Vocoder (spectrogram-to-waveform)
        waveforms = hifi_gan.decode_batch(mel_output)

        # Save the waverform
        torchaudio.save(audio_path, waveforms.squeeze(1), 22050)

        created_temp_files.append((i, audio_path))
        logging.info(f"processed item {i} {len(sentence)=}: {sentence=}  ")
    except Exception as e:
        logging.error(
            f"Error at item {i} {len(sentence)=}: {sentence=} ", exc_info=True
        )


threads = []
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    for i_line, line in enumerate(source()):
        sentences = split_into_sentences(line)
        for i_sentence, sentence in enumerate(sentences):
            audio_path = i_path(i_line, i_sentence, args.out)

            threads.append(
                executor.submit(
                    generate_audio_clip, audio_path, sentence, (i_line, i_sentence)
                )
            )

    for thread in threads:
        thread.result()

out_path = args.out.replace(".ogg", "") + ".ogg"

print(created_temp_files)
created_temp_files = [
    val
    for i, val in list(
        sorted(
            created_temp_files, key=lambda i_path: (i_path[0][0] * 1000) + i_path[0][1]
        )
    )
]
logging.info(f"writing result to {out_path}")
os.system(f"oggCat -x {os.path.basename(out_path)}  {' '.join(created_temp_files)}")
if not out_path == os.path.basename(out_path):
    os.system(f"mv {os.path.basename(out_path)} {out_path}")
os.system(f"rm  -f   {' '.join(created_temp_files)}")
