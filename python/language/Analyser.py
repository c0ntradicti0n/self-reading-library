import itertools
from collections import defaultdict
import nltk
from core.pathant.PathSpec import PathSpec
from core.pathant.Converter import converter
from nltk.corpus import wordnet
import spacy

SUBJECT = "SUBJECT"
CONTRAST = "CONTRAST"


def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {
        "J": wordnet.ADJ,
        "N": wordnet.NOUN,
        "V": wordnet.VERB,
        "R": wordnet.ADV,
    }

    return tag_dict.get(tag, wordnet.NOUN)


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
        ant = PathAnt()
        gold_span_annotation = ant(
            "span_annotation.collection.fix",
            "span_annotation.collection.span_set",
            service_id="gold_span_annotation",
        )

        extra_antonyms = defaultdict(lambda: set())

        for i, (path, meta) in enumerate(gold_span_annotation([])):
            span_sets = meta["span_set"]
            subjects = [
                " ".join([tw[0] for tw in tag_words])
                for _set in span_sets.values()
                for kind, tag_words in _set
                if kind == SUBJECT
            ]

            for subject_a, subject_b in itertools.permutations(subjects, 2):
                extra_antonyms[subject_a].add(subject_b)

        for path, meta in prediction_metas:
            span_sets = meta["span_set"]
            subjects = [
                " ".join([tw[0] for tw in tag_words])
                for _set in span_sets.values()
                for kind, tag_words in _set
                if kind == SUBJECT
            ]

            contrasts = [
                " ".join([tw[0] for tw in tag_words])
                for _set in span_sets.values()
                for kind, tag_words in _set
                if kind == CONTRAST
            ]

            antonyms_to_look_for = []
            new_links = []
            for i, contrast in enumerate(contrasts):
                try:
                    contrast = self.nlp(contrast)
                except LookupError:
                    import nltk

                    nltk.download("omw-1.4")
                    contrast = self.nlp(contrast)

                for token in contrast:
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

                for (
                    i,
                    (nym_lemma, antonym_lemma),
                    (nym_text, antonym_text),
                ) in antonyms_to_look_for:
                    other_contrasts = [
                        (j, o) for j, o in enumerate(contrasts) if j != i
                    ]
                    for j, other_contrast in other_contrasts:
                        if antonym_text in other_contrast:
                            if not any(
                                l[0] == antonym_text or l[0] == nym_text
                                for l in new_links
                            ):
                                new_links.append(
                                    (
                                        antonym_text,
                                        nym_text,
                                        contrasts[i],
                                        contrasts[j],
                                        nym_lemma,
                                        antonym_lemma,
                                    )
                                )

            meta["analysed_links "] = new_links
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
