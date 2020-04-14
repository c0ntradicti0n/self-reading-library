# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/3 7:15 下午
# @Author: wuchenglong
import numpy
import pandas
import tensorflow as tf
import tensorflow_addons as tf_ad

import numpy as np
from tensorflow_core.python.keras.layers import TimeDistributed, Dense, Bidirectional, LSTM, Dropout, GRU
from tf2crf import CRF


def get_precomputed_features(feature_data, cols_to_use):
    embedding_matrix = feature_data[cols_to_use].to_numpy()
    return embedding_matrix


class LayoutModel(tf.keras.Model):
    def __init__(self, hidden_num, data, cols_to_use, embedding_size, pad_label=0, name=None):
        super(LayoutModel, self).__init__(name=name)

        self.num_hidden = hidden_num
        self.PAD_LABEL = pad_label
        self.vocab_size = len(data)

        self.label_size = len(data['column_labels'].unique())
        self.transition_params = None

        self.embedding_matrix = get_precomputed_features(data, cols_to_use=cols_to_use)

        self.embedding = tf.keras.layers.Embedding(self.vocab_size, embedding_size,
                  weights=[self.embedding_matrix],
                  input_length=self.vocab_size,
                  trainable=False)

        self.biLSTM1 = Bidirectional(LSTM(hidden_num, return_sequences=True, trainable=True),   trainable=True)
        self.biLSTM2 = Bidirectional(LSTM(hidden_num, return_sequences=True, trainable=True),   trainable=True)
        self.biLSTM3 = Bidirectional(LSTM(hidden_num, return_sequences=True, trainable=True),   trainable=True)

        self.gru = Bidirectional(GRU(64, return_sequences=True))

        self.dropout = Dropout(0.3)

        #self.cnn_layer = tf.keras.layers.Conv1D(
        #    filters=100,
        #    kernel_size=4,
        #    # Use 'same' padding so outputs have the same shape as inputs.
        #    padding='same')

        self.timedistributed = TimeDistributed(Dense(1700, activation="sigmoid"))

        self.dense2 = tf.keras.layers.Dense(1700, trainable=True,  activation = 'sigmoid')

        self.crf = CRF(self.label_size,trainable=True)


        self.dense51 = tf.keras.layers.Dense(self.label_size, trainable=True, activation="selu")
        self.dense52 = tf.keras.layers.Dense(self.label_size, trainable=True, activation="selu")
        self.dense53 = tf.keras.layers.Dense(self.label_size, trainable=True, activation="selu")
        self.dense54 = tf.keras.layers.Dense(self.label_size, trainable=True, activation="selu")
        self.dense55 = tf.keras.layers.Dense(self.label_size, trainable=True, activation="selu")
        self.dense56 = tf.keras.layers.Dense(self.label_size, trainable=True, activation="selu")
        self.dense57 = tf.keras.layers.Dense(self.label_size, trainable=True, activation="selu")




        #self.transition_params = tf.Variable(tf.random.uniform(shape=(self.label_size, self.label_size)),
        #                                     trainable=False)

        self.dropout = tf.keras.layers.Dropout(0)

    @tf.function
    def call(self, text,labels=None,training=None, precomputed=False):
        text_lens = tf.math.reduce_sum(tf.cast(tf.math.not_equal(text, 0), dtype=tf.int32), axis=-1)
        # -1 change 0        #try:
        text_lens = tf.constant(text.shape[0] *[text.shape[1]], dtype=tf.int32)
        #except:
        #    raise
        # -1 change 0

        if not precomputed:
            inputs = self.embedding(text)
        else:
            raise NotImplementedError

        #inputs = self.cnn_layer(inputs)
        #inputs = tf.keras.layers.Attention(ac)(
        #    [inputs, inputs])
        #inputs = tf.keras.layers.Attention(32, 3, activation='relu')(inputs)
        #inputs = tf.keras.layers.MaxPooling1D(3)(inputs)
        #inputs = self.biLSTM1(inputs) # self.crf3(self.crf4(self.crf1(self.crf2(inputs))))
        #inputs = self.biLSTM2(inputs) # self.crf3(self.crf4(self.crf1(self.crf2(inputs))))
        #inputs = self.biLSTM3(inputs) # self.crf3(self.crf4(self.crf1(self.crf2(inputs))))
        #inputs = self.timedistributed(inputs) # self.crf3(self.crf4(self.crf1(self.crf2(inputs))))
        #inputs = self.timedistributed(inputs)
        logits = self.crf(self.dense51(
            self.dense52(
                self.dense53(
                    self.dense54(
                        self.dense55(
                            self.dense56(
                                self.dense57(inputs,training=training),training=training),training=training),training=training),training=training),training=training)))

        #logits = inputs #self.crf(self.dense57(self.gru(inputs)))

        if labels is not None:

            return logits, text_lens
        else:
            return logits, text_lens

