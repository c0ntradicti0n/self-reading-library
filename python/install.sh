sudo apt-get install libopenjp2-7-dev

wget https://poppler.freedesktop.org/poppler-0.89.0.tar.xz

tar -xf poppler-0.89.0.tar.xz

cd poppler-0.89.0/
mkdir build
cd build
cmake ..
make
sudo make install
cd ../../../

sudo apt-get install gettext

git clone https://github.com/fontforge/fontforge.git
sudo apt-get install libjpeg-dev libtiff5-dev libpng-dev libfreetype6-dev libgif-dev libgtk-3-dev libxml2-dev libpango1.0-dev libcairo2-dev libspiro-dev libuninameslist-dev python3-dev ninja-build cmake build-essential
cd fontforge
mkdir build
cd build

cmake ..
make
sudo make install

cd ../../

git clone https://github.com/pdf2htmlEX/pdf2htmlEX.git
cd pdf2htmlEX

cp -r ../fontforge/fontforge/*.* ../../pdf2htmlEX/src/
cp -r ../../fontforge/build/inc/*.* ../../pdf2htmlEX/src
