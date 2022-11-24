import itertools
from collections import defaultdict

import spacy
from nltk.corpus.reader import Lemma

from core.pathant.PathSpec import PathSpec
from core.pathant.Converter import converter

SUBJECT = "SUBJECT"
CONTRAST = "CONTRAST"


@converter(
    "span_annotation.collection.span_set",
    "span_annotation.collection.analysed",
)
class AnnotationAnalyser(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.nlp = spacy.load("en_core_web_sm")

        self.nlp.add_pipe("spacy_wordnet", after="tagger")


    def __call__(self, prediction_metas, *args, **kwargs):
        from core.pathant.PathAnt import PathAnt

        ant = PathAnt()
        gold_span_annotation = ant(
            "span_annotation.collection.fix",
            "span_annotation.collection.span_set",
            service_id="gold_span_annotation",
        )

        extra_antonyms = defaultdict(lambda: set())

        for i, (path, meta) in enumerate(gold_span_annotation([])):
            span_set = meta["span_set"]

            for subject_a, subject_b in itertools.permutations(
                span_set.subjects.text, 2
            ):
                extra_antonyms[subject_a].add(subject_b)

        for path, meta in prediction_metas:
            span_sets = meta["span_set"]

            antonyms_to_look_for = []
            new_links = []
            for i, contrast in enumerate(span_sets.contrasts):
                for token in contrast.doc:
                    antonyms = [
                        (i, (l, a), (str(l.name()), str(a.name())))
                        for l in token._.wordnet.lemmas()
                        if (a_s := l.antonyms())
                        for a in a_s
                    ]
                    antonyms_to_look_for.extend(antonyms)

                    if token.text in extra_antonyms:
                        antonyms_to_look_for.extend(
                            [
                                (i, (token.text, o), (token.text, o))
                                for o in extra_antonyms[token.text]
                            ]
                        )

                # exclude if explained opposites appear in explanation
                antonyms_to_look_for = [
                    a
                    for a in antonyms_to_look_for
                    if not any(aa in span_sets.subjects.text for aa in a[-1])
                ]

                for (
                    i,
                    (nym_lemma, antonym_lemma),
                    (nym_text, antonym_text),
                ) in antonyms_to_look_for:
                    other_contrasts = [
                        (j, o) for j, o in enumerate(span_sets.contrasts) if j != i
                    ]
                    for j, other_contrast in other_contrasts:

                        if isinstance(antonym_lemma, Lemma):
                            antonym_lemma_text = antonym_lemma.name()
                        elif isinstance(antonym_lemma, str):
                            antonym_lemma_text = antonym_lemma

                        # TODO use right POS-LEMMA?
                        if antonym_lemma_text in other_contrast.lemmas:
                            if not any(
                                l[0] == antonym_text or l[0] == nym_text
                                for l in new_links
                            ):
                                new_links.append(
                                    (
                                        antonym_text,
                                        nym_text,
                                        span_sets.contrasts[i],
                                        span_sets.contrasts[j],
                                        nym_lemma,
                                        antonym_lemma,
                                    )
                                )

            meta["analysed_links"] = new_links
            yield path, meta


if __name__ == "__main__":
    from helpers.hash_tools import hashval

    from config.ant_imports import *

    ant = PathAnt()

    def node_id(kind, a_num, s_num, words):
        return f"{hashval(words)}"  # f"{kind}+{a_num}-{s_num}"

    gold_span_annotation = ant(
        "span_annotation.collection.fix",
        "span_annotation.collection.analysed",
        service_id="gold_span_annotation",
    )

    for i, (path, meta) in enumerate(gold_span_annotation([])):
        nodes = []
        edges = []
        span_sets = meta["span_set"]
        if meta["analysed_links "]:
            print(meta["analysed_links "])
