# Simple Text To Speech on command line

Using some modern TTS package with simple use in  sh.

At the moment:

* tacotron2, wave-form with speechbrain. it predicts spectograms and then waveforms from them. 

Text input must be chunked for that into sentences producing single soundfiles, that are concatenated finally.

## Installation
``` sh 
git clone git@github.com:c0ntradicti0n/text2speech.git
cd text2speech
python -m venv venv
. activate /venv/bin/activate
pip install -r requirements.txt
```



### Requirements

* oggCat

for Ubuntu

``` sh
sudo apt-get install oggvideotools
```
## Usage

``` sh
python tts.py --help                                                                            3s  + ✱ ●  ~/P/text2speech 
usage: tts.py [-h] [-i [INPUT_FILE]] [-t [TMP_DIR]] out

Process some integers.

positional arguments:
  out                   name of output_file

optional arguments:
  -h, --help            show this help message and exit
  -i [INPUT_FILE], --input_file [INPUT_FILE]
                        name of input file
  -t [TMP_DIR], --tmp_dir [TMP_DIR]
                        directory for temporary files
```

Pipe or type the text into the script:

**It will create ogg-Files!**

``` sh
. activate /venv/bin/activate

cat test.txt | python tts.py out.ogg

```

Or with `-i`-Flag or `echo` or with pipin into `stdin`
