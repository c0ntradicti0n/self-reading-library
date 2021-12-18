import re
import textwrap

import chardet
from pdfminer.high_level import extract_text

from core import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from language.NlpUtils.Regexes import SENTENCE_END_REGEX
from language.NlpUtils.split_interpunction import split_punctuation


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

            encoding = chardet.detect(content)['encoding']
            lines = content.decode(encoding).split()
            i_word = [self.match_wordi_line(line) for line in lines if len(line) > 2]


            # read pure text with better tokenization with pdfminer.six
            text = extract_text(meta['pdf_path']).replace('', "")
            real_tokens = split_punctuation(text, ":!?;")

            # TODO sorting and filtering by latex analysis
            # ...

            # start iterating on windows of this text
            generator = self.make_tokenized_windows(real_tokens)
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

    def make_tokenized_windows(self, real_tokens):
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

        windowing = True
        start_i2 = 0

        while windowing:
            consumed_tokens = yield
            if consumed_tokens:
                try:
                    start_i2 = consumed_tokens + start_i2 + 1

                except KeyError:
                    self.logger.error("error computing new beginning")
                    return

            window = []
            sentences_j = 0
            for j, w in enumerate(real_tokens[start_i2: start_i2 + 300]):
                window.append(w)
                if len(window) > self.max_window:
                    window = window[:sentences_j]
                    break
                if SENTENCE_END_REGEX.match(w):
                    sentences_j = j + 1

            print(window)

            yield window, {}
