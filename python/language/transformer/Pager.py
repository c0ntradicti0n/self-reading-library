import logging
import sys

import re
import os
import unicodedata
from functools import reduce
from queue import Empty
from pathlib import Path
from typing import Callable
from xml.sax.saxutils import escape, unescape
import chardet
from bs4 import BeautifulSoup, NavigableString, Tag, Comment
from listalign.word_pyalign import align

from config import config
from helpers.list_tools import unique

sys.path.insert(0,"/home/stefan/Programming/Programming/self-reading-library/python")

from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from helpers.latex_tools import latex_replace
from helpers.str_tools import str_list_ascii, str_ascii
from language.nlp_helpers.Regexes import SENTENCE_END_REGEX
from language.nlp_helpers.split_interpunction import split_punctuation
try:
    from language.transformer import ElmoPredict
except Exception as e:
    logging.warning(e, exc_info=True)




import threading


def preprocess_text(texts):
    text = " ".join([word for t in texts for i, word in t])
    text = text.replace("-\n", "")
    text = latex_replace(text)
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

    def run_pdf2htmlEX(self, pdf_path, meta, _html_path=None):
        outputs = {
            "html": "html",  # same looking html
            "reading_order": "wordi",  # numbered word list
            "feat": "feat",  # json with indexed single words as they can be reapplied via css to the html-document
        }

        html_path =  pdf_path + "." + outputs["html"] if not _html_path else _html_path
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
    def flat_visit(self, soup, pos_acc,  collector = lambda: list(), exluded=["head", "style", "script", "svg", "title"]):
        if isinstance(collector, Callable):
            collector = collector()

        pos =  pos_acc[soup.sourceline-1 if soup.sourceline else 0 ] + soup.sourcepos if soup.sourcepos else 0
        added = ""

        for content in soup.contents:

            if isinstance(content, NavigableString):
                if not isinstance(content, Comment):
                    added_temp = added
                    for word in split_punctuation(content, ".!?;,-:", matches=True):

                        if word.strip():
                            collector.append(((pos+1 + len(added_temp),(pos +1+ len(added_temp)+len(word))) , word.strip().replace(str(chr(160)), "][{<<>")))
                        added_temp += str(word)

                added += str(content)#.encode('ascii', 'xmlcharrefreplace').decode()

            elif isinstance(content, Tag):

                if content.name not in exluded:

                    self.flat_visit(content, pos_acc, collector=collector)
                added += str(content)

        return collector


    def insert_z_tags(self, url, html_path, i_word, meta, pdf2htmlEX_wordi_path):
        # repair html
        t = Path(html_path).read_text()
        souper = BeautifulSoup(t,  'html5lib')
        with open(html_path + ".rep", "w") as f:
            f.write(str(souper))

        with open(html_path  + ".rep" ) as f:
            def _(acc, i_line):
                i, line = i_line
                i += 0
                acc[i+1] = (acc[i] if i in acc else 0)  + len(line)
                return acc
            html_lines = f.readlines()
            line_lenghts = (reduce(_, enumerate(html_lines), {0:0}))

        with open(html_path  + ".rep") as f:
            html = f.read()
        soup = BeautifulSoup(html,  'html5lib')

        html_index, l_a = list(zip(*[(pos, word) for pos, word in self.flat_visit(soup, line_lenghts)]))
        word_index, l_b = list(zip(*[ (i, word) for i, word in i_word]))

        alignment, cigar = align(l_a, l_b)

        alignment = unique(alignment, key=lambda l: l[1])
        alignment = unique(alignment, key=lambda l: l[0])

        z_html_path = html_path + ".z.html"
        for (i_a, i_b) in reversed(alignment):
            html_i_a = html_index[i_a]
            i=word_index[i_b]

            start, end = html_i_a
            html = html[:end] + "</z>" + html[end:]
            html= html[:start] + f"<z class='z z{str(hex(i))[2:]}'>" + html[start:]

        with open(z_html_path, "w", encoding="utf-8") as f:
            f.write(html.replace("–", "&#150;").replace("“", "&quot;").replace("”","&quot;" ))
        return z_html_path

    def __call__(self, paths, *args, **kwargs):
        for _pdf_path, meta in paths:
            texts = meta["enumerated_texts"]
            try:
                pdf_path, pdf2htmlEX_wordi_path, _ = self.run_pdf2htmlEX(
                    meta["html_path"], meta
                )
            except Exception:
                self.logger.error("could not transpile pdf to html", exc_info=True)
                continue

            i_word = self.read_i_word(pdf2htmlEX_wordi_path)

            if "url" in meta:
                try:
                    z_path = self.insert_z_tags(meta["url"], meta["original_html_path"], i_word, meta, pdf2htmlEX_wordi_path)
                    os.system(f"mv -f {z_path} " + meta["html_path"])
                    logging.info("Wrote z-etted file now to " + meta["d"])

                except Exception as e:
                    logging.error("Error while Z-etting", exc_info=True)

            # use layout filtered text
            real_tokens = preprocess_text(texts)

            # start iterating on windows of this text
            generator = self.make_tokenized_windows(real_tokens)
            try:
                next(generator)
            except StopIteration:
                logging.error("Windows raised StopIteration")
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

    def read_i_word(self, pdf2htmlEX_wordi_path):
        with open(pdf2htmlEX_wordi_path, "rb") as f:
            content = f.read()
        encoding = chardet.detect(content)["encoding"]
        if not encoding:
            encoding = "utf-8"
        content = content.decode(encoding, errors="ignore")
        content = latex_replace(content)
        # read the text as it is referenced in the html from the reading_order file
        # containing the class index of the tags and the string, may contain
        # errors: f"{index}:{string}"
        lines = [
            ww
            for w in re.split("(?![^:])\n", content)
            for ww in w.split("\n")
            if ww
        ]
        i_word = [
            self.match_reading_order_line(line) for line in lines if len(line) > 2
        ]
        return i_word

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

if __name__ == "__main__":
    from core.standard_converter.Scraper import Scraper
    url = "https://www.differencebetween.com/what-is-the-difference-between-hendravirus-and-nipahvirus/"
    path = "test" + ".pdf"
    html_path = "test.html"
    html_path_ex = "test.pdf.html"

    i_path = path + ".wordi"
    meta = {}
    if not os.path.exists(path):
        Scraper.scrape(url, path)
        os.system(f"mv {path}.htm {html_path}")
    Pager.run_pdf2htmlEX(
        path , meta, _html_path=html_path_ex
    )
    i_word = Pager.read_i_word(i_path)
    Pager.insert_z_tags(url, html_path,i_word, meta,i_path )