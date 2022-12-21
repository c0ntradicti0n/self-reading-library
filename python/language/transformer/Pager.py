import re
import os
import unicodedata
from queue import Empty
from pathlib import Path

import chardet
from config import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from helpers.str_tools import str_list_ascii
from language.nlp_helpers.Regexes import SENTENCE_END_REGEX
from language.nlp_helpers.split_interpunction import split_punctuation
from language.transformer import ElmoPredict

import threading


def preprocess_text(texts):
    text = " ".join([word for t in texts for i, word in t])
    text = text.replace("-\n", "")
    text = unicodedata.normalize("NFKD", text)
    real_tokens = split_punctuation(text, ".,:!?;")
    return real_tokens


@converter("reading_order", "reading_order.page")
class Pager(PathSpec):
    def __init__(self, *args, max_window=200, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_window = max_window

    WORD_I_LINE_REGEX = re.compile(r"^(\d+):(.*)", re.DOTALL)

    def match_reading_order_line(self, line):
        m = Pager.WORD_I_LINE_REGEX.match(line)
        if not m:
            self.logger.error(f"No match line in reading_order! for {line}")
            return -1, line
        return int(m.group(1)), m.group(2)

    def run_pdf2htmlEX(self, pdf_path, meta):
        outputs = {
            "html": "html",  # same looking html
            "reading_order": "wordi",  # numbered word list
            "feat": "feat",  # json with indexed single words as they can be reapplied via css to the html-document
        }

        html_path = pdf_path + "." + outputs["html"]
        pdf2htmlEX_wordi_path = pdf_path + "." + outputs["reading_order"]
        feat_path = pdf_path + "." + outputs["feat"]

        if not (
            os.path.exists(pdf2htmlEX_wordi_path)
            and os.path.exists(html_path)
            and os.path.exists(feat_path)
        ):
            self.logger.warning(f"working on {pdf_path}")
            self.pdf2htmlEX(pdf_path, html_path)
        else:
            self.logger.warning(f"pdf2htmlEX has run yet on {pdf_path}")

        meta["pdf2htmlEX.html"] = html_path
        meta["html_path"] = html_path
        meta["pdf_path"] = pdf_path
        meta["pdf2htmlEX_wordi_path"] = pdf2htmlEX_wordi_path
        meta["feat_path"] = feat_path

        return (html_path, pdf2htmlEX_wordi_path, feat_path)

    def __call__(self, paths, *args, **kwargs):
        for _pdf_path, meta in paths:
            texts = meta["enumerated_texts"]
            try:
                pdf_path, pdf2htmlEX_wordi_path, _ = self.run_pdf2htmlEX(
                    meta["html_path"], meta
                )
            except Exception as e:
                self.logger.error("could not transpile pdf to html", exc_info=True)
                continue

            # read the text as it is referenced in the html from the reading_order file
            # containing the class index of the tags and the string, may contain
            # errors: f"{index}:{string}"
            with open(pdf2htmlEX_wordi_path, "rb") as f:
                content = f.read()

            encoding = chardet.detect(content)["encoding"]
            if not encoding:
                encoding = "utf-8"
            lines = [
                ww
                for w in re.split(
                    "(?![^:])\n", content.decode(encoding, errors="ignore")
                )
                for ww in w.split("\n")
                if ww
            ]

            i_word = [
                self.match_reading_order_line(line) for line in lines if len(line) > 2
            ]

            # use layout filtered text
            real_tokens = preprocess_text(texts)

            # start iterating on windows of this text
            generator = self.make_tokenized_windows(real_tokens)
            next(generator)
            threading.Thread(
                target=self.window_thread,
                args=(
                    generator,
                    meta,
                    i_word,
                ),
                name="make text windows",
            ).start()
            meta["texts"] = texts
            yield _pdf_path, meta

    def window_thread(self, generator, meta, i_word):
        i = 0
        prev_window = ""
        last_annotated_token = 0
        while True:
            try:
                last_annotated_token = ElmoPredict.q1[self.flags["service_id"]].get(
                    timeout=369
                )
            except Empty:
                self.logger.error("Left windowing thread, deadlock")
                break

            try:
                ElmoPredict.q1[self.flags["service_id"]].task_done()
            except Exception as e:
                self.logger.error("Tasks were already done, retrying")
                break

            try:

                window, window_meta = generator.send(last_annotated_token)

            except StopIteration as e:
                self.logger.info("eof")
                ElmoPredict.q2[self.flags["service_id"]].put((None, None))
                break

            window = str_list_ascii(window)
            try:
                self.logger.info(" ".join([t for t in window]))
            except:
                self.logger.info("Encoding Error")

            if len(window) == 0:
                self.logger.info("finishing?")
                return

            ElmoPredict.q2[self.flags["service_id"]].put(
                (
                    window,
                    {
                        **window_meta,
                        "i_word": i_word,
                        **meta,
                        "doc_id": meta["pdf_path"],
                    },
                )
            )

            # last_annotated_token = ElmoPredict.consumed_tokens_queue.get()

            # determine if we annotated some text with a unrealistic number if text
            # windows
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
        sent = []
        windowing = True
        start_i2 = 0
        sentence_marks = [0] + [
            i + 1 for i, w in enumerate(real_tokens) if SENTENCE_END_REGEX.match(w)
        ]

        consumed_tokens = 0
        loop_count = 0

        while windowing:

            if consumed_tokens:
                try:
                    start_i2 = consumed_tokens + start_i2 + 1

                except KeyError:
                    self.logger.error("error computing new beginning")
                    return
            else:
                pass

            start_i2 = min(sentence_marks, key=lambda _m: abs(_m - start_i2))
            rest_text = real_tokens[start_i2 : start_i2 + 300]

            if len(rest_text) == 0:
                return

            j = min(sentence_marks, key=lambda _m: abs(_m - self.max_window))
            window = rest_text[:j]

            if not window or str(window) in sent:
                self.logger.info("Zero or repeating text, resetting window")
                window = rest_text[: self.max_window]

            sent.append(str(window))
            consumed_tokens = yield window, {}

            if consumed_tokens == 0 and loop_count > 0:
                consumed_tokens = 123
                self.logger.info("consuming more than 0 tokens")

            loop_count += 1

    def pdf2htmlEX(self, pdf_filename, html_filename):
        assert pdf_filename.endswith(".pdf")
        self.logger.info(f"converting pdf {pdf_filename} to html {html_filename} ")

        origin = Path(os.getcwd()).resolve()
        destination = Path(html_filename).resolve()
        rel_html_path = os.path.relpath(destination, start=origin)
        return_code = os.system(
            f"{config.pdf2htmlEX} "
            f"--space-as-offset 1 "
            f"--decompose-ligature 1 "
            f"--optimize-text 1 "
            f"--fit-width {config.reader_width}  "
            f'"{pdf_filename}" "{rel_html_path}"'
        )

        if return_code != 0:
            if os.path.exists(pdf_filename):
                raise RuntimeError(
                    f"{pdf_filename} could not be converted to html back"
                )
            else:
                raise FileNotFoundError(f"{pdf_filename} was not found")
