FROM python:3.9
WORKDIR /
ARG CONTEXT
ARG OUTSIDE_CONTEXT

ENV CONTEXT=$CONTEXT
ENV OUTSIDE_CONTEXT=$OUTSIDE_CONTEXT
RUN git clone https://github.com/antimatter15/alpaca.cpp
RUN ls -a
WORKDIR /alpaca.cpp

RUN make
WORKDIR /
COPY $OUTSIDE_CONTEXT/requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . ./
