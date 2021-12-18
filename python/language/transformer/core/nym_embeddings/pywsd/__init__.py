#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD)
#
# Copyright (C) 2014-2020 alvations
# URL:
# For license information, see LICENSE.md

from __future__ import absolute_import, print_function

import sys
import time

from wn import WordNet
from wn.constants import wordnet_30_dir

__builtins__['wn'] = WordNet(wordnet_30_dir)

__version__ = '1.2.3'

# Warm up the library.
print('Warming up PyWSD (takes ~10 secs)...', end=' ', file=sys.stderr, flush=True)
start = time.time()

import nym_embeddings.pywsd.lesk

#import semcor
#import semeval

#nym_embeddings.pywsd.lesk.simple_lesk('This is a foo bar sentence', 'bar')
#print('took {} secs.'.format(time.time()-start), file=sys.stderr)
