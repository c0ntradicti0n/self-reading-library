from typing import Dict

import pandas
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow_core.python.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow_core.python.keras.utils import to_categorical

from layouteagle.helpers.list_tools import Lookup, sorted_by_zipped

import logging
import pprint


class LayoutModeler:
    kwargs = {
        'dropout': {'rate': 0.2,
                    'dtype': 'float64'},
        'dense1': {'units': 200,
                   'trainable': True,
                   'activation': 'tanh',
                   'dtype': 'float64'},
        'denseE': { # 'units' are set by us self to necessary
                   'trainable': True,
                   'activation': 'softmax',
                   'dtype': 'float64'},
        'adam': {'lr': 0.00003},
        'epochs': 100,
        'batch_size': 32,
        'labels': 'column_labels',
        'cols_to_use': ['x', 'y', 'len', 'height', 'page_number', 'font-size',
                        'fine_grained_pdf', 'coarse_grained_pdf','line-height',
                        'chars', 'nums', 'signs']
    }

    def __init__(self,
                 feature_path: str = '.layouteagle/features.pckl',
                 model_path: str = '.layouteagle/layoutmodel.keras',
                 override_train_kwargs: Dict= {},
                 debug: bool = False):
        self.feature_path = feature_path
        self.model_path = model_path
        self.kwargs.update(override_train_kwargs)
        self.debug = debug

        try:
            self.model = self.load()
        except OSError:
            logging.error("no model found, not initializing model, call the model with the path to the feature df dump")

    def load_pandas_file(self, feature_path):
        return pandas.read_pickle(feature_path)

    def prepare_features(self, feature_df):
        self.label_set = list(set(feature_df['column_labels'].tolist()))
        self.label_lookup = Lookup([self.label_set])
        feature_df.column_labels = self.label_lookup(token_s=feature_df.column_labels.tolist())

        self.cols_to_use = self.kwargs['cols_to_use'] + [self.kwargs['labels']]
        feature_df = feature_df.reset_index(drop=True)

        distance_col_prefix = 'd_'
        max_distance = max([max(x) for x in feature_df[1:]['distance_vector']])
        feature_df.distance_vector = feature_df[1:].distance_vector.apply(lambda x: x / max_distance)
        feature_df.distance_vector = feature_df[1:].distance_vector.apply(lambda x: list(sorted(x)))
        feature_df = feature_df.assign(
            **feature_df.distance_vector.apply(pandas.Series).add_prefix(distance_col_prefix))
        feature_df = feature_df.fillna(1)

        angle_col_prefix = 'a_'
        feature_df.angle = feature_df[1:].angle.apply(lambda x: list(x))
        feature_df['da'] = list(zip(feature_df['angle'], feature_df['distance_vector']))
        feature_df.angle = feature_df[1:]['da'].apply(lambda x: list(sorted_by_zipped(x))[:50])
        feature_df = feature_df.assign(**feature_df.angle.apply(pandas.Series).add_prefix(angle_col_prefix))
        feature_df = feature_df.fillna(1)

        with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
            logging.info(str(feature_df.head()))

        self.cols_to_use += [col for col in feature_df.columns if
                             col.startswith(distance_col_prefix) or col.startswith(angle_col_prefix)]
        feature_df = feature_df.sample(frac=1).reset_index(drop=True)
        feature_df = feature_df[self.cols_to_use]

        train, test = train_test_split(feature_df, test_size=0.2)
        train, val = train_test_split(train, test_size=0.2)
        logging.info(f'{len(train)} train samples')
        logging.info(f'{len(val)} validation samples')
        logging.info(f'{len(test)} test samples')

        # A utility method to create a tf.data dataset from a Pandas Dataframe
        def df_to_dataset(dataframe, shuffle=True, batch_size=self.kwargs['batch_size']):
            dataframe = dataframe.copy()
            dataframe = dataframe.reset_index(drop=True)
            try:
                labels = dataframe[self.kwargs['labels']].tolist()
                dataframe.pop(self.kwargs['labels'])
                categorical_labels = to_categorical(labels)
            except:
                raise
            ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), categorical_labels))
            if shuffle:
                ds = ds.shuffle(buffer_size=len(dataframe))
            ds = ds.batch(batch_size)
            return ds

        self.train_ds = df_to_dataset(train)
        self.val_ds = df_to_dataset(val, shuffle=False)
        self.test_ds = df_to_dataset(test, shuffle=False)

        for feature_batch, label_batch in self.train_ds.take(1):
            logging.debug(f'Every feature: {list(feature_batch.keys())}')
            logging.debug(f'A batch of ages: {feature_batch["chars"]}')
            logging.debug(f'A batch of targets: {str(label_batch)}')

        feature_columns = []

        # remove the labels, that were put in the df temporarily
        self.cols_to_use = [col for col in self.cols_to_use if col != self.kwargs['labels']]

        # all are numeric cols
        for header in self.cols_to_use:
            feature_columns.append(tf.feature_column.numeric_column(header))
        return feature_columns

    def train(self, feature_columns, override_kwargs={}):
        self.kwargs.update(override_kwargs)
        feature_layer = tf.keras.layers.DenseFeatures(feature_columns=feature_columns, dtype='float64')

        es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=3)
        mc = ModelCheckpoint(self.model_path + ".h5", monitor='val_accuracy', mode='max', verbose=1, save_best_only=True)

        self.model = tf.keras.Sequential([
            feature_layer,
            tf.keras.layers.Dropout(**self.kwargs['dropout']),
            tf.keras.layers.Dense(**self.kwargs['dense1']),
            tf.keras.layers.Dense(units=len(self.label_set), **self.kwargs['denseE'])
        ])

        optimizer = tf.optimizers.Adam(**self.kwargs['adam'])
        self.model.compile(optimizer=optimizer,
                      loss=tf.keras.losses.CategoricalCrossentropy(from_logits=False),
                      metrics=['accuracy'])

        history = self.model.fit(self.train_ds,
                            validation_data=self.val_ds,
                            epochs=self.kwargs['epochs'], callbacks=[es, mc])
        return history

    def plot(self, history):
        from matplotlib import pyplot
        # plot training history
        pyplot.plot(history.history['accuracy'], label='train')
        pyplot.plot(history.history['val_accuracy'], label='test')
        pyplot.legend()
        pyplot.show()
        pyplot.savefig("accuracy_epochs2.png")

    def validate(self):
        # evaluate the model
        _, train_acc = self.model.evaluate(self.train_ds, verbose=0)
        _, test_acc = self.model.evaluate(self.test_ds, verbose=0)
        logging.info('Train: %.3f, Test: %.3f' % (train_acc, test_acc))

        self.val_ds
        y_new = self.model.predict_classes(self.val_ds, batch_size=None)
        logging.info('Validation')
        for x, y in zip(self.val_ds.unbatch(), y_new):
            logging.info(f'{x[1]} --->>> {y}')
        logging.warning(f'Legend {pprint.pformat(self.label_lookup.id_to_token, indent=4)}')

    def save(self):
        self.model.save(self.model_path)

    def load(self):
        self.model = tf.saved_model.load(self.model_path)

    def __call__(self, **train_kwargs):
        feature_df = self.load_pandas_file(self.feature_path)
        feature_columns = self.prepare_features(feature_df)
        history = self.train(feature_columns, **train_kwargs)
        if self.debug:
            self.plot(history)
        self.validate()
        self.save()
        logging.info(f'made model, saved to {self.feature_path}')


if __name__ == '__main__':
    modeler = LayoutModeler(debug=True)
    modeler()
