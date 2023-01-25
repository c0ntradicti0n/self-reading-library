FROM python:3.9
RUN apt update
RUN apt upgrade -y
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y install tzdata
RUN apt install python3.9 -y
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3
RUN apt install python3-pip -y
RUN apt install git -y
RUN apt install libpq-dev -y
RUN apt install wget -y
RUN apt install --reinstall libpq-dev -y
RUN apt install libgraphviz-dev -y
RUN apt install python3.9-distutils -y
RUN apt install python3.9-dev -y
RUN apt install libfreetype6-dev pkg-config pkg-config -y
RUN apt-get -y update
RUN apt -y install librsvg2-bin
WORKDIR /home/finn/Programming/self-reading-library
RUN pip3 install torch torchvision torchaudio
RUN pip install transformers==4.25.1
RUN --mount=type=cache,target=/root/.cache/pip pip install setuptools==57.5.0
RUN --mount=type=cache,target=/root/.cache/pip pip install spacy spacy-transformers
RUN --mount=type=cache,target=/root/.cache/pip python3 -m spacy download en_core_web_trf
RUN --mount=type=cache,target=/root/.cache/pip python3 -m spacy download en_core_web_md
RUN --mount=type=cache,target=/root/.cache/pip python3 -m spacy download en_core_web_sm
RUN --mount=type=cache,target=/root/.cache/pip pip install git+https://github.com/facebookresearch/detectron2.git
RUN --mount=type=cache,target=/root/.cache/pip pip install uvicorn[standard]
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt --use-deprecated=legacy-resolver
RUN pip3 install torch torchvision torchaudio
RUN mkdir /.allennlp  && mkdir /.allennlp/cache  && chmod -R 777 /.allennlp
RUN mkdir /nltk_data  && chmod -R 777 /nltk_data
RUN  apt-get -y install gcc-4.9
RUN  apt-get -y upgrade libstdc++6
RUN mkdir /.local  && chmod -R 777 /.local
RUN ls
COPY tokenization_layoutvm2_fast.py /usr/local/lib/python3.9/dist-packages/transformers/models/layoutlmv2/tokenization_layoutlmv2_fast.py
WORKDIR /home/finn/Programming/self-reading-library/python

