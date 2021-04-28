import itertools
import os
import pickle
from typing import Dict

import joblib
import more_itertools
import pandas
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, Normalizer
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.python.keras.layers import BatchNormalization, Dropout
from tensorflow.python.keras.utils.np_utils import to_categorical
import logging
import pprint


from python.helpers.list_tools import Lookup, sorted_by_zipped
from python.layouteagle import config
from python.layouteagle.pathant.PathSpec import PathSpec



class LayoutModeler(PathSpec):
    train_kwargs = {
        'dropout': {'rate': 0.01,
                    'dtype': 'float64'},
        'dense0': {'units': 44,
                   'trainable': True,
                   'activation': 'swish',
                   'dtype': 'float64'},
        'dense1': {'units': 27,
                   'trainable': True,
                   'activation': 'swish',
                   'dtype': 'float64'},
        'dense2': {'units': 17,
                   'trainable': True,
                   'activation': 'swish',
                   'dtype': 'float64'},
        'dense3': {'units': 10,
                   'trainable': True,
                   'activation': 'swish',
                   'dtype': 'float64'},
        'dense4': {'units': 7,
                   'trainable': True,
                   'activation': 'swish',
                   'dtype': 'float64'},
        'denseE': { # 'units' are set by us self to the necessary value
                   'trainable': True,
                   'activation': 'softmax',
                   'dtype': 'float64'},
        'adam': {'lr': 0.0005},
        'epochs': 200,
        'batch_size': 320,
        'patience': 3,
        'labels': 'layoutlabel',
        'cols_to_use': ['x', 'y', 'height', 'font-size', 'len', "spans_no",
                        'fine_grained_pdf', 'coarse_grained_pdf','line-height']
    }

    def __init__(self,
                 *args,
                 override_train_kwargs: Dict= {},
                 model_path = config.layout_model_path,
                 debug: bool = True, **kwargs):
        super().__init__(*args, **kwargs)

        if not model_path:
            raise ValueError("Please specify a path for saving and loading the model")

        self.model_path = model_path
        self.lookup_path = self.model_path + ".lookup.pickle"

        self.train_kwargs.update(override_train_kwargs)

        self.debug = debug

    def load_pandas_file(self, feature_path):
        return pandas.read_pickle(feature_path)

    def prepare_features(self, feature_df, training=True):
        if training:
            self.label_set = list(set(feature_df['layoutlabel'].tolist()))
            self.label_lookup = Lookup([self.label_set])

        feature_df.layoutlabel = self.label_lookup(token_s=feature_df.layoutlabel.tolist())

        feature_df = self.prepare_df(feature_df, training=training)

        norm_cols = [col for col in self.cols_to_use if col != self.train_kwargs['labels']]

        if training:
            scaler = Normalizer()
            scaler.fit(feature_df[norm_cols].to_numpy())
            joblib.dump(scaler, self.model_path + ".scaler")
        else:
            scaler = joblib.load(self.model_path + ".scaler")

        feature_df[norm_cols] = scaler.transform(feature_df[norm_cols])

        for col in self.cols_to_use:
            if col != self.train_kwargs['labels']:
                feature_df[col] = feature_df[col] + abs(feature_df[col].min())
                feature_df[col] = feature_df[col] / feature_df[col].max()

        feature_df = feature_df.fillna(0)

        if training:
            train, test = train_test_split(feature_df, test_size=0.2)
            train, val = train_test_split(train, test_size=0.2)
            logging.info(f'{len(train)} train samples')
            logging.info(f'{len(val)} validation samples')
            logging.info(f'{len(test)} test samples')

            self.train_ds = self.df_to_dataset(train, shuffle=False, batch_size=self.train_kwargs['batch_size'], training=training)
            self.val_ds = self.df_to_dataset(val, shuffle=False, batch_size=self.train_kwargs['batch_size'], training=training)
            self.test_ds = self.df_to_dataset(test, shuffle=False, batch_size=self.train_kwargs['batch_size'], training=training)
        else:
            self.predict_ds =  self.df_to_dataset(feature_df, shuffle=False, batch_size=len(feature_df), training=False)

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

        labels = dataframe[self.train_kwargs['labels']].tolist()
        dataframe.pop(self.train_kwargs['labels'])
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
        self.cols_to_use = self.train_kwargs['cols_to_use'] + [self.train_kwargs['labels']] #([self.train_kwargs['labels']] if training else [])
        feature_df = feature_df.reset_index(drop=True)

        N = 7

        distance_col_prefix = 'd_'
        max_distance = max([max(x) for x in feature_df['distance_vector']])
        feature_df.distance_vector = feature_df.distance_vector.apply(lambda x: x / max_distance)
        feature_df.distance_vector = feature_df.distance_vector.apply(lambda x: list(more_itertools.padded(list(sorted(x))[:N], 0, 8)))
        feature_df = feature_df.assign(
            **feature_df.distance_vector.apply(pandas.Series).add_prefix(distance_col_prefix))
        feature_df = feature_df.fillna(1)

        angle_col_prefix = 'a_'
        feature_df.angle = feature_df.angle.apply(lambda x: list(x))
        feature_df['da'] = list(zip(feature_df['angle'], feature_df['distance_vector']))
        feature_df.angle = feature_df['da'].apply(lambda x: list(more_itertools.padded(list(sorted_by_zipped(x))[:N], 0, N)))
        feature_df = feature_df.assign(**feature_df.angle.apply(pandas.Series).add_prefix(angle_col_prefix))
        feature_df = feature_df.fillna(1)
        with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
            logging.info(str(feature_df.head()))

        x_profile_col_prefix = 'xp_'
        y_profile_col_prefix = 'yp_'

        feature_df = feature_df.assign(**feature_df.x_profile.apply(pandas.Series).add_prefix(x_profile_col_prefix))
        feature_df = feature_df.assign(**feature_df.y_profile.apply(pandas.Series).add_prefix(y_profile_col_prefix))


        self.cols_to_use = self.cols_to_use + [col for col in feature_df.columns if
                             any(col.startswith(prefix) for prefix in [distance_col_prefix, angle_col_prefix, x_profile_col_prefix, y_profile_col_prefix])]


        if training:
            feature_df = feature_df.sample(frac=1).reset_index(drop=True)

        feature_df = feature_df[self.cols_to_use]


        #shift1 = feature_df.shift(periods=1, fill_value = 0)
        #shift_1 = feature_df.shift(periods=-1, fill_value = 0)
        #names =['bef', '', 'aft']
        #dfs = [feature_df, shift1, shift_1]
        #feature_df = pandas.concat([df.add_prefix(name) for name, df in zip(names, dfs)], axis=1).dropna()

        return feature_df

    def train(self, feature_columns, override_kwargs={}):
        logging.info(f"Model will go to {self.model_path}")
        os.system(f"rm {self.model_path}")

        self.train_kwargs.update(override_kwargs)
        feature_layer = tf.keras.layers.DenseFeatures(feature_columns=feature_columns, dtype='float64')

        es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=self.train_kwargs['patience'])
        mc = ModelCheckpoint(self.model_path,
                             monitor='val_accuracy',
                             save_best_only=True,
                             save_weights_only=True,
                             verbose=1)

        self.model = tf.keras.Sequential([
            feature_layer,

            tf.keras.layers.Dense(**self.train_kwargs['dense0']),
            tf.keras.layers.Dense(**self.train_kwargs['dense1']),
            tf.keras.layers.Dense(**self.train_kwargs['dense2']),
            tf.keras.layers.Dense(**self.train_kwargs['dense3']),
            tf.keras.layers.Dense(**self.train_kwargs['dense4']),

            tf.keras.layers.Dense(units=len(self.label_set), **self.train_kwargs['denseE']),
            #tf.keras.layers.Dropout(**self.train_kwargs['dropout']),

        ])

        optimizer = tf.optimizers.Adam(**self.train_kwargs['adam'])
        self.model.compile(optimizer=optimizer,
                      loss=tf.keras.losses.CategoricalCrossentropy(from_logits=False),
                      metrics=['accuracy'])#, 'mse'])

        history = self.model.fit(self.train_ds,
                            validation_data=self.val_ds,
                            epochs=self.train_kwargs['epochs'], callbacks=[es, mc])
        return history

    def plot(self, history):
        from matplotlib import pyplot
        # plot training history
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
            logging.info('Train: %.3f, Test: %.3f' % (train_acc, test_acc))

        except ValueError:
            logging.error("Bad distribution of training data, shapes did'nt match, no extra evaluation")

        xy_new = self.model.predict_classes(self.val_ds, batch_size=None)
        logging.info('Validation')
        for x_y_pred, y_true in itertools.islice(zip(self.val_ds.unbatch(), xy_new),20):
            y_pred = tf.keras.backend.argmax(x_y_pred[1])
            print(f'{y_pred} --->>> {y_true}')
        print(f'Legend {pprint.pformat(self.label_lookup.id_to_token, indent=4)}')

    def predict(self, feature_df):
        self.prepare_features(feature_df, training=False)
        pred = self.model.predict(self.predict_ds)
        #indices = [i for i, v in enumerate(pred) if pred[i] != y_test[i]]
        #subset_of_wrongly_predicted = [x_test[i] for i in indices]
        pred = tf.argmax(pred, axis=-1)
        return pred #self.model.predict_classes(self.predict_ds, batch_size=len(feature_df), verbose=100)

    def save(self):
        #self.model.load_weights(self.model_path)
        self.model.save(self.model_path + ".kerasmodel")
        with open(self.lookup_path, "wb") as f:
            pickle.dump(self.label_lookup,f)


    def load(self):
        try:
            if not hasattr(self, "model"):
                self.model = tf.keras.models.load_model (self.model_path)

            if not hasattr(self, "label_lookup"):
                with open(self.lookup_path, "rb") as f:
                    self.label_lookup = pickle.load(f)
            else:
                raise ValueError(f"No lookup table could be loaded from {self.lookup_path} (cwd= {os.getcwd()}")

        except OSError as e:
            e.args = (str(e.args[0]) + f"\n Please train model first and it should be written to {self.model_path}",)
            raise

if __name__ == '__main__':
    modeler = LayoutModeler(debug=True)
    modeler(modeler.feature_path)
