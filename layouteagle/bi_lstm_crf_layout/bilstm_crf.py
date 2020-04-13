import logging
import os
from types import GeneratorType

import numpy
import pandas
import tensorflow as tf
import tensorflow_addons as tf_ad
import tensorflow.keras.backend as K


from layouteagle.bi_lstm_crf_layout.model import LayoutModel
from layouteagle.helpers.list_tools import Lookup


def sorted_by_zipped(x):
    return list(_x[0] for _x in sorted(zip(*x), key=lambda __x:__x[1]))



class Bi_LSTM_CRF:
    def __init__(self, batch_size=50, hidden_num=950, lr=0.01,
                 embedding_size=9, epoch=160, max_divs_per_page=150,
                 output_dir="models/"):
        self.batch_size = batch_size
        self.hidden_num = embedding_size
        self.lr = lr
        self.embedding_size = embedding_size
        self.epoch = epoch
        self.output_dir = output_dir
        self.max_divs_per_page = max_divs_per_page


    def __call__(self, feature_path):
        os.system(f"rm -r {self.output_dir} & mkdir {self.output_dir}")
        if isinstance(feature_path, GeneratorType):

            feature_path = next(feature_path)
        self.prepare_from_pickle(feature_path)
        self.train()
        logging.info("finished")
        model_file_path = self.output_dir + 'model.ckpt'
        return model_file_path

    def prepare_from_pickle(self, feature_path):
        feature_df = pandas.read_pickle(feature_path)
        self.prepare(feature_df)

    def prepare(self, feature_df):

        # append padding features
        ml_data = pandas.DataFrame([[0] * len (feature_df.columns)], columns=feature_df.columns)
        self.PAD_FEATURE_INDEX = 0
        self.PAD_LABEL = "PAD"
        ml_data['column_labels'] = self.PAD_LABEL
        ml_data['page_number'] = -1
        ml_data['doc_id'] = 0
        feature_df = pandas.concat([ml_data, feature_df])

        feature_df.reset_index(drop=True, inplace=True)
        feature_df['index'] = feature_df.index

        in_page = feature_df[1:].groupby(["doc_id", "page_number"]).groups
        in_page = {grouper_tuple: group.tolist() for grouper_tuple, group in in_page.items() if len(group) < self.max_divs_per_page}
        cols_to_use = ["x", "y", "len", "height",  "page_number", "font-size", "fine_grained_pdf", "coarse_grained_pdf", "line-height", "chars", "nums", "signs"]

        distance_col_prefix = 'd_'
        max_distance = max([max(x) for x in feature_df[1:]['distance_vector']])
        max_distance = max([max(x) for x in feature_df[1:]['distance_vector']])
        feature_df.distance_vector = feature_df[1:].distance_vector.apply(lambda x:x/max_distance)
        feature_df.distance_vector = feature_df[1:].distance_vector.apply(lambda x: list(sorted(x)[:6]))
        feature_df = feature_df.assign(**feature_df.distance_vector.apply(pandas.Series).add_prefix(distance_col_prefix))
        feature_df = feature_df.fillna(1)

        angle_col_prefix = 'a_'
        max_angle = max([max(x) for x in feature_df[1:]['angle']])
        min_angle = min([min(x) for x in feature_df[1:]['angle']])

        #feature_df.angle = feature_df[1:].angle.apply(lambda x:(x+abs(min_angle))/(max_angle+abs(min_angle)))
        feature_df.angle = feature_df[1:].angle.apply(lambda x: list(x))
        feature_df['da'] = list(zip(feature_df["angle"] , feature_df["distance_vector"]))
        feature_df.angle = feature_df[1:]["da"].apply(lambda x: (sorted_by_zipped(x))[:6])
        feature_df = feature_df.assign(**feature_df.angle.apply(pandas.Series).add_prefix(angle_col_prefix))
        feature_df = feature_df.fillna(1)

        for col in cols_to_use:
            feature_df[col] = feature_df[col] / max(feature_df[col])

        cols_to_use += [col for col in feature_df.columns if col.startswith(distance_col_prefix) or col.startswith(angle_col_prefix)]

        # zip token ids and labels
        content_ids, labels = list(zip(*[(
            pp,
            feature_df.iloc[list(pp)]['column_labels'].tolist()) for pp in in_page.values()]))

        # PAD Tokens
        content_ids = tf.keras.preprocessing.sequence.pad_sequences(content_ids, padding='post', value=self.PAD_FEATURE_INDEX)

        self.label_lookup = Lookup([ml_data['column_labels'].tolist()] + list(labels))
        labels = self.label_lookup(token_s=labels)
        labels = tf.keras.preprocessing.sequence.pad_sequences(
            labels,
            padding='post',
            value=self.label_lookup.token_to_id[self.PAD_LABEL])

        self.train_dataset = tf.data.Dataset.from_tensor_slices((content_ids, labels))
        self.train_dataset = self.train_dataset.shuffle(
            len(feature_df['index']) - len(ml_data), reshuffle_each_iteration=True).batch(self.batch_size, drop_remainder=True,
                                                           )

        self.embedding_matrix = [feature_df.iloc[[sample for sample in samples]][cols_to_use] for samples in content_ids]

        int_to_one_hot  = ["reading_sequence", "page_number"]
        for col in cols_to_use:
            feature_df[col] = feature_df[col] / feature_df[col].max()


        logging.info(f"hidden_num:{self.hidden_num}, vocab_size:{len(feature_df['index'])}, label_size:{len(feature_df['column_labels'].unique())}, features: {len(cols_to_use)},"
                     f"{self.lr}")
        self.optimizer = tf.keras.optimizers.Adam(self.lr)

        self.model = LayoutModel(hidden_num=self.hidden_num,
                              data=feature_df,
                              cols_to_use=cols_to_use,
                              embedding_size=len(cols_to_use),
                              pad_label=self.PAD_FEATURE_INDEX)

        ckpt = tf.train.Checkpoint(optimizer=self.optimizer, model=self.model)
        ckpt.restore(tf.train.latest_checkpoint(self.output_dir))
        self.ckpt_manager = tf.train.CheckpointManager(ckpt,
                                                       self.output_dir,
                                                       checkpoint_name='model.ckpt',
                                                       max_to_keep=3)

    # @tf.function
    def train_one_step(self, text_batch, labels_batch):
        with tf.GradientTape() as tape:
            logits, text_lens = self.model(text_batch, labels_batch, training=True)
            loss = self.model.crf.loss(labels_batch, logits)
        gradients = tape.gradient(loss, self.model.trainable_variables, unconnected_gradients='zero')
        self.optimizer = tf.keras.optimizers.Adam(self.lr)
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
        return loss, logits, text_lens

    def get_acc_one_step(self, logits, text_lens, labels_batch):
        paths = []
        accuracies = []
        for logit, text_len, labels in zip(logits, text_lens, labels_batch):
            paths.append(logit)
            correct_prediction = correct_prediction = tf.equal(logit, labels)
            accuracies.append(tf.reduce_mean(tf.cast(correct_prediction, tf.float32)))
        accuracy = sum(numpy.array(accuracies) / len(paths))
        return accuracy

    best_name = "bestmodel"
    def train(self):
        best_acc = 0
        step = 0
        best_loss = 10000


        for epoch in range(self.epoch):
            dataset = list(enumerate(self.train_dataset))
            for _, (text_batch, labels_batch) in dataset:

                step = step + 1
                loss, logits, text_lens = self.train_one_step(text_batch, labels_batch)

                accuracy = self.model.crf.accuracy(labels_batch, logits)
                logging.info(f'epoch {epoch}, step {step}/{len(dataset)}, '
                                f'loss {loss}, accuracy {accuracy}, lr {self.lr}')

                if True and  accuracy > best_acc and step>10:
                    best_loss = loss
                    best_acc = accuracy

                    logits = K.argmax(logits, axis=-1)
                    unique_labels = set(logits[0].numpy().tolist())
                    logging.info(
                        f"\n{logits[0].numpy().tolist()} | \n"
                        f"{labels_batch[0]} \n"
                        f"{dict(zip(unique_labels, self.label_lookup.ids_to_tokens(unique_labels)))}")
                    #tf.saved_model.save(self.model, self.output_dir + self.best_name)
                    logging.warning("Saved best model up to now")

    def predict(self, features):
        self.prepare(features)
        dataset = list(enumerate(self.train_dataset))
        for _, (text_batch, labels_batch) in dataset:
            logits, text_lens = self.model.predict(dataset)
            paths = []
            for logit, text_len in zip(logits, text_lens):
                viterbi_path, _ = tf_ad.text.viterbi_decode(logit[:text_len], model.transition_params)
                paths.append(viterbi_path)
            print(paths[0])
            print([self.label_lookup[id] for id in paths[0]])

    def load(self):
        self.model = tf.saved_model.load(
            self.output_dir + self.best_name, tags=None
        )
