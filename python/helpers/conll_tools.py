import logging
import os

import nltk

from language.span.DifferenceSpanSet import Span
from language.transformer.core.bio_annotation import conll_line


def conll2annotation(content):
    cols = list(
        zip(
            *[
                m.groups()
                for i, line in enumerate(content.split("\n"))
                if line and (m := conll_line.match(line.replace("\t", "  ")))
            ]
        )
    )
    result = {"annotation": list(zip(cols[0], cols[-1])), "pos": cols[1]}
    return result


def conll_file2annotation(pickle_path):
    with open(pickle_path, errors="ignore") as f:
        content = f.read()
    result = conll2annotation(content)
    return result


def annotation2conll_file(annotation, filename, new_folder, pos=None):
    if not pos:
        tags, words = list(zip(*annotation))
        logging.info(words)
        try:
            pos = nltk.pos_tag(words)
        except LookupError:
            nltk.download("averaged_perceptron_tagger")
            pos = nltk.pos_tag(words)
            pos = [p for w, p in pos]
    logging.info(pos)

    pos_tags = [
        p if "-" not in tag else tag[:2] + p for (word, tag), p in zip(annotation, pos)
    ]
    content = "\n".join("\t".join(t) for t in zip(words, pos, pos_tags, tags))
    if not os.path.isdir(new_folder):
        os.makedirs(new_folder)
    new_path = new_folder + "/" + filename
    with open(new_path, "w") as f:
        f.write(content)
    return new_path
