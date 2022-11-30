import hashlib
import unittest
from functools import cached_property

import spacy

from helpers.hash_tools import hashval
from spacy_wordnet.wordnet_annotator import WordnetAnnotator

from helpers.span_tools import annotation2span_sets

SUBJECT = "SUBJECT"
CONTRAST = "CONTRAST"


class SuperList(list):
    def __getattr__(self, item):
        try:
            return super().__getattr__(self, item)
        except AttributeError:
            return [getattr(e, item) for e in self]


class Span:

    _nlp = None

    @cached_property
    def nlp(self):
        if not self._nlp:
            Span._nlp = spacy.load("en_core_web_sm")
            Span._nlp.add_pipe("spacy_wordnet", after="tagger")
            try:
                Span._nlp("test this text")
            except LookupError:
                self.post_install()
                Span._nlp("test this text")
        return Span._nlp

    def __post_install(self):
        import nltk

        nltk.download("wordnet")
        nltk.download("omw-1.4")

    def __init__(self, kind, word_tags):
        self.kind = kind
        self.word_tags = word_tags

    @cached_property
    def words(self):
        return [" ".join([tw[0] for tw in self.word_tags])]

    @cached_property
    def text(self):
        return " ".join(self.words)

    @cached_property
    def nlp_id(self):
        return f"{hashval(self.words)}"

    @cached_property
    def lemmas(self):
        return [token.lemma_ for token in self.doc]

    @cached_property
    def doc(self):
        try:
            return self.nlp(self.text)
        except:
            self.__post_install()
            return self.nlp(self.text)

    @cached_property
    def __hash__(self):
        return hashval(self.subjects)

    def __repr__(self):
        return f"{self.kind}: '{self.text}' {self.nlp_id}"

    def __getstate__(self):
        return {0: self.kind, 1: self.word_tags}

    def __setstate__(self, d):
        kind, word_tags = d[0], d[1]
        self.kind = kind
        self.word_tags = word_tags


class DifferenceSpanSet:
    def __init__(self, d):
        if isinstance(d, dict):
            self.span_sets = d
        elif isinstance(d, DifferenceSpanSet):
            self.span_sets = d.span_sets
        else:
            self.span_sets = annotation2span_sets(annotation=d)

    def __getstate__(self):
        return self.span_sets

    def __setstate__(self, span_sets):
        self.span_sets = span_sets

    def _filter_kind(self, kind):
        return SuperList(
            [
                Span(kind=_kind, word_tags=tag_words)
                for _set in self.span_sets.values()
                for _kind, tag_words in _set
                if (kind and _kind == kind) or (kind == None)
            ]
        )

    @cached_property
    def subjects(self):
        return SuperList(
            reversed(sorted(self._filter_kind(SUBJECT), key=lambda s: s.text))
        )

    @cached_property
    def subject_hash(self):
        return hashval(self.subjects)

    @cached_property
    def subject_hash_int(self):
        value = str(self.subjects.text)
        t_value = value.encode("utf8")
        h = hashlib.sha256(t_value)
        h.hexdigest()
        return int(h.hexdigest(), base=32)

    @cached_property
    def contrasts(self):
        return self._filter_kind(CONTRAST)

    @cached_property
    def side_sets(self):
        return SuperList(
            [
                SuperList(
                    [Span(kind=_kind, word_tags=tag_words) for _kind, tag_words in _set]
                )
                for _set in self.span_sets.values()
            ]
        )

    @cached_property
    def kind_sets(self):
        return SuperList([self.subjects, self.contrasts])

    def flat(self):
        return self._filter_kind(kind=None)

    def __contains__(self, item):
        return any(item in span for span in self.flat().text)


class TestSpanMethods(unittest.TestCase):
    v = {
        0: [
            (
                "CONTRAST",
                [
                    ["believes", "B", "CONTRAST", 14],
                    ["in", "I", "CONTRAST", 15],
                    ["an", "I", "CONTRAST", 16],
                    ["omnipresent", "I", "CONTRAST", 17],
                    [",", "I", "CONTRAST", 18],
                    ["omnipotent", "I", "CONTRAST", 19],
                    ["God", "I", "CONTRAST", 20],
                    [",", "I", "CONTRAST", 21],
                    ["the", "I", "CONTRAST", 22],
                    ["Almighty", "I", "CONTRAST", 23],
                    ["Father", "L", "CONTRAST", 24],
                ],
            ),
            ("SUBJECT", [["Catholicism", "U", "SUBJECT", 13]]),
        ],
        1: [
            (
                "CONTRAST",
                [
                    ["does", "B", "CONTRAST", 28],
                    ["not", "I", "CONTRAST", 29],
                    [".", "I", "CONTRAST", 30],
                    ["The", "I", "CONTRAST", 31],
                    ["closest", "I", "CONTRAST", 32],
                    ["thing", "I", "CONTRAST", 33],
                    ["to", "I", "CONTRAST", 34],
                    ["God", "I", "CONTRAST", 35],
                    ["would", "I", "CONTRAST", 36],
                    ["be", "I", "CONTRAST", 37],
                    ["Siddhartha", "I", "CONTRAST", 38],
                    ["Gautama", "I", "CONTRAST", 39],
                    [",", "I", "CONTRAST", 40],
                    ["the", "I", "CONTRAST", 41],
                    ["first", "I", "CONTRAST", 42],
                    ["Buddha", "I", "CONTRAST", 43],
                    ["to", "I", "CONTRAST", 44],
                    ["achieve", "I", "CONTRAST", 45],
                    ["spiritual", "I", "CONTRAST", 46],
                    ["enlightenment", "L", "CONTRAST", 47],
                ],
            ),
            ("SUBJECT", [["Buddhism", "U", "SUBJECT", 27]]),
        ],
    }
    dss = DifferenceSpanSet(v)

    def test_subjects(self):
        self.assertEqual(self.dss.subjects.text, ["Catholicism", "Buddhism"])

    def test_ids(self):
        self.assertEqual(
            self.dss.subjects.nlp_id,
            [
                "e3ef22cc849bb1c42487ad348e9a8968c5e2bc3704be4b06080dc3f54b880e3c",
                "61ec49b2f01f80373b48baac46459bf964a638374606264bf8701b94884df7f6",
            ],
        )

    def test_subj_hash(self):
        self.assertEqual(
            self.dss.subject_hash,
            "530147de47c462a1ed178ac02794db62f1849d3328b05276a9944c28cc5bde72",
        )

    def test_subj_hash_int(self):
        self.assertEqual(
            self.dss.subject_hash_int,
            605655766414173305614492906248267245040171940863844408278379738501985147138083118269722709201217,
        )

    def test_lemmas(self):
        self.assertEqual(
            self.dss.contrasts.lemmas,
            [
                [
                    "believe",
                    "in",
                    "an",
                    "omnipresent",
                    ",",
                    "omnipotent",
                    "God",
                    ",",
                    "the",
                    "Almighty",
                    "Father",
                ],
                [
                    "do",
                    "not",
                    ".",
                    "the",
                    "close",
                    "thing",
                    "to",
                    "God",
                    "would",
                    "be",
                    "Siddhartha",
                    "Gautama",
                    ",",
                    "the",
                    "first",
                    "Buddha",
                    "to",
                    "achieve",
                    "spiritual",
                    "enlightenment",
                ],
            ],
        )


if __name__ == "__main__":
    unittest.main()
