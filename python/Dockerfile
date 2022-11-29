FROM docker.io/c0ntradiction/pdf2htmlex

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
RUN apt install poppler-utils -y
RUN apt install -y pandoc texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra

RUN   >&2 echo "$(python3 --version)"
WORKDIR /home/finn/Programming/self-reading-library


RUN --mount=type=cache,target=/root/.cache/pip pip install setuptools==57.5.0
RUN --mount=type=cache,target=/root/.cache/pip pip install torch==1.10.2 spacy spacy-transformers
RUN --mount=type=cache,target=/root/.cache/pip python3 -m spacy download en_core_web_trf
RUN --mount=type=cache,target=/root/.cache/pip python3 -m spacy download en_core_web_md
RUN --mount=type=cache,target=/root/.cache/pip python3 -m spacy download en_core_web_sm
RUN --mount=type=cache,target=/root/.cache/pip pip install git+https://github.com/facebookresearch/detectron2.git
RUN --mount=type=cache,target=/root/.cache/pip pip install uvicorn[standard]

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt --use-deprecated=legacy-resolver
RUN pip3 install torch-1.12.1-cpu torchvision==1.12.1+cpu torchaudio==1.12.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

RUN apt update && apt install  openssh-server  -y

RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -u 123 test

RUN  echo 'test:test' | chpasswd

RUN service ssh start

EXPOSE 22

# COPY . python

RUN mkdir /.allennlp  && mkdir /.allennlp/cache  && chmod -R 777 /.allennlp
RUN mkdir /nltk_data  && chmod -R 777 /nltk_data

RUN ls

RUN python3 -c 'import nltk; nltk.download("wordnet"); nltk.download("omw-1.4")'
RUN pip install dash==2.3.0 dash-extensions visdcc werkzeug==2.0.3
#RUN cp python/tokenization_layoutvm2_fast.py ../venv/lib/python3.9/site-packages/transformers/models/layoutlmv2/tokenization_layoutlmv2_fast.py

WORKDIR /home/finn/Programming/self-reading-library/python

