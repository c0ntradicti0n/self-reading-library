import itertools
import os
import pickle
from typing import Dict
import joblib
import pandas
import numpy as np
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
        **{f'dense1_{i}': {
            'units': 25120,
            'trainable': True,
            'activation': 'swish',
            'dtype': 'float64'} for i in range(2, 1)
        },
        **{f'dense2_{i}': {
            'units': 5120,
            'trainable': True,
            'activation': 'swish',
            'dtype': 'float64'} for i in range(0, 0)
        },
        'denseE': {
            # 'units' are set by us self to the necessary value
            'trainable': True,
            'activation': 'softmax',
            'dtype': 'float64'},
        'optimizer': 'SGD',
        'optimizer_args': {
            'lr': 0.1,
            'momentum':0.9,
            'nesterov':True
            },
        'epochs':600,
        'num_layout_labels':4,
        'batch_size': 1000,
        'patience': 40,
        'labels': 'LABEL',
        'cols_to_use': config.cols_to_use,
        'array_cols_to_use': config.array_cols_to_use
    }

    def __init__(
        self,
        *args,
        override_train_kwargs: Dict = {},
        model_path=config.layout_model_path,
        debug: bool = True, **kwargs
    ):
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
        feature_df = feature_df.fillna(0)

        if training:
            self.label_set = list(set(feature_df['LABEL'].tolist()))
            self.label_lookup = Lookup([self.label_set])
            feature_df['LABEL'] = self.label_lookup(token_s=feature_df.LABEL.tolist())

        if training:
            train, test = train_test_split(feature_df, test_size=0.2)
            train, val = train_test_split(train, test_size=0.2)
            self.logger.info(f'{len(train)} train samples')
            self.logger.info(f'{len(val)} validation samples')
            self.logger.info(f'{len(test)} test samples')

            self.train_ds, self.feature_columns = self.df_to_dataset(train, shuffle=False, batch_size=self.train_kwargs['batch_size'],
                                               training=training)
            self.val_ds, _ = self.df_to_dataset(val, shuffle=False, batch_size=self.train_kwargs['batch_size'],
                                             training=training)
            self.test_ds, _ = self.df_to_dataset(test, shuffle=False, batch_size=self.train_kwargs['batch_size'],
                                              training=training)
        else:
            self.predict_ds, self.feature_columns = self.df_to_dataset(feature_df, shuffle=False, batch_size=len(feature_df), training=False)



    # A utility method to create a tf.data dataset from a Pandas Dataframe
    def df_to_dataset(self, dataframe, shuffle=True, batch_size=None, training=True):


        def feature_generator():


            if training:
                labels = dataframe[self.train_kwargs['labels']].tolist()
            else:
                labels = [0] * len(dataframe)

            categorical_labels = to_categorical(labels, num_classes=self.train_kwargs['num_layout_labels'])

            for ((idx, row), label) in zip(dataframe.iterrows(), categorical_labels):
                unpacked_row = self.prepare_df(row)

                res = tf.constant(unpacked_row, dtype=tf.float64), tf.constant(label, dtype=tf.float64)
                yield res

        try:
            ds = tf.data.Dataset.from_generator(
                feature_generator,
                # tf 2.3.0
                output_types=(tf.float64, tf.float64),
                output_shapes=(
                    (next(feature_generator())[0].__len__(),),
                    (self.train_kwargs['num_layout_labels'],)
                )
                # tf 2.5.0
                #output_signature=(
                #    tf.TensorSpec(shape=(next(feature_generator())[0].__len__(),), dtype=tf.float64),
                #    tf.TensorSpec(shape=(self.train_kwargs['num_layout_labels'],), dtype=tf.float64))
            )
        except:
            raise
        if shuffle:
            ds = ds.shuffle(buffer_size=len(dataframe))

        gen = feature_generator()
        x_y = next(gen)
        feature_columns = \
            [tf.feature_column.numeric_column(str(i)) for i in range(0, len(config.cols_to_use))] +\
            [tf.feature_column.numeric_column("cat" + str(i)) for i in range(len(config.cols_to_use), len(x_y[0]))]


        ds = ds.batch(batch_size)

        return ds, feature_columns

    def prepare_df(self, feature_df, training=True):
        scalar_values = np.array(feature_df[self.train_kwargs['cols_to_use']], dtype=np.float64)
        array_values = np.hstack(
            [col.flatten() for col in feature_df[self.train_kwargs['array_cols_to_use']]]
        )

        return np.hstack([scalar_values, array_values])

    def train(self, override_kwargs={}):
        self.logger.info(f"Model will go to {self.model_path}")

        self.train_kwargs.update(override_kwargs)

        es = EarlyStopping(
            monitor='val_accuracy',
            mode='min',
            verbose=1,
            patience=self.train_kwargs['patience']
        )
        mc = ModelCheckpoint(
            self.model_path,
            monitor='val_accuracy',
            save_best_only=True,
            save_weights_only=False,
            verbose=1
        )
        self.model = tf.keras.Sequential([
            *[tf.keras.layers.Dense(**v, use_bias=True) for k, v in self.train_kwargs.items() if "dense1_" in k],
            #tf.keras.layers.experimental.EinsumDense("...x,xy->...y", output_shape=256, bias_axes="y"),
            #tf.keras.layers.SimpleRNN(4),
            #tf.keras.layers.GRU(4),
            #tf.keras.layers.LeakyReLU(
            #    alpha=0.5
            #),
           #"""tf.keras.layers.Reshape((512,1)),
           #tf.keras.layers.Conv1D(filters=3, kernel_size=(100), activation='softmax'),
           #tf.keras.layers.Reshape((1239,)),"""

            *[tf.keras.layers.Dense(**v, use_bias=True) for k, v in self.train_kwargs.items() if "dense2_" in k],
            tf.keras.layers.Dense(units=len(self.label_set), **self.train_kwargs['denseE']),
        ])
        optimizer = getattr(tf.optimizers, self.train_kwargs['optimizer'])(**self.train_kwargs['optimizer_args'])
        self.model.compile(optimizer=optimizer,
                           loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                           metrics=[ 'mse', 'accuracy'])
        history = self.model.fit_generator(
            self.train_ds,
            validation_data=self.val_ds,
            epochs=self.train_kwargs['epochs'],
            callbacks=[es, mc]
        )
        LayoutModeler.model = self.model
        return history

    def plot(self, history):
        from matplotlib import pyplot
        pyplot.plot(history.history['accuracy'], label='train')
        pyplot.plot(history.history['val_accuracy'], label='validation')
        pyplot.legend()
        pyplot.show()
        pyplot.savefig("accuracy_epochs2.png")

    def validate(self):
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
                optimizer = tf.optimizers.SGD(**self.train_kwargs['optimizer'])
                self.model.compile(optimizer=optimizer,
                                   loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                                   metrics=['mse', 'accuracy'])
                self.model.built = True

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
