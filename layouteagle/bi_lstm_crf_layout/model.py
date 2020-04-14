# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/3 7:15 下午
# @Author: wuchenglong
import numpy
import pandas
import tensorflow as tf
import tensorflow_addons as tf_ad

import numpy as np
from tensorflow_core.python.keras.layers import TimeDistributed, Dense, Bidirectional, LSTM
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

        self.dropout = self.Dropout(0.3)

        #self.cnn_layer = tf.keras.layers.Conv1D(
        #    filters=100,
        #    kernel_size=4,
        #    # Use 'same' padding so outputs have the same shape as inputs.
        #    padding='same')

        self.timedistributed = TimeDistributed(Dense(self.label_size, activation="relu"))

        self.dense2 = tf.keras.layers.Dense(17, trainable=True,  activation = 'softmax')

        self.crf = CRF(trainable=True)

        self.dense5 = tf.keras.layers.Dense(self.label_size, trainable=True)



        #self.transition_params = tf.Variable(tf.random.uniform(shape=(self.label_size, self.label_size)),
        #                                     trainable=False)

        self.dropout = tf.keras.layers.Dropout(0)

    # @tf.function
    def call(self, text,labels=None,training=None, precomputed=False):
        #text_lens = tf.math.reduce_sum(tf.cast(tf.math.not_equal(text, self.PAD_LABEL), dtype=tf.int32), axis=-1)
        #try:
        text_lens = tf.constant(text.shape[0] *[text.shape[1]], dtype=tf.int32)
        #except:
        #    raise
        # -1 change 0

        if not precomputed:
            inputs = self.embedding(text)
        else:
            raise NotImplementedError

        inputs = self.dropout(inputs, training)
        #inputs = self.cnn_layer(inputs)
        #inputs = tf.keras.layers.Attention(ac)(
        #    [inputs, inputs])
        #inputs = tf.keras.layers.Attention(32, 3, activation='relu')(inputs)
        #inputs = tf.keras.layers.MaxPooling1D(3)(inputs)
        #inputs = self.biLSTM1(inputs) # self.crf3(self.crf4(self.crf1(self.crf2(inputs))))
        #inputs = self.biLSTM2(inputs) # self.crf3(self.crf4(self.crf1(self.crf2(inputs))))
        #inputs = self.biLSTM3(inputs) # self.crf3(self.crf4(self.crf1(self.crf2(inputs))))
        #inputs = self.timedistributed(inputs) # self.crf3(self.crf4(self.crf1(self.crf2(inputs))))

        logits = self.crf(self.dense5(inputs))

        if labels is not None:

            return logits, text_lens
        else:
            return logits, text_lens

