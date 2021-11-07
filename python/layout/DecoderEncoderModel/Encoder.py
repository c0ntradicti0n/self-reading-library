from tf_import import *

from layout.DecoderEncoderModel.ShapeChecker import ShapeChecker


class Encoder(tf.keras.layers.Layer):
    def __init__(self, embedding_dim, enc_units):
        super(Encoder, self).__init__()
        self.enc_units = enc_units

        # The embedding layer converts tokens to vectors
        # self.embedding = tf.keras.layers.Embedding(self.input_vocab_size,
        #                                           embedding_dim)

        # The GRU RNN layer processes those vectors sequentially.
        self.gru = tf.keras.layers.GRU(self.enc_units,
                                       # Return the sequence and state
                                       return_sequences=True,
                                       return_state=True,
                                       recurrent_initializer='glorot_uniform')

    def call(self, tokens, state=None):
        shape_checker = ShapeChecker()

        shape_checker(tokens, ('batch', 's', 'embed_dim'))

        # 3. The GRU processes the embedding sequence.
        #    output shape: (batch, s, enc_units)
        #    state shape: (batch, enc_units)
        # with tf.device('/device:GPU:0'):

        output, state = self.gru(tokens, initial_state=state)
        shape_checker(output, ('batch', 's', 'enc_units'))
        shape_checker(state, ('batch', 'enc_units'))

        # 4. Returns the new sequence and its state.
        return output, state
