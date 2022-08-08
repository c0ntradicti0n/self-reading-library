# bash

sudo apt-get install wkhtmltopdf
pip install setuptools==57.5.0
sudo apt-get install  libgraphviz-dev
git clone https://github.com/c0ntradicti0n/pdf2htmlEX-1.git
cd pdf2htmlEX-1
. ./buildScripts/buildInstallLocallyApt
sudo apt-get install chromium-browser chromium-browser-l10n chromium-codecs-ffmpeg

curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

sudo apt-get install --reinstall libpq-dev

git clone https://github.com/c0ntradicti0n/tts.git
cd tts
python -m venv venv
. venv/bin/activate
pip install -r tts/requirements.txt
cd ..
cd python/.layouteagle/elmo_difference_models/
wget https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_weights.hdf5
wget https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_options.json
sudo apt-get install oggvideotools