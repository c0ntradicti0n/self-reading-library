# syntax=docker/dockerfile:1
FROM ubuntu:20.04

RUN apt update && apt-get --yes upgrade
RUN apt --yes install git
RUN apt-get  --yes install sudo
RUN git clone https://github.com/c0ntradicti0n/pdf2htmlEX-1.git
RUN cd pdf2htmlEX-1
RUN ls
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata

RUN cd pdf2htmlEX-1 && ./buildScripts/buildInstallLocallyApt
RUN cd pdf2htmlEX-1 &&  ./buildScripts/getFontforge
RUN cd pdf2htmlEX-1 &&  ./buildScripts/buildFontforge
RUN cd pdf2htmlEX-1 &&  ./buildScripts/getPoppler
RUN cd pdf2htmlEX-1 &&  ./buildScripts/buildPoppler
RUN cd pdf2htmlEX-1 && git checkout zwordi
RUN cd pdf2htmlEX-1 && ls && ./buildScripts/buildPdf2htmlEX


RUN apt --yes  install texlive-full
RUN apt-get --yes install python3-venv
RUN apt  --yes install python3-pip
RUN git clone https://github.com/c0ntradicti0n/LayoutEagle.git
RUN python3 -m venv venv
RUN . venv/bin/activate

RUN cd LayoutEagle/python && pip install -r requirements.txt