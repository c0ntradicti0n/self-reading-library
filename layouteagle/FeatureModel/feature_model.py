import numpy as np
import pandas
import pandas as pd

import tensorflow as tf
from more_itertools import flatten

from sklearn.model_selection import train_test_split
from tensorflow_core.python.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow_core.python.keras.layers.normalization_v2 import BatchNormalization
from tensorflow_core.python.keras.optimizers import Adam
from tensorflow_core.python.keras.utils import to_categorical
from tf2crf import CRF

from layouteagle.bi_lstm_crf_layout.bilstm_crf import sorted_by_zipped
from layouteagle.helpers.list_tools import Lookup

feature_path = ".layouteagle/features.pckl"
feature_df = pandas.read_pickle(feature_path)

label_set = list(set(feature_df['column_labels'].tolist()))
label_lookup = Lookup([label_set])
feature_df.column_labels = label_lookup(token_s=feature_df.column_labels.tolist())

cols_to_use = ["x", "y", "len", "height", "page_number", "font-size", "fine_grained_pdf", "coarse_grained_pdf",
               "line-height", "chars", "nums", "signs", "column_labels"]
feature_df = feature_df.reset_index()

distance_col_prefix = 'd_'
max_distance = max([max(x) for x in feature_df[1:]['distance_vector']])
max_distance = max([max(x) for x in feature_df[1:]['distance_vector']])
feature_df.distance_vector = feature_df[1:].distance_vector.apply(lambda x: x / max_distance)
feature_df.distance_vector = feature_df[1:].distance_vector.apply(lambda x: list(sorted(x)))
feature_df = feature_df.assign(**feature_df.distance_vector.apply(pandas.Series).add_prefix(distance_col_prefix))
feature_df = feature_df.fillna(1)

angle_col_prefix = 'a_'
max_angle = max([max(x) for x in feature_df[1:]['angle']])
min_angle = min([min(x) for x in feature_df[1:]['angle']])

# feature_df.angle = feature_df[1:].angle.apply(lambda x:(x+abs(min_angle))/(max_angle+abs(min_angle)))
feature_df.angle = feature_df[1:].angle.apply(lambda x: list(x))
feature_df['da'] = list(zip(feature_df["angle"], feature_df["distance_vector"]))
feature_df.angle = feature_df[1:]["da"].apply(lambda x: (sorted_by_zipped(x)))
feature_df = feature_df.assign(**feature_df.angle.apply(pandas.Series).add_prefix(angle_col_prefix))
feature_df = feature_df.fillna(1)

cols_to_use += [col for col in feature_df.columns if col.startswith(distance_col_prefix) or col.startswith(angle_col_prefix)]

feature_df = feature_df[cols_to_use]

with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
    print (feature_df.head())

train, test = train_test_split(feature_df, test_size=0.2)
train, val = train_test_split(train, test_size=0.2)
print(len(train), 'train examples')
print(len(val), 'validation examples')
print(len(test), 'test examples')

# A utility method to create a tf.data dataset from a Pandas Dataframe
def df_to_dataset(dataframe, shuffle=True, batch_size=32):
  dataframe = dataframe.copy()
  dataframe = dataframe.reset_index()
  labels = to_categorical(dataframe.pop('column_labels'))
  ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
  if shuffle:
    ds = ds.shuffle(buffer_size=len(dataframe))
  ds = ds.batch(batch_size)
  return ds

batch_size = 5 # A small batch sized is used for demonstration purposes
train_ds = df_to_dataset(train, batch_size=batch_size)
val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)
test_ds = df_to_dataset(test, shuffle=False, batch_size=batch_size)

for feature_batch, label_batch in train_ds.take(1):
  print('Every feature:', list(feature_batch.keys()))
  print('A batch of ages:', feature_batch['chars'])
  print('A batch of targets:', label_batch )

# We will use this batch to demonstrate several types of feature columns
example_batch = next(iter(train_ds))[0]

# A utility method to create a feature column
# and to transform a batch of data
def demo(feature_column):
  feature_layer = tf.keras.layers.DenseFeatures(feature_column)
  print(feature_layer(example_batch).numpy())


feature_columns = []

# numeric cols
for header in ["x", "y", "len", "height", "page_number", "font-size", "fine_grained_pdf", "coarse_grained_pdf",
               "line-height", "chars", "nums", "signs"]:
  feature_columns.append(tf.feature_column.numeric_column(header))



feature_layer = tf.keras.layers.DenseFeatures(feature_columns=feature_columns)
batch_size = 4
train_ds = df_to_dataset(train, batch_size=batch_size)
val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)
test_ds = df_to_dataset(test, shuffle=False, batch_size=batch_size)

es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=3)
mc = ModelCheckpoint('best_model.h5', monitor='val_accuracy', mode='max', verbose=1, save_best_only=True)

model = tf.keras.Sequential([
    feature_layer,
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(200, trainable=True, activation='tanh', dtype='float64'),
    tf.keras.layers.Dense(len(label_set), trainable=True, activation='softmax',dtype='float64'),

])

optimizer = tf.optimizers.Adam(lr=0.0001)
model.compile(optimizer=optimizer,
              loss=tf.keras.losses.CategoricalCrossentropy(from_logits=False, ),
              metrics=['accuracy'])

history = model.fit(train_ds,
          validation_data=val_ds,
          epochs=300, callbacks=[es, mc])

from matplotlib import pyplot
# evaluate the model
_, train_acc = model.evaluate(train_ds, verbose=0)
_, test_acc = model.evaluate(test_ds, verbose=0)
print('Train: %.3f, Test: %.3f' % (train_acc, test_acc))
# plot training history
pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()

ynew = model.predict_classes(val_ds, batch_size = None)
print("Validation", len(ynew))
for x,y in  zip(val_ds.unbatch(), ynew):
        print (f"{x[1]} --->>> {y}")
print ("Legend", label_lookup.id_to_token)

model.save("./layouteagle/FeatureModel.keras")





