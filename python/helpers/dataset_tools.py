import tensorflow_text as tf_text
import tensorflow as tf
import numpy as np
import typing


def split_dataset(
    dataset: tf.data.Dataset,
    dataset_size: int,
    train_ratio: float,
    validation_ratio: float,
) -> typing.Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]:
    assert (train_ratio + validation_ratio) < 1

    train_count = int(dataset_size * train_ratio)
    validation_count = int(dataset_size * validation_ratio)
    test_count = dataset_size - (train_count + validation_count)

    dataset = dataset.shuffle(dataset_size)

    train_dataset = dataset.take(train_count)
    validation_dataset = dataset.skip(train_count).take(validation_count)
    test_dataset = dataset.skip(validation_count + train_count).take(test_count)

    return train_dataset, validation_dataset, test_dataset


def pad(array, shape, offsets, value=0, dtype=np.float):
    """
    array: Array to be padded
    reference: Reference array with the desired shape
    offsets: list of offsets (number of elements must be equal to the dimension of the array)
    """
    # Create an array of zeros with the reference shape
    result = np.full(shape=shape, fill_value=value, dtype=dtype)
    # Create a list of slices from offset to offset + shape in each dimension
    insertHere = [
        slice(offsets[dim], offsets[dim] + array.shape[dim])
        for dim in range(array.ndim)
    ]
    # Insert the array in the result at the specified offsets
    result[insertHere] = array
    return result


def translate_symbolic(
    self, input_text, *, max_length=50, return_attention=True, temperature=1.0
):
    shape_checker = ShapeChecker()
    shape_checker(input_text, ("batch",))

    batch_size = tf.shape(input_text)[0]

    # Encode the input
    input_tokens = self.input_text_processor(input_text)
    shape_checker(input_tokens, ("batch", "s"))

    enc_output, enc_state = self.encoder(input_tokens)
    shape_checker(enc_output, ("batch", "s", "enc_units"))
    shape_checker(enc_state, ("batch", "enc_units"))

    # Initialize the decoder
    dec_state = enc_state
    new_tokens = tf.fill([batch_size, 1], self.start_token)
    shape_checker(new_tokens, ("batch", "t1"))

    # Initialize the accumulators
    result_tokens = tf.TensorArray(tf.int64, size=1, dynamic_size=True)
    attention = tf.TensorArray(tf.float32, size=1, dynamic_size=True)
    done = tf.zeros([batch_size, 1], dtype=tf.bool)
    shape_checker(done, ("batch", "t1"))

    for t in tf.range(max_length):
        dec_input = DecoderInput(
            new_tokens=new_tokens, enc_output=enc_output, mask=(input_tokens != 0)
        )

        dec_result, dec_state = self.decoder(dec_input, state=dec_state)

        shape_checker(dec_result.attention_weights, ("batch", "t1", "s"))
        attention = attention.write(t, dec_result.attention_weights)

        new_tokens = self.sample(dec_result.logits)
        shape_checker(dec_result.logits, ("batch", "t1", "vocab"))
        shape_checker(new_tokens, ("batch", "t1"))

        # If a sequence produces an `end_token`, set it `done`
        done = done | (new_tokens == self.end_token)
        # Once a sequence is done it only produces 0-padding.
        new_tokens = tf.where(done, tf.constant(0, dtype=tf.int64), new_tokens)

        # Collect the generated tokens
        result_tokens = result_tokens.write(t, new_tokens)

        if tf.reduce_all(done):
            break

    # Convert the list of generated token ids to a list of strings.
    result_tokens = result_tokens.stack()
    shape_checker(result_tokens, ("t", "batch", "t0"))
    result_tokens = tf.squeeze(result_tokens, -1)
    result_tokens = tf.transpose(result_tokens, [1, 0])
    shape_checker(result_tokens, ("batch", "t"))

    result_text = self.tokens_to_text(result_tokens)
    shape_checker(result_text, ("batch",))

    if return_attention:
        attention_stack = attention.stack()
        shape_checker(attention_stack, ("t", "batch", "t1", "s"))

        attention_stack = tf.squeeze(attention_stack, 2)
        shape_checker(attention_stack, ("t", "batch", "s"))

        attention_stack = tf.transpose(attention_stack, [1, 0, 2])
        shape_checker(attention_stack, ("batch", "t", "s"))

        return {"text": result_text, "attention": attention_stack}
    else:
        return {"text": result_text}


def tf_lower_and_split_punct(text):
    # Split accecented characters.
    text = tf_text.normalize_utf8(text, "NFKD")
    text = tf.strings.lower(text)
    # Keep space, a to z, and select punctuation.
    text = tf.strings.regex_replace(text, "[^ a-z.?!,¿]", "")
    # Add spaces around punctuation.
    text = tf.strings.regex_replace(text, "[.?!,¿]", r" \0 ")
    # Strip whitespace.
    text = tf.strings.strip(text)

    text = tf.strings.join(["[START]", text, "[END]"], separator=" ")
    return text
