FROM  c0ntradicti0n/pdf2htmlex:0.18.8.rc2-x-tag-feature-file-css-20220911-ubuntu-22.04-x86_64
RUN apt update
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y install tzdata
RUN apt install python3.9 -y
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3
RUN apt install python3-pip -y
RUN apt install git -y
RUN apt install libpq-dev -y
RUN apt install wget -y
RUN wget https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_weights.hdf5
RUN wget https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_options.json
RUN apt install oggvideotools -y
RUN apt install --reinstall libpq-dev -y
RUN apt install libgraphviz-dev -y
RUN apt install python3.9-distutils -y
RUN apt install python3.9-dev -y
RUN apt install libfreetype6-dev pkg-config pkg-config -y


RUN   >&2 echo "$(python3 --version)"
WORKDIR /home/finn/Programming/self-reading-library

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip pip install setuptools==57.5.0
RUN --mount=type=cache,target=/root/.cache/pip pip install torch
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt --use-deprecated=legacy-resolver
RUN --mount=type=cache,target=/root/.cache/pip python3 -m spacy download en_core_web_trf
RUN --mount=type=cache,target=/root/.cache/pip python3 -m spacy download en_core_web_md

COPY . .
ENTRYPOINT uwsgi --http 0.0.0.0:9999 --module wsgi:application --memory-report  --workers 16 --threads 2  --memory-report --enable-threads --skip-atexit-teardown --max-worker-lifetime=300 --max-worker-lifetime-delta=320 --harakiri=500

