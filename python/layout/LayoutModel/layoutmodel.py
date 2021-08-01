import itertools
import os
import pickle
from typing import Dict
import joblib
import pandas
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Normalizer
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.python.keras.utils.np_utils import to_categorical
import logging
import pprint
import more_itertools

from helpers.list_tools import Lookup, sorted_by_zipped
from helpers.pandas_tools import unpack_list_column
from layouteagle import config
from layouteagle.pathant.PathSpec import PathSpec
from helpers.nested_dict_tools import flatten


class LayoutModeler(PathSpec):
    train_kwargs = {
        **{f'dense1_{i}': {'units': 256,
                   'trainable': True,
                   'activation': 'relu',
                   'dtype': 'float64'} for i in range(0, 4)},
        **{f'dense2_{i}': {'units': 256,
                          'trainable': True,
                          'activation': 'relu',
                          'dtype': 'float64'} for i in range(0, 4)},
        'denseE': { # 'units' are set by us self to the necessary value
                   'trainable': True,
                   'activation': 'softmax',
                   'dtype': 'float64'},
        'adam': {'lr': 0.0003},
        'epochs':7,
        'batch_size': 3200,
        'patience': 3,
        'labels': 'layoutlabel',
        'cols_to_use': config.cols_to_use
    }

    def __init__(self,
                 *args,
                 override_train_kwargs: Dict = {},
                 model_path=config.layout_model_path,
                 debug: bool = True, **kwargs):
        super().__init__(*args, **kwargs)

        if not model_path:
            raise ValueError("Please specify a path for saving and loading the model")

        self.model_path = model_path
        if not os.path.isdir(self.model_path):
            os.mkdir(self.model_path)

        self.lookup_path = config.hidden_folder + ".lookup.pickle"

        self.train_kwargs.update(override_train_kwargs)

        self.debug = debug

    def load_pandas_file(self, feature_path):
        return pandas.read_pickle(feature_path)

    def prepare_features(self, feature_df, training=True):
        if training:
            self.label_set = list(set(feature_df['layoutlabel'].tolist()))
            self.label_lookup = Lookup([self.label_set])

            feature_df['layoutlabel'] = self.label_lookup(token_s=feature_df.layoutlabel.tolist())

        feature_df = self.prepare_df(feature_df, training=training)

        norm_cols = [col for col in self.cols_to_use if col != self.train_kwargs['labels']]

        """if training:
            scaler = Normalizer()
            scaler.fit(feature_df[norm_cols].to_numpy())
            joblib.dump(scaler, self.model_path + ".scaler")

            with open(self.lookup_path, "wb") as f:
                pickle.dump(self.label_lookup, f)
        else:
            scaler = joblib.load(self.model_path + ".scaler")

        feature_df[norm_cols] = scaler.transform(feature_df[norm_cols])"""

        feature_df = feature_df.fillna(0)

        if training:
            train, test = train_test_split(feature_df, test_size=0.2)
            train, val = train_test_split(train, test_size=0.2)
            self.logger.info(f'{len(train)} train samples')
            self.logger.info(f'{len(val)} validation samples')
            self.logger.info(f'{len(test)} test samples')

            self.train_ds = self.df_to_dataset(train, shuffle=False, batch_size=self.train_kwargs['batch_size'],
                                               training=training)
            self.val_ds = self.df_to_dataset(val, shuffle=False, batch_size=self.train_kwargs['batch_size'],
                                             training=training)
            self.test_ds = self.df_to_dataset(test, shuffle=False, batch_size=self.train_kwargs['batch_size'],
                                              training=training)
        else:
            self.predict_ds = self.df_to_dataset(feature_df, shuffle=False, batch_size=len(feature_df), training=False)

        feature_columns = []

        # remove the labels, that were put in the df temporarily
        self.cols_to_use = [col for col in self.cols_to_use if col != self.train_kwargs['labels']]

        # all are numeric cols
        for header in self.cols_to_use:
            feature_columns.append(tf.feature_column.numeric_column(header))

        as_numpy = feature_df[self.cols_to_use].to_numpy()
        return feature_columns, as_numpy

    # A utility method to create a tf.data dataset from a Pandas Dataframe
    def df_to_dataset(self, dataframe, shuffle=True, batch_size=None, training=True):
        dataframe = dataframe.copy()
        dataframe = dataframe.reset_index(drop=True)

        if training:
            labels = dataframe[self.train_kwargs['labels']].tolist()
            dataframe.pop(self.train_kwargs['labels'])
        else:
            labels = [0] * len(dataframe)

        categorical_labels = to_categorical(labels)

        try:
            ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), categorical_labels))
        except:
            raise
        if shuffle:
            ds = ds.shuffle(buffer_size=len(dataframe))

        ds = ds.batch(batch_size)

        return ds

    def prepare_df(self, feature_df, training=True):
        self.cols_to_use = self.train_kwargs['cols_to_use'] + [
            self.train_kwargs['labels']]  # ([self.train_kwargs['labels']] if training else [])

        feature_df = feature_df.reset_index(drop=True)

        N = 7

        max_distance = max([max(x) for x in feature_df['distance_vector']])
        feature_df.distance_vector = feature_df.distance_vector.apply(lambda x: x / max_distance)
        feature_df.distance_vector = feature_df.distance_vector.apply(lambda x: list(more_itertools.padded(list(sorted(x))[:N], 0, 8)))

        new_d_cols = unpack_list_column("distance_vector", feature_df, prefix='d_')

        feature_df = feature_df.fillna(1)

        feature_df.angle = feature_df.angle.apply(lambda x: list(x))
        feature_df['da'] = list(zip(feature_df['angle'], feature_df['distance_vector']))
        feature_df.angle = feature_df['da'].apply(lambda x: list(more_itertools.padded(list(sorted_by_zipped(x))[:N], 0, N)))

        new_a_cols = unpack_list_column("angle", feature_df, prefix='a_')

        feature_df = feature_df.fillna(1)
        with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
            self.logger.debug(str(feature_df.head()))

        new_xp_cols = unpack_list_column("x_profile", feature_df, prefix='xp_')
        new_yp__cols = unpack_list_column("y_profile", feature_df, prefix='yp_')

        self.cols_to_use = self.cols_to_use + new_d_cols + new_a_cols + new_xp_cols + new_yp__cols

        feature_df = feature_df[self.cols_to_use]

        return feature_df

    def train(self, feature_columns, override_kwargs={}):
        self.logger.info(f"Model will go to {self.model_path}")

        self.train_kwargs.update(override_kwargs)
        feature_layer = tf.keras.layers.DenseFeatures(feature_columns=feature_columns, dtype='float64')

        es = EarlyStopping(
            monitor='val_loss',
            mode='min', verbose=1,
            patience=self.train_kwargs['patience']
        )
        mcweights = ModelCheckpoint(self.model_path + "/model.h5",
                             monitor='val_accuracy',
                             save_best_only=True,
                             save_weights_only=False,
                             verbose=1)
        mcwhole = ModelCheckpoint(self.model_path,
                             monitor='val_accuracy',
                             save_best_only=True,
                             save_weights_only=False,
                             verbose=1)
        self.model = tf.keras.Sequential([
            feature_layer,

            *[tf.keras.layers.Dense(**v, use_bias=True) for k, v in self.train_kwargs.items() if "dense1_" in k],
            #tf.keras.layers.experimental.EinsumDense("...x,xy->...y", output_shape=256, bias_axes="y"),
            *[tf.keras.layers.Dense(**v, use_bias=True) for k, v in self.train_kwargs.items() if "dense2_" in k],

            tf.keras.layers.Dense(units=len(self.label_set), **self.train_kwargs['denseE']),
            #tf.keras.layers.Dropout(**self.train_kwargs['dropout']),

        ])

        optimizer = tf.optimizers.Adam(**self.train_kwargs['adam'])
        self.model.compile(optimizer=optimizer,
                           loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                           metrics=[ 'mse', 'accuracy'])

        #self.model.build()
        #self.model.summary()

        history = self.model.fit(self.train_ds,
                                 validation_data=self.val_ds,
                                 epochs=self.train_kwargs['epochs'], callbacks=[es, mcwhole, mcweights])


        LayoutModeler.model = self.model
        return history

    def plot(self, history):
        from matplotlib import pyplot
        # plot training histortest/tapetumn-vs-nucullus.pdf.labeled.htmy
        pyplot.plot(history.history['accuracy'], label='train')
        pyplot.plot(history.history['val_accuracy'], label='validation')
        pyplot.legend()
        pyplot.show()
        pyplot.savefig("accuracy_epochs2.png")

    def validate(self):
        # evaluate the model
        try:
            _, train_acc = self.model.evaluate(self.train_ds, verbose=0)
            _, test_acc = self.model.evaluate(self.test_ds, verbose=0)
            self.logger.info('Train: %.3f, Test: %.3f' % (train_acc, test_acc))

        except ValueError:
            self.logger.error("Bad distribution of training data, shapes did'nt match, no extra evaluation")

        logging.info('Validation')
        xy_new = self.model.predict_classes(self.val_ds, batch_size=None)
        for x_y_pred, y_true in itertools.islice(zip(self.val_ds.unbatch(), xy_new), 40):
            y_pred = tf.keras.backend.argmax(x_y_pred[1])
            print(f'{y_pred} --->>> {y_true}')

        logging.info('Test')
        xy_new = self.model.predict_classes(self.test_ds, batch_size=None)
        for x_y_pred, y_true in itertools.islice(zip(self.test_ds.unbatch(), xy_new), 40):
            y_pred = tf.keras.backend.argmax(x_y_pred[1])
            print(f'{y_pred} --->>> {y_true}')
        print(f'Legend {pprint.pformat(self.label_lookup.id_to_token, indent=4)}')

    def predict(self, feature_df):
        self.prepare_features(feature_df, training=False)
        pred_classes = self.model.predict(self.predict_ds)
        pred = tf.keras.backend.argmax(pred_classes)
        return list(pred.numpy())

    def load(self):
        try:
            if not hasattr(self, "model"):
                self.model = LayoutModeler.model if hasattr(LayoutModeler, "model") else tf.keras.models.load_model(self.model_path)
                optimizer = tf.optimizers.Adam(**self.train_kwargs['adam'])
                self.model.compile(optimizer=optimizer,
                                   loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                                   metrics=['mse', 'accuracy'])
                self.model.built = True
                self.model.load_weights(self.model_path + "variables/vair")


            print(os.getcwd() + "->" + self.lookup_path)

            with open(self.lookup_path, "rb") as f:
                self.label_lookup = pickle.load(f)

            if not hasattr(self, "label_lookup") and not hasattr(self, "lookup_path"):
                raise ValueError(f"No lookup table could be loaded from {self.lookup_path} (cwd= {os.getcwd()}")

        except OSError as e:
            e.args = (str(e.args[0]) + f"\n Please train model first and it should be written to {self.model_path}",)
            raise


if __name__ == '__main__':
    modeler = LayoutModeler(debug=True)
    modeler(modeler.feature_path)
