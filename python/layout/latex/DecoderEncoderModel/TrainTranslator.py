from tf_import import *

from layout.latex.DecoderEncoderModel.ShapeChecker import ShapeChecker

from latex.DecoderEncoderModel.Encoder import Encoder
from latex.DecoderEncoderModel.Decoder import Decoder, DecoderInput


class TrainTranslator(tf.keras.Model):
    use_tf_function = True

    def __init__(self, num_classes, embedding_dim, units,
                 # input_text_processor,
                 # output_text_processor,
                 use_tf_function=True,
                 pad_value=0):
        super().__init__()
        # Build the encoder and decoder
        encoder = Encoder(embedding_dim, units)
        decoder = Decoder(num_classes, embedding_dim, units)

        self.encoder = encoder
        self.decoder = decoder
        # self.input_text_processor = input_text_processor
        # self.output_text_processor = output_text_processor
        self.use_tf_function = use_tf_function
        self.shape_checker = ShapeChecker()
        self.pad_value = pad_value

    def train_step(self, inputs):
        self.shape_checker = ShapeChecker()
        if self.use_tf_function:
            return self._tf_train_step(inputs)
        else:
            return self._train_step(inputs)

    def _preprocess(self, input_vecs, target_tokens):
        self.shape_checker(input_vecs, ('batch', 't', 's'))
        self.shape_checker(target_tokens, ('batch', 't'))

        # Convert IDs to masks.
        input_mask = tf.broadcast_to(tf.expand_dims(tf.reduce_sum(input_vecs, axis=-1) != 0,axis=-1), shape=input_vecs.shape)
        self.shape_checker(input_vecs, ('batch', 't', 's'))

        target_mask = target_tokens != self.pad_value
        self.shape_checker(target_mask, ('batch', 't'))

        return input_vecs, input_mask, target_tokens, target_mask

    def _train_step(self, inputs):
        self.shape_checker = ShapeChecker()

        input_text, target_text = inputs

        (input_tokens, input_mask,
         target_tokens, target_mask) = self._preprocess(input_text, target_text)

        max_target_length = target_tokens.shape[1]

        with tf.GradientTape() as tape:
            # Encode the input
            enc_output, enc_state = self.encoder(input_tokens)

            self.shape_checker(enc_output, ('batch', 't', 'enc_units'))
            self.shape_checker(enc_state, ('batch', 'enc_units'))

            # Initialize the decoder's state to the encoder's final state.
            # This only works if the encoder and decoder have the same number of
            # units.
            dec_state = enc_state
            loss = tf.constant(0.0)

            for t in range(max_target_length - 11):
                # Pass in two tokens from the target sequence:
                # 1. The current input to the decoder.
                # 2. The target the target for the decoder's next prediction.
                new_tokens = target_tokens[:, t:t + 12]

                step_loss, dec_state = self._loop_step(input_tokens, new_tokens, input_mask, target_mask,
                                                       enc_output, dec_state)
                loss = loss + step_loss

            # Average the loss over all non padding tokens.
            average_loss = loss / tf.reduce_sum(tf.cast(target_mask, tf.float32))

        # Apply an optimization step
        variables = self.trainable_variables
        gradients = tape.gradient(average_loss, variables)
        self.optimizer.apply_gradients(zip(gradients, variables))

        # Return a dict mapping metric names to current value
        return {'batch_loss': average_loss,"halloloss": 00.1}


    def test_step(self, inputs):
        self.shape_checker = ShapeChecker()
        input_text, target_text = inputs
        input_text = tf.expand_dims(input_text, axis=0)
        target_text = tf.expand_dims(target_text, axis=0)
        (input_tokens, input_mask,
         target_tokens, target_mask) = self._preprocess(input_text, target_text)

        max_target_length = target_tokens.shape[1]

        # Encode the input
        enc_output, enc_state = self.encoder(input_tokens)

        self.shape_checker(enc_output, ('batch', 't', 'enc_units'))
        self.shape_checker(enc_state, ('batch', 'enc_units'))

        # Initialize the decoder's state to the encoder's final state.
        # This only works if the encoder and decoder have the same number of
        # units.
        dec_state = enc_state
        loss = tf.constant(0.0)

        for t in range(max_target_length - 1):
            # Pass in two tokens from the target sequence:
            # 1. The current input to the decoder.
            # 2. The target the target for the decoder's next prediction.
            new_tokens = target_tokens[:, t:t + 2]
            step_loss, dec_state = self._loop_step(input_tokens,input_tokens, new_tokens, input_mask, target_mask,
                                                   enc_output, dec_state)
            loss = loss + step_loss

        # Average the loss over all non padding tokens.
        average_loss = loss / tf.reduce_sum(tf.cast(target_mask, tf.float32))

        # Apply an optimization step
        variables = self.trainable_variables

        # Return a dict mapping metric names to current value
        return {'batch_loss': average_loss, "halloloss":0.1231245465}

    def _loop_step(self,input_vecs, new_tokens, input_mask, target_mask, enc_output, dec_state):
        input_token, target_token = new_tokens[:, 0:1], new_tokens[:, 1:2]

        # Run the decoder one step.
        decoder_input = DecoderInput(new_tokens=input_token,
                                     enc_output=enc_output,
                                     mask=target_mask,
                                     input_vecs=  input_vecs)

        dec_result, dec_state = self.decoder(decoder_input, state=dec_state)
        self.shape_checker(dec_result.logits, ('batch', 't1', 'logits'))
        self.shape_checker(dec_result.attention_weights, ('batch', 't1', 't'))
        self.shape_checker(dec_state, ('batch', 'dec_units'))

        # `self.loss` returns the total for non-padded tokens
        y = target_token
        y_pred = dec_result.logits
        step_loss = self.loss(y, y_pred)

        return step_loss, dec_state

    @tf.function  # (input_signature=[[tf.TensorSpec(dtype=tf.float64, shape=[154,10]),
    #                               tf.TensorSpec(dtype=tf.int64, shape=[None])]])
    def _tf_train_step(self, inputs):
        return self._train_step(inputs)

    def step_function(self, inputs):
        self.shape_checker = ShapeChecker()
        if self.use_tf_function:
            return self._tf_train_step(inputs)
        else:
            return self._train_step(inputs)
