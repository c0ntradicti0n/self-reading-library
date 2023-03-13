#!/bin/sh

rm -r ./$2
allennlp train \
  $1 -s ./$2/

