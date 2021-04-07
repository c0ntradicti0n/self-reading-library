import re
import textwrap

import chardet
from pdfminer.high_level import extract_text

from python.layouteagle import config
from python.layouteagle.pathant.Converter import converter
from python.layouteagle.pathant.PathSpec import PathSpec
from python.nlp.NlpUtils.Regexes import SENTENCE_END_REGEX
from python.nlp.NlpUtils.split_interpunction import split_punctuation
from python.nlp.TransformerStuff.alignment import needle
from python.nlp.TransformerStuff.simple_align import align


@converter("wordi", 'wordi.page')
class Pager(PathSpec):
    def __init__(self, *args, max_window=200, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_window = max_window

    WORD_I_LINE_REGEX = re.compile(r"^(\d+):(.*)", re.DOTALL);

    def match_wordi_line(self, line):
        m = Pager.WORD_I_LINE_REGEX.match(line)
        if not m:
            self.logger.error(f"No match line in wordi! for {line}")
            return -1, line
        return int(m.group(1)), m.group(2)

    def __call__(self, paths, *args, **kwargs):
        for paths, meta in paths:
            pdf_path, wordi_path, _ = paths

            # read the text as it is referenced in the html from the wordi file
            # containing the class index of the tags and the string, may contain
            # errors: f"{index}:{string}"
            with open(wordi_path, 'rb') as f:
                content = f.read()
            print(chardet.detect(content))
            encoding = chardet.detect(content)['encoding']
            lines = content.decode(encoding).split()
            i_word = [self.match_wordi_line(line) for line in lines if len(line) > 2]
            print(lines[:3])

            # read pure text with better tokenization with pdfminer.six
            text = extract_text(meta['pdf_path']).replace("/x19", "")
            real_tokens = split_punctuation(text, ":!?;")

            # TODO sorting and filtering by layout analysis
            # ...

            # start iterating on windows of this text
            generator = self.make_tokenized_windows(i_word, real_tokens)
            i = 0
            prev_window = ""
            while True:

                try:
                    next(generator)
                    last_annotated_token = yield

                    window, window_meta = generator.send(last_annotated_token)
                except StopIteration as e:
                    self.logger.info(f"finished after {i} texts")
                    return

                print(f"text window:")
                print(textwrap.fill(" ".join([t for t in window]), width=200))

                yield window, {**window_meta, "i_word": i_word, **meta, 'doc_id': meta['pdf_path']}

                i += 1
                if i > config.max_windows_per_text:
                    i = 0
                    break
                if window == prev_window:
                    i = 0
                    break

                prev_window = window

    def make_tokenized_windows(self, i_word, real_tokens):
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
                try:
                    start_i1 = i2_to_i1[consumed_tokens] + start_i1
                    start_i2 = consumed_tokens + start_i2 + 1

                except KeyError:
                    self.logger.error("error computing new beginning")
                    return

            window_tokens = list(tokens[start_i1:start_i1 + 300])
            window = []
            sentences_i = 0
            sentences_j = 0
            for j, w in enumerate(real_tokens[start_i2: start_i2 + 300]):
                window.append(w)
                if len(window) > self.max_window:
                    window = window[:sentences_j]
                    break
                if SENTENCE_END_REGEX.match(w):
                    sentences_i += 1
                    sentences_j = j + 1


            alignment = needle(window_tokens, window)[2:][0]

            _i_to_i2 = {}
            _i2_old = None
            for _i1, _i2 in reversed(alignment):
                if _i2:
                    _i2_old = _i2
                if _i1 and _i2_old:
                    _i_to_i2.setdefault(_i[_i1 + start_i1], []).append(_i2_old)

            # to translate the comsumed tokens to the index for the paper index
            i2_to_i1 = []
            _i1_old, _i2_old = None, None
            for _i1, _i2 in reversed(alignment):
                if _i1:
                    _i1_old = _i1
                if _i2:
                    _i2_old = _i2

                if _i1_old and _i2_old:
                    i2_to_i1.append(
                        (_i2 if _i2 is not None else _i2_old,
                         _i1 if _i1 is not None else _i1_old)
                    )

            i2_to_i1 = dict(list(reversed(i2_to_i1)))
            print(window)

            yield window, {
                "_i_to_i2":
                    _i_to_i2,
                "i2_to_i1":
                    i2_to_i1,
                "alignment":
                    alignment,
                "original_text":
                    window_tokens
            }
