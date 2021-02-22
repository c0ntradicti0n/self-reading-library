import re
import textwrap
import chardet
from python.layouteagle.pathant.Converter import converter
from python.layouteagle.pathant.PathSpec import PathSpec
import paired
import wordninja


@converter("wordi", 'wordi.page')
class Pager(PathSpec):
    def __init__(self, *args, max_window=200, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_window = max_window

    max_windows_per_text = 100

    WORD_I_LINE_REGEX = re.compile("^(\d+):(.*)", re.DOTALL);

    def match_wordi_line(self, line):
        m = Pager.WORD_I_LINE_REGEX.match(line)
        if not m:
            self.logger.error(f"No match line in wordi! for {line}")
            return (-1, line)
        return int(m.group(1)), m.group(2)


    def split_to_interpunction_tuple_parts(self, str, interpunction_parts ):
        if len(interpunction_parts) == 0:
            return " ".join(wordninja.split(str))
        else:
            seperator, *rest = interpunction_parts

            things = []
            for word in str.split(seperator):
                things.append(
                    self.split_to_interpunction_tuple_parts(word, rest))
            return  (seperator + " ").join(things)


    def __call__(self, paths, *args, **kwargs):
        for paths, meta in paths:
            _, wordi_path, _ = paths
            with open(wordi_path, 'rb') as f:
                content = f.read()
                print(chardet.detect(content))
                encoding = chardet.detect(content)['encoding']
                lines = content.decode(encoding).split()
                i_word = [self.match_wordi_line(line) for line in lines]
                print(lines[:3])

                generator = self.make_tokenized_windows(i_word)
                window = ""
                i = 0

                prev_window = None
                while True:
                    next(generator)

                    last_annotated_token = yield

                    try:
                        window, window_meta = generator.send(last_annotated_token)
                    except TypeError as e:
                        self.logger.info(f"finished after {i} texts")
                        break

                    print(f"text window:")
                    print(textwrap.fill(" ".join([t.text for t in window])))

                    yield window, {**window_meta, "i_word": i_word, **meta, 'doc_id': meta['pdf_path']}


                    i += 1
                    if i > self.max_windows_per_text:
                        i = 0
                        break

                    prev_window = window


    from spacy.lang.en import English

    nlp = English()
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer)

    def make_tokenized_windows(self, i_word):
        # holding three kinds of indices in parallel, splitting windows, keeping
        # information to retranslate results on the retokenized version of the
        # text:
        # * _i -> is the index from the pdf-reading result, used for applying a css
        #      class on the tag (the list can have wholes, -1 values for errors and
        #      indices for single letters
        # * _i1 -> index of this index, used for accessing this value again.
        # * _i2 -> index of the text, after it was splitted again in more rational
        #      words
        #


        _i, tokens = list(zip(*i_word))

        windowing = True
        start_i1 = 0
        start_i2 = 0

        while windowing:
            consumed_tokens = yield
            if consumed_tokens:

                start_i1 = i2_to_i1[consumed_tokens] + start_i1
                start_i2 = consumed_tokens + start_i2


            window_tokens = list(tokens[start_i1:start_i1 + 300])
            text = "".join(self.split_to_interpunction_tuple_parts(
                "".join(window_tokens)
                    .replace(" ", ""),
                [',', '.', ';', ':', '<']
            ))
            doc = self.nlp(text)
            sentences = doc.sents

            end = 0
            for sentence in sentences:
                if len(sentence) > self.max_window:
                    end += self.max_window - 1
                    break
                if end < self.max_window:
                    end += len(sentence)
                else:
                    break

            window = doc[0:end]
            try:
                print(window[0].idx, window[-1].idx)
                original_text = text[window[0].idx:window[-1].idx]

                tokens_in_window = [token.text for token in window]

                alignment = paired.align(
                    window_tokens, tokens_in_window
                )


                _i_to_i2 = []

                _i1_old, _i2_old = None, None
                for _i1, _i2 in alignment:
                    if  _i1 :
                        _i1_old = _i1
                    if  _i2:
                        _i2_old = _i2

                    if _i1_old and _i2_old:
                        _i_to_i2.append((_i[
                            (_i1 if _i1  is not None else _i1_old)
                            + start_i1] ,
                            (_i2 if _i2 is not None else _i2_old )
                        ))

                # to translate the comsumed tokens to the index for the paper index
                i2_to_i1 = {}
                _i1_old, _i2_old = None, None
                for _i1, _i2 in alignment:
                    if  _i1 :
                        _i1_old = _i1
                    if  _i2:
                        _i2_old = _i2

                    if _i1_old and _i2_old:
                        i2_to_i1[_i2 if _i2 is not None else _i2_old] = \
                            _i1 if _i1 is not None else _i1_old


                i2_to__i = \
                    { _i2:_i[_i1] for _i1, _i2 in alignment if _i2 and _i1}

                print(window)


                yield window, {
                    "_i_to_i2":
                        _i_to_i2,
                    "i2_to_i1":
                        i2_to_i1,
                    "alignment":
                        alignment,
                    "original_text":
                        original_text

                    }




            except Exception as e:
                self.logger.error("Making windows and translating tokenized window and original token indices")
                self.logger.error(str(e))



    def align_tokens_to_string(self, window_text, tokens_in_window, add=0):
        indices = [0]
        len_prev_substring = 0
        for i, substring in enumerate(tokens_in_window):
            try:
                indices.append(window_text.find(substring, indices[i] + len_prev_substring, len(window_text)))
                assert (len(indices) - 2 == i)
                len_prev_substring = len(substring)
            except Exception as e:
                x = 1

        indices = list([i + add for i in indices])[1:]
        assert (len(tokens_in_window) == len(indices))

        return indices
