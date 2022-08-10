import numpy as np

import os

import pandas
from helpers.list_tools import Lookup
from config import config

os.environ["LD_LIBRARY_PATH"] = '/usr/local/cuda-11.0/targets/x86_64-linux/lib/'

from helpers.dataset_tools import tf_lower_and_split_punct, pad, split_dataset
from latex.DecoderEncoderModel.BahdanauAttention import BahdanauAttention, plot_attention
from latex.DecoderEncoderModel.BatchLogs import BatchLogs
from latex.DecoderEncoderModel.Decoder import Decoder, DecoderInput
from latex.DecoderEncoderModel.Encoder import Encoder
from latex.DecoderEncoderModel.MaskedLoss import MaskedLoss
from layout.latex.DecoderEncoderModel.TrainTranslator import TrainTranslator
from latex.DecoderEncoderModel.Translator import Translator
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint
from tf_import import *

BATCH_SIZE = 64
_PAD = "PAD"
MODEL_NAME = 'layout_translator'

import matplotlib.pyplot as plt

use_builtins = True

# Download the file


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


dataset = dataset.batch(BATCH_SIZE)


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

for example_input_batch, example_target_batch in dataset.take(4):
    print(example_input_batch[:5])
    print()
    print(example_target_batch[:5])


example_input_tokens = tf.random.uniform(
    shape=example_input_batch[0].shape, minval=0, dtype=tf.float64,
    maxval=1)
example_output_tokens = tf.random.uniform(
    shape=example_target_batch[0].shape, minval=0, dtype=tf.int64,
    maxval=len(label_lookup.token_to_id))

print(example_output_tokens)

example_logits = tf.random.normal([5, 1, len(label_lookup.token_to_id)])
print(example_output_tokens)

page_input_data = tf.constant(
    tf.expand_dims(example_input_tokens,0)
)
# dataset = tf.data.Dataset.from_tensor_slices((inp, targ)).shuffle(BUFFER_SIZE)
# dataset = dataset.batch(BATCH_SIZE)


example_text = tf.constant('c1 c1 c1 c1 c1')

print(example_text.numpy())
print(tf_text.normalize_utf8(example_text, 'NFC').numpy())

print(example_text.numpy().decode())
print(tf_lower_and_split_punct(example_text).numpy().decode())

max_vocab_size = 5
"""
input_text_processor = preprocessing.TextVectorization(
    standardize=tf_lower_and_split_punct,
    max_tokens=max_vocab_size)


input_text_processor.adapt(inp)

# Here are the first 10 words from the vocabulary:
print(input_text_processor.get_vocabulary()[:10])


"""
"""
example_tokens = input_text_processor(example_input_batch)
example_tokens[:3, :10]


input_vocab = np.array(input_text_processor.get_vocabulary())
tokens = input_vocab[example_tokens[0].numpy()]
' '.join(tokens)
"""

plt.subplot(1, 2, 1)
plt.pcolormesh(example_target_batch)
plt.title('Token IDs')

plt.subplot(1, 2, 2)
plt.pcolormesh(example_target_batch != PAD)
plt.title('Mask')

EMBEDDING_DIM = 10
UNITS = 30

# Convert the input text to tokens.
# example_tokens = input_text_processor(example_input_batch)

# Encode the input sequence.
encoder = Encoder(
    EMBEDDING_DIM, UNITS)
example_enc_output, example_enc_state = encoder(example_input_batch)

print(f'Input batch, shape (batch): {example_input_batch.shape}')
print(f'Encoder output, shape (batch, s, units): {example_enc_output.shape}')
print(f'Encoder state, shape (batch, units): {example_enc_state.shape}')

attention_layer = BahdanauAttention(UNITS)

# Later, the decoder will generate this attention query
example_attention_query = tf.random.normal(shape=[len(example_input_batch), 2, 10])

# Attend to the encoded tokens

context_vector, attention_weights = attention_layer(
    query=example_attention_query,
    value=example_enc_output,
    mask=(example_target_batch != PAD))

print(f'Attention result shape: (batch_size, query_seq_length, units):           {context_vector.shape}')
print(f'Attention weights shape: (batch_size, query_seq_length, value_seq_length): {attention_weights.shape}')

# Later, the decoder will generate this attention query
example_attention_query = tf.random.normal(shape=[len(example_input_batch), 2, 10])

# Attend to the encoded tokens

context_vector, attention_weights = attention_layer(
    query=example_attention_query,
    value=example_enc_output,
    mask=(example_target_batch != PAD))

print(f'Attention result shape: (batch_size, query_seq_length, units):           {context_vector.shape}')
print(f'Attention weights shape: (batch_size, query_seq_length, value_seq_length): {attention_weights.shape}')

plt.subplot(1, 2, 1)
plt.pcolormesh(attention_weights[:, 0, :])
plt.title('Attention weights')
plt.show()

plt.subplot(1, 2, 2)
plt.pcolormesh(example_target_batch != PAD)
plt.title('Mask')
plt.show()

attention_weights.shape

attention_slice = attention_weights[0, 0].numpy()
attention_slice = attention_slice[attention_slice != 0]

plt.suptitle('Attention weights for one sequence')

plt.figure(figsize=(12, 6))
a1 = plt.subplot(1, 2, 1)
plt.bar(range(len(attention_slice)), attention_slice)
# freeze the xlim
plt.xlim(plt.xlim())
plt.xlabel('Attention weights')
plt.show()

a2 = plt.subplot(1, 2, 2)
plt.bar(range(len(attention_slice)), attention_slice)
plt.xlabel('Attention weights, zoomed')
plt.show()

# zoom in
top = max(a1.get_ylim())
zoom = 0.85 * top
a2.set_ylim([0.90 * top, top])
a1.plot(a1.get_xlim(), [zoom, zoom], color='k')

decoder = Decoder(len(label_lookup.token_to_id),
                  EMBEDDING_DIM, UNITS)

# Convert the target sequence, and collect the "[START]" tokens
# example_output_tokens = output_text_processor(example_target_batch)

start_index = 0  # output_text_processor._index_lookup_layer('[START]').numpy()
first_token = tf.constant([[start_index]] * example_target_batch.shape[0])

# Run the decoder
dec_result, dec_state = decoder(
    inputs=DecoderInput(new_tokens=first_token,
                        enc_output=example_enc_output,
                        input_vecs = example_input_batch,
                        mask=(example_target_batch != PAD)),
    state=example_enc_state
)

print(f'logits shape: (batch_size, t, output_vocab_size) {dec_result.logits.shape}')
print(f'state shape: (batch_size, dec_units) {dec_state.shape}')

sampled_token = tf.random.categorical(dec_result.logits[:, 0, :], num_samples=1)

dec_result, dec_state = decoder(
    DecoderInput(sampled_token,
                 example_enc_output,
                 input_vecs=example_input_batch,
                 mask=(example_target_batch != PAD)),
    state=dec_state)

sampled_token = tf.random.categorical(dec_result.logits[:, 0, :], num_samples=1)

"""

translator.train_step([example_input_batch, example_target_batch])

for n in range(10):
  print(translator.train_step([example_input_batch, example_target_batch]))
print()

print ("OVERFITTING SINGLE BATCH")
losses = []
for n in range(10):
  print(str(n) + '.', end='')
  logs = translator.train_step([example_input_batch, example_target_batch])
  losses.append(logs['batch_loss'].numpy())

print(losses)
plt.plot(losses)
plt.show()
"""

print("DOING IT WITH TF FUNCTION")
train_translator = TrainTranslator(
    len(label_lookup.id_to_token),
    EMBEDDING_DIM, UNITS, use_tf_function=True,
    pad_value=PAD
)

# Configure the loss and optimizer
train_translator.compile(
    optimizer=tf.optimizers.Adam(),
    loss=MaskedLoss(pad_value=PAD),
    metrics=['mse', 'accuracy'],
    run_eagerly=True
)

batch_loss = BatchLogs('batch_loss')
EBOCHS = 8

train_translator.fit(dataset, epochs=EPOCHS,
                     #validation_data=validation_dataset,
                     callbacks=[batch_loss, es, mc]
                     )
plt.plot(batch_loss.logs)
plt.ylim([0, EBOCHS])
plt.xlabel('Batch #')
plt.ylabel('CE/token')

plt.show()
translator = Translator(
    lookup=label_lookup,
    encoder=train_translator.encoder,
    decoder=train_translator.decoder,
    batch=BATCH_SIZE,
    size=PAD_WIDTH,
    dimension=EMBEDDING_DIM,
    pad_value=PAD,
    output_vocab_size=len(label_lookup.token_to_id)
)
tf.saved_model.save(translator, MODEL_NAME,
                    signatures={'serving_default': translator.tf_translate})

example_output_tokens = translator.sample(example_logits)

for input_row, output_row in zip(example_input_batch, example_target_batch):
    input_row = tf.expand_dims(input_row, axis=0)

    result = translator.tf_translate(input_features=example_input_batch)

    for x,y in zip(result['text'], [0]):

        print(x.numpy())
        print(output_row.numpy())

        print()

a = result['attention'][0]

print(np.sum(a, axis=-1))

_ = plt.bar(range(len(a[0, :])), a[0, :])

plt.imshow(np.array(a), vmin=0.0)
plt.show()

i = 0

plot_attention(result['attention'][i], page_input_data[i], result['text'][i])
