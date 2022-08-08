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