# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/3 7:15 下午
# @Author: wuchenglong
import pandas
import tensorflow as tf
import tensorflow_addons as tf_ad

import numpy as np


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

        self.biLSTM1 = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(hidden_num, return_sequences=True))
        self.biLSTM2 = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(hidden_num, return_sequences=True))
        self.biLSTM3 = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(hidden_num, return_sequences=True))
        self.biLSTM4 = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(hidden_num, return_sequences=True))
        self.biLSTM5 = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(hidden_num, return_sequences=True))

        self.dense1 = tf.keras.layers.Dense(hidden_num)
        self.dense2 = tf.keras.layers.Dense(hidden_num)
        self.dense3 = tf.keras.layers.Dense(hidden_num)
        self.dense4 = tf.keras.layers.Dense(hidden_num)
        self.dense5 = tf.keras.layers.Dense(self.label_size)

        self.transition_params = tf.Variable(tf.random.uniform(shape=(self.label_size, self.label_size)),
                                             trainable=False)

        self.dropout = tf.keras.layers.Dropout(0)

    # @tf.function
    def call(self, text,labels=None,training=None, precomputed=False):
        #text_lens = tf.math.reduce_sum(tf.cast(tf.math.not_equal(text, self.PAD_LABEL), dtype=tf.int32), axis=-1)
        try:
            text_lens = tf.constant(text.shape[0] *[text.shape[1]], dtype=tf.int32)
        except:
            raise
        # -1 change 0

        if not precomputed:
            inputs = self.embedding(text)
        else:
            raise NotImplementedError

        inputs = self.dropout(inputs, training)
        inputs = self.dense1(self.biLSTM1(inputs))
        inputs = self.dense2(self.biLSTM2(inputs))
        inputs = self.dense3(self.dense4(inputs))

        logits = self.dense5(inputs)

        if labels is not None:
            label_sequences = tf.convert_to_tensor(labels, dtype=tf.int32)
            log_likelihood, self.transition_params = tf_ad.text.crf_log_likelihood(logits, label_sequences, text_lens)
            self.transition_params = tf.Variable(self.transition_params, trainable=False)
            return logits, text_lens, log_likelihood
        else:
            return logits, text_lens

