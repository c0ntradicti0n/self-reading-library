import os
import sys
import numpy as np
import pandas
from helpers.dataset_tools import split_dataset, pad
from helpers.list_tools import Lookup
from keras import Input
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.models import Model
from keras.layers import Embedding, Conv1D, MaxPooling1D, Flatten, Dense
from config import config
from tensorflow.python.keras.utils.np_utils import to_categorical
import tensorflow as tf
texts = []  # list of text samples
labels_index = {}  # dictionary mapping label name to numeric id
labels = []  # list of label ids
TEXT_DATA_DIR = "./20_newsgroup"
MAX_NB_WORDS = 200000
MAX_SEQUENCE_LENGTH = 200
VALIDATION_SPLIT = 0.5
EMBEDDING_DIM = 100
GLOVE_DIR = "./glove.6B"
_PAD = "PAD"
EPOCHS = 3
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
for name in sorted(os.listdir(TEXT_DATA_DIR)):
    path = os.path.join(TEXT_DATA_DIR, name)
    if os.path.isdir(path):
        label_id = len(labels_index)
        labels_index[name] = label_id
        for fname in sorted(os.listdir(path)):
            if fname.isdigit():
                fpath = os.path.join(path, fname)
                if sys.version_info < (3,):
                    f = open(fpath)
                else:
                    f = open(fpath, encoding='latin-1')
                t = f.read()
                i = t.find('\n\n')  # skip header
                if 0 < i:
                    t = t[i:]
                texts.append(t)
                f.close()
                labels.append(label_id)

print('Found %s texts.' % len(texts))




def prepare_row(feature_row, training=True):
    scalar_values = np.array(feature_row[config.cols_to_use], dtype=np.float64)
    if config.array_cols_to_use:
        array_values = np.hstack(
            [col.flatten() for col in feature_row[config.array_cols_to_use]]
        )

    return np.hstack([scalar_values] + ([array_values] if config.array_cols_to_use else []))


feature_df = pandas.read_pickle('/home/finn/PycharmProjects/LayoutEagle/python/.layouteagle/labeled_features.pickle')
feature_df = feature_df.head((int(len(feature_df))))
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



from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

tokenizer = Tokenizer(nb_words=MAX_NB_WORDS)
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)

word_index = tokenizer.word_index
print('Found %s unique tokens.' % len(word_index))

data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)

labels = to_categorical(np.asarray(labels))
print('Shape of data tensor:', data.shape)
print('Shape of label tensor:', labels.shape)

# split the data into a training set and a validation set
indices = np.arange(data.shape[0])
np.random.shuffle(indices)
data = data[indices]
labels = labels[indices]
nb_validation_samples = int(VALIDATION_SPLIT * data.shape[0])

x_train = data[:-nb_validation_samples]
y_train = labels[:-nb_validation_samples]
x_val = data[-nb_validation_samples:]
y_val = labels[-nb_validation_samples:]

embeddings_index = {}
f = open(os.path.join(GLOVE_DIR, 'glove.6B.100d.txt'))
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()

print('Found %s word vectors.' % len(embeddings_index))

embedding_matrix = np.zeros((len(word_index) + 1, EMBEDDING_DIM))
for word, i in word_index.items():
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        # words not found in embedding index will be all-zeros.
        embedding_matrix[i] = embedding_vector

"""
embedding_layer = Embedding(len(word_index) + 1,
                            EMBEDDING_DIM,
                            weights=[embedding_matrix],
                            input_length=MAX_SEQUENCE_LENGTH,
                            trainable=False)
"""

embedding_layer = Embedding(len(word_index) + 1,
                            EMBEDDING_DIM,
                            input_length=MAX_SEQUENCE_LENGTH)

sequence_input = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')
embedded_sequences = embedding_layer(sequence_input)
x = Conv1D(128, 5, activation='swish')(embedded_sequences)
x = MaxPooling1D(5)(x)
x = Conv1D(128, 5, activation='swish')(x)
x = MaxPooling1D(5)(x)
x = Conv1D(128, 5, activation='swish')(x)
x = MaxPooling1D(1)(x)  # global max pooling
x = Flatten()(x)
x = Dense(128, activation='swish')(x)
preds = Dense(len(labels_index), activation='softmax')(x)

model = Model(sequence_input, preds)
model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['acc', 'mse'])

# happy learning!
model.fit(x_train, y_train, validation_data=(x_val, y_val),
          epochs=20, batch_size=128,
          callbacks=[es, mc]
)
