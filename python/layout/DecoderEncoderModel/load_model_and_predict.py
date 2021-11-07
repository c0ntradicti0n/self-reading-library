
import pickle

import numpy as np

import os

import pandas
from helpers.list_tools import Lookup
from layouteagle import config
from tensorflow.python.keras.utils.np_utils import to_categorical

os.environ["LD_LIBRARY_PATH"] ='/usr/local/cuda-11.0/targets/x86_64-linux/lib/'

from helpers.dataset_tools import tf_lower_and_split_punct, pad
from layout.DecoderEncoderModel.BahdanauAttention import BahdanauAttention, plot_attention
from layout.DecoderEncoderModel.BatchLogs import BatchLogs
from layout.DecoderEncoderModel.Decoder import Decoder, DecoderInput
from layout.DecoderEncoderModel.Encoder import Encoder
from layout.DecoderEncoderModel.MaskedLoss import MaskedLoss
from layout.DecoderEncoderModel.TrainTranslator import TrainTranslator
from layout.DecoderEncoderModel.Translator import Translator
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint
from helpers.dataset_tools import tf_lower_and_split_punct, pad, split_dataset

from tf_import import *


from tensorflow.keras.layers.experimental import preprocessing
import tensorflow_text as tf_text


feature_df = pandas.read_pickle('/home/finn/PycharmProjects/LayoutEagle/python/.layouteagle/labeled_features.pickle')

feature_df = feature_df.head((int(len(feature_df) / 2)))

BUFFER_SIZE = feature_df
BATCH_SIZE = 64
_PAD = "PAD"
MODEL_NAME = 'layout_translator'

import matplotlib.pyplot as plt

use_builtins = True

# Download the file
import pathlib


def prepare_row(feature_row, training=True):
    scalar_values = np.array(feature_row[config.cols_to_use], dtype=np.float64)
    if config.array_cols_to_use:
        array_values = np.hstack(
            [col.flatten() for col in feature_row[config.array_cols_to_use]]
        )

    return np.hstack([scalar_values] + ([array_values] if config.array_cols_to_use else []))


label_set = list(set(feature_df['LABEL'].tolist())) + [_PAD]
label_lookup = Lookup([label_set])
PAD = label_lookup.token_to_id[_PAD]
feature_df['LABEL'] = label_lookup(token_s=feature_df.LABEL.tolist())
PAD_WIDTH = None


def feature_generator():
    global PAD_WIDTH
    page_groups = feature_df.groupby(['page_number', "doc_id"])
    max_len = len(max(page_groups, key=lambda x: len(x[1]))[1]) + 1
    PAD_WIDTH = max_len
    for grouper, page in page_groups:
        x = []
        y = []
        for ((idx, row)) in page.iterrows():
            unpacked_row = prepare_row(row)

            x.append(unpacked_row)
            y.append(row.LABEL)

        x = pad(np.array(x), (max_len, 10), [0, 0])
        # print (x.shape)
        # print (x)

        y = pad(np.array(y), (max_len,), [0], value=PAD, dtype=object).tolist()
        # print (y.shape)

        yield tf.constant(x, dtype=tf.float64), tf.constant(y, dtype=tf.int64)


print(next((d for d in feature_generator())))
assert (PAD_WIDTH)

dataset = tf.data.Dataset.from_generator(
    feature_generator,
    # tf 2.3.0
    output_types=(tf.float64, tf.int64),
    output_shapes=(
        (PAD_WIDTH, 10),
        (PAD_WIDTH,)
    )
    # tf 2.5.0
    # output_signature=(
    #    tf.TensorSpec(shape=(next(feature_generator())[0].__len__(),), dtype=tf.float64),
    #    tf.TensorSpec(shape=(self.train_kwargs['num_layout_labels'],), dtype=tf.float64))
)
train_dataset, validation_dataset, test_dataset = split_dataset(dataset, len(feature_df.groupby(['page_number', "doc_id"])), 0.2, 0.2)


dataset = dataset.batch(BATCH_SIZE)


EPOCHS = 10
es = EarlyStopping(
    monitor='val_accuracy',
    mode='min',
    verbose=1,
    patience=int(EPOCHS / 4)
)
mc = ModelCheckpoint(
    "translator",
    monitor='val_accuracy',
    save_best_only=True,
    save_weights_only=False,
    verbose=1
)

for example_input_batch, example_target_batch in dataset.take(4):
    print(example_input_batch[:5])
    print()
    print(example_target_batch[:5])

reloaded = tf.saved_model.load('layout_translator')
result = reloaded.tf_translate(example_input_batch)

esult = reloaded.tf_translate(example_input_batch)

for tr in result['text']:
  print(tr.numpy().decode())

print()