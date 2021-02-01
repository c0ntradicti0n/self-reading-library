import re
import textwrap
import chardet
from python.layouteagle.pathant.Converter import converter
from python.layouteagle.pathant.PathSpec import PathSpec
import paired

@converter("wordi", 'wordi.page')
class Pager(PathSpec):
    def __init__(self, *args, max_window = 200, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_window = max_window

    max_windows_per_text = 50

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

                generator = self.make_tokenized_windows(i_word)
                next(generator)
                window = "..."
                i = 0

                prev_window = None
                while str(window):
                    window, window_meta = generator.send(len(window))
                    print(f"text window:")
                    print(textwrap.fill(" ".join([t.text for t in window])))
                    next(generator)
                    yield window, {**window_meta, "i_word": i_word, **meta, 'doc_id': meta['pdf_path']}

                    i += 1
                    if i > self.max_windows_per_text:
                        i = 0
                        break

                    if window == prev_window:
                        break
                    prev_window = window

    from spacy.lang.en import English

    nlp = English()
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer)

    def make_tokenized_windows (self, i_word):
        _i, tokens = list(zip(*i_word))

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
            if not consumed_tokens:
                consumed_tokens = 50
            start = start + consumed_tokens
            end = start
            for sentence in sentences:
                if len(sentence)> self.max_window:
                    end += self.max_window - 1
                    break
                if end - start + len(sentence) < self.max_window:
                    end += len(sentence)
                else:
                    break


            window = doc[start:end]
            try:
                print (window[0].idx, window[-1].idx)
                original_text = text[window[0].idx:window[-1].idx]

                tokens_in_window = [token.text for token in window]
                window_text = " ".join(tokens_in_window)

                indices = self.align_tokens_to_string(window_text,
                                            tokens_in_window,
                                            add=window[0].idx)

                # needleman wunsch algorithm to align tokens
                alignment = paired.align(
                     tokens, tokens_in_window,
                     match_score=5,
                     mismatch_score=-1,
                     gap_score=-5
                )
                original_indices = \
                    [i for i, (_i2, _i2) in enumerate(alignment) if _i2]

                print (window)
                assert (len(window) == len(indices))

            except Exception as e:
                self.logger.error("Making windows and translating tokenized window and original token indices")
                self.logger.error(str(e))


            yield window, {
                "original_indices":
                    original_indices ,
                "original_text":
                    original_text,
                "window_indices":
                    indices}


    def align_tokens_to_string(self, window_text, tokens_in_window, add=0):
        indices = [0]
        len_prev_substring = 0
        for i, substring in enumerate(tokens_in_window):
            try:
                indices.append(window_text.find(substring, indices[i] + len_prev_substring, len(window_text)))
                assert(len(indices) - 2 == i)
                len_prev_substring = len(substring)
            except Exception as e:
                x = 1

        indices = list( [i + add for i in indices])[1:]
        assert (len(tokens_in_window) == len(indices))

        return indices
