from tf_import import *
from layout.DecoderEncoderModel.ShapeChecker import ShapeChecker
from layout.DecoderEncoderModel.Decoder import DecoderInput
from helpers.list_tools import Lookup

import numpy as np

tf.config.threading.set_intra_op_parallelism_threads(10)
tf.config.threading.set_inter_op_parallelism_threads(10)
tf.config.run_functions_eagerly(True)

class Translator(tf.Module):

    def __init__(self,
                 lookup: Lookup, encoder, decoder,
                 batch, size, dimension,
                 pad_value, output_vocab_size):
        self.encoder = encoder
        self.decoder = decoder
        self.lookup = lookup
        self.batch = batch
        self.size = size
        self.dimension = dimension


        token_mask = np.zeros([output_vocab_size], dtype=np.bool)
        token_mask[np.array([pad_value])] = True
        self.token_mask = token_mask

        self.end_token = pad_value


        self.tf_translate = tf.function(input_signature=[tf.TensorSpec(dtype=tf.float64, shape=[batch, size, dimension])])(self.tf_translate)


    def tokens_to_text(self, result_tokens):
        shape_checker = ShapeChecker()
        shape_checker(result_tokens, ('batch', 't'))
        #result_text_tokens = self.output_token_string_from_index(result_tokens)
        """shape_checker(result_text_tokens, ('batch', 't'))

        result_text = tf.strings.reduce_join(result_text_tokens,
                                             axis=1, separator=' ')
        shape_checker(result_text, ('batch'))

        result_text = tf.strings.strip(result_text)
        shape_checker(result_text, ('batch',))
        """
        return result_tokens

    def translate(self,
                  input_vecs, *,
                  max_length=50,
                  return_attention=True):
        batch_size = input_vecs.shape[0]
        enc_output, enc_state = self.encoder(input_vecs)

        dec_state = enc_state
        new_tokens = tf.fill([batch_size, 1], 0)



        input_mask = tf.broadcast_to(tf.expand_dims(tf.reduce_sum(input_vecs, axis=-1) != 0,axis=-1), shape=input_vecs.shape)
        output_mask = tf.reduce_sum(input_vecs, axis=-1) != self.end_token

        result_tokens = []
        attention = []
        done = tf.zeros([batch_size, 1], dtype=tf.bool)

        for _ in range(max_length):
            dec_input = DecoderInput(input_vecs=input_vecs, new_tokens=new_tokens,
                                     enc_output=enc_output,
                                     mask=output_mask)

            dec_result, dec_state = self.decoder(dec_input, state=dec_state)

            attention.append(dec_result.attention_weights)

            new_tokens = self.sample(dec_result.logits)

            # If a sequence produces an `end_token`, set it `done`
            done = done | (new_tokens == self.end_token)
            # Once a sequence is done it only produces 0-padding.
            new_tokens = tf.where(done, tf.constant(self.end_token, dtype=tf.int64), new_tokens)

            # Collect the generated tokens
            result_tokens.append(new_tokens)

            if tf.executing_eagerly() and tf.reduce_all(done):
                break

        # Convert the list of generates token ids to a list of strings.
        result_tokens = tf.concat(result_tokens, axis=-1)
        #result_text = self.tokens_to_text(result_tokens)

        if return_attention:
            attention_stack = tf.concat(attention, axis=1)
            return {'text': result_tokens, 'attention': attention_stack}
        else:
            return {'text': result_tokens}

    def tf_translate(self, input_features):
        return self.translate(input_features)

    def sample(self, logits):
        shape_checker = ShapeChecker()
        # 't' is usually 1 here.
        shape_checker(logits, ('batch', 't', 'vocab'))
        shape_checker(self.token_mask, ('vocab',))

        token_mask = self.token_mask[tf.newaxis, tf.newaxis, :]
        shape_checker(token_mask, ('batch', 't', 'vocab'), broadcast=True)

        # Set the logits for all masked tokens to -inf, so they are never chosen.
        logits = tf.where(self.token_mask, -np.inf, logits)

        new_tokens = tf.argmax(logits, axis=-1)


        shape_checker(new_tokens, ('batch', 't'))

        return new_tokens
