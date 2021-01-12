import functools
import re
from pprint import pprint
from re import Pattern

import chardet

from python.layouteagle.pathant.Converter import converter
from python.layouteagle.pathant.PathSpec import PathSpec
from python.nlp.TransformerStuff.conll_annnotation import CONLL_Annotation


@converter("wordi", 'wordi.page')
class Pager(PathSpec):
    def __init__(self, *args, max_window = 200, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_window = max_window

    WORD_I_LINE_REGEX = re.compile("^(\d+):(.*)", re.DOTALL);
    def match_wordi_line(self, line):
        m = Pager.WORD_I_LINE_REGEX.match(line)
        if not m:
            self.logger.error(f"No match line in wordi! for {line}")
            return (-1, line)
        return int(m.group(1)), m.group(2)

    def __call__(self, paths, *args, **kwargs):
        for paths, meta in paths:
            _, wordi_path, _ = paths
            with open(wordi_path, 'rb') as f:
                content = f.read()
                print(chardet.detect(content))
                encoding = chardet.detect(content)['encoding']
                lines = content.decode(encoding).split()
                i_word = [self.match_wordi_line(line) for line in lines]
                print (lines[:3])

                doing = True
                generator = self.make_tokenized_windows(i_word)
                next(generator)
                value = ""

                while doing:
                    value = generator.send (len(value))
                    print (f"value {value}")
                    next(generator)
                yield "hallo", meta

    from spacy.lang.en import English

    nlp = English()
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer)
    doc = nlp("This is a sentence. This is another sentence.")

    def make_tokenized_windows (self, lines):
        tokens = [word_snipped for _, word_snipped in lines]

        text = " ".join(tokens)
        original_indices_full = self.align_tokens_to_string(
            text,
            tokens
        )

        doc = self.nlp(text)
        sentences = doc.sents


        windowing = True
        end = 0
        start = 0
        while windowing:
            consumed_tokens =  yield
            start = start + consumed_tokens
            start = start + end
            for sentence in sentences:
                if end - start + len(sentence) < self.max_window:
                    end += len(sentence)
                else:
                    break


            window = doc[start:end]
            original_text = text[window[0].idx:window[-1].idx]



            tokens_in_window = [token.text for token in window]
            window_text = " ".join(tokens_in_window)

            indices = self.align_tokens_to_string(window_text,
                                        tokens_in_window,
                                        add=window[0].idx)

            print (window)

            yield window


    def align_tokens_to_string(self, window_text, tokens_in_window, add=0):
        indices = [0]
        for i, substring in enumerate(tokens_in_window):
            indices.append(window_text.find(substring, indices[i], len(window_text)))
        ##pprint(indices)
        indices = [i + add for i in indices]
        return indices







