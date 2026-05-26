FROM docker.io/c0ntradiction/pdf2htmlex
RUN echo cool
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y software-properties-common tzdata
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update
RUN apt-get install -y python3.9 python3.9-distutils python3.9-dev
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3
# Install pip specifically for python3.9 and wire up pip/pip3 symlinks
RUN apt-get install -y curl git libpq-dev wget
RUN curl -sS https://bootstrap.pypa.io/pip/3.9/get-pip.py | python3.9
RUN ln -sf /usr/local/bin/pip3.9 /usr/local/bin/pip \
 && ln -sf /usr/local/bin/pip3.9 /usr/local/bin/pip3
RUN wget https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_weights.hdf5
RUN wget https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_options.json
RUN apt-get install -y oggvideotools libpq-dev libgraphviz-dev libfreetype6-dev pkg-config poppler-utils
RUN apt install -y pandoc texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra texlive-xetex
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable
RUN apt -y install language-pack-en
RUN apt -y install librsvg2-bin
RUN apt -y install moreutils

RUN apt update

# install chromedriver
RUN apt-get install -y unzip curl

# Install Chrome WebDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    curl -sS -o /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver && \
    ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver /usr/local/bin/chromedriver

# set display port to avoid crash
ENV DISPLAY=:99

RUN   >&2 echo "$(python3 --version)"
WORKDIR /home/finn/Programming/self-reading-library

RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install transformers==4.25.1
RUN --mount=type=cache,target=/root/.cache/pip pip install setuptools==57.5.0
RUN --mount=type=cache,target=/root/.cache/pip pip install "spacy==3.7.5" "spacy-transformers==1.3.5"
RUN --mount=type=cache,target=/root/.cache/pip python3 -m spacy download en_core_web_trf
RUN --mount=type=cache,target=/root/.cache/pip python3 -m spacy download en_core_web_md
RUN --mount=type=cache,target=/root/.cache/pip python3 -m spacy download en_core_web_sm
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-build-isolation git+https://github.com/facebookresearch/detectron2.git
RUN --mount=type=cache,target=/root/.cache/pip pip install uvicorn[standard]
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-build-isolation -r requirements.txt --use-deprecated=legacy-resolver
RUN pip install weasyprint
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb
RUN apt -y install ./wkhtmltox_0.12.6-1.focal_amd64.deb || (apt-get install -f -y && apt -y install ./wkhtmltox_0.12.6-1.focal_amd64.deb)



RUN apt update && apt install  openssh-server  -y

RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -u 123 test

RUN  echo 'test:test' | chpasswd

RUN service ssh start


# COPY . python

RUN mkdir /.allennlp  && mkdir /.allennlp/cache  && chmod -R 777 /.allennlp
RUN mkdir /nltk_data  && chmod -R 777 /nltk_data
RUN mkdir /.local  && chmod -R 777 /.local
RUN ls

RUN python3 -c 'import nltk; nltk.download("wordnet"); nltk.download("omw-1.4")'
RUN python3 -c 'from transformers import pipeline; pipeline("summarization")'

COPY tokenization_layoutvm2_fast.py /usr/local/lib/python3.9/dist-packages/transformers/models/layoutlmv2/tokenization_layoutlmv2_fast.py

RUN pip install gevent
RUN apt install -y jq
RUN apt install graphviz  -y
RUN apt install graphviz-dev  -y
RUN pip install pygad
COPY config/default.latex  /usr/share/pandoc/data/templates/default.latex
WORKDIR /home/finn/Programming/self-reading-library/python

EXPOSE 22

ARG USER=go
ARG PASS=go

RUN adduser $USER && echo "$USER:$PASS" | chpasswd

RUN chmod -R 777  /etc/ssh/