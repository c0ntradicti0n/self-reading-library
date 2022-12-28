import hashlib
import itertools
import json
import logging
import unittest
from functools import cached_property

import nltk
import spacy
from franz.openrdf.vocabulary import XMLSchema
from more_itertools import pairwise
from nltk import SnowballStemmer

from core.database import BASE
from helpers.list_tools import unique
from helpers.cache_tools import compressed_pickle, decompress_pickle
from helpers.hash_tools import hashval
from spacy_wordnet.wordnet_annotator import WordnetAnnotator

from helpers.span_tools import annotation2span_sets


SUBJECT = "SUBJECT"
CONTRAST = "CONTRAST"
stemmer = SnowballStemmer("english")
lemma = nltk.wordnet.WordNetLemmatizer()


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
            Span._nlp.disable_pipes("tok2vec", "parser", "ner")

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

    def __init__(self, kind, word_tags=None):
        self.kind = kind
        if isinstance(word_tags, str):
            words = word_tags.split(" ")
            self.word_tags = [
                [
                    w,
                    "B" if i == 0 else ("I" if i < len(words) - 1 else "L"),
                    kind,
                ]
                for i, w in enumerate(words)
            ]
        else:
            self.word_tags = word_tags

    def wordnet_lemmas(self):
        return [token._.wordnet.lemmas() for token in self.doc]

    @cached_property
    def words(self):
        return [" ".join([tw[0] for tw in self.word_tags])]

    @cached_property
    def text(self):
        return " ".join(self.words)

    def stems(self):
        return [lemma.lemmatize(w) for w in self.words]

    def same_root(self, other):
        return any(l in self.derived for l in other.lemmas)

    @cached_property
    def derived(self):
        return list(
            itertools.chain(
                *[
                    map(lambda d: d._name, l.derivationally_related_forms())
                    for l in self.doc[0]._.wordnet.lemmas()
                ]
            )
        )

    @cached_property
    def nlp_id(self):
        return f"{hashval(self.stems())}"

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

    def __eq__(self, other):
        return self.word_tags == other.word_tags and self.kind == other.kind

    def __getstate__(self):
        return {0: self.kind, 1: self.word_tags}

    def __setstate__(self, d):
        kind, word_tags = d[0], d[1]
        self.kind = kind
        self.word_tags = word_tags

    SUBJECTS_URI = f"{BASE}{SUBJECT}"
    CONTRASTS_URI = f"{BASE}{CONTRAST}"

    FTS_TEXT = f"{BASE}text"
    FTS_LEMMA = f"{BASE}lemma"
    WORD_TAGS = f"{BASE}word_tags"

    FTS_Uris = [FTS_TEXT, FTS_LEMMA]

    def add_graph_literal(self, conn):
        Text = conn.createURI(self.FTS_TEXT)
        Lemma = conn.createURI(self.FTS_LEMMA)
        WordTags = conn.createURI(self.WORD_TAGS)
        k = conn.createURI(f"{BASE}{self.nlp_id}")
        t = conn.createLiteral(self.text, XMLSchema.STRING)
        l = conn.createLiteral(json.dumps(self.lemmas), XMLSchema.STRING)
        wt = conn.createLiteral(json.dumps(self.word_tags))

        try:
            conn.addTriple(k, Text, t)
        except Exception as e:
            logging.error("Error writing text in graphdb")
        try:
            conn.addTriple(k, Lemma, l)
        except Exception as e:
            logging.error("Error writing lemma in graphdb")
        try:
            conn.addTriple(k, WordTags, wt)
        except Exception as e:
            logging.error("Error writing word_tags in graphdb")

        return k

    def add_link(self, kind, other, conn):
        Kind = conn.createURI(f"{BASE}{kind}")

        a = self.add_graph_literal(conn)
        b = other.add_graph_literal(conn)

        conn.addTriple(a, Kind, b)
        return [a, b]


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
    def hash(self):
        return hashval(self.flat())

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

    @cached_property
    def n_arity(self):
        ks = list(set(map(len, self.kind_sets)))
        if len(ks) != 1:
            return None
        return ks[0]

    @cached_property
    def valid(self):
        return self.n_arity not in [1, None]

    def flat(self):
        return self._filter_kind(kind=None)

    def __contains__(self, item):
        return any(item in span for span in self.flat().text)

    DIFFERENCE = f"{BASE}difference"
    SPAN_SETS = f"{BASE}span_sets"

    def add_graph_db(self, conn):
        d = conn.createURI(self.DIFFERENCE)
        ss = conn.createURI(self.SPAN_SETS)

        sides = []
        for spans in self.kind_sets:
            for a, b in pairwise(spans):
                sides += a.add_link(a.kind, b, conn)

        for a, b in zip(*self.kind_sets):
            sides += a.add_link("explains", b, conn)

        sides = unique(sides)
        id = conn.createLiteral(self.hash, XMLSchema.STRING)
        span_sets = conn.createLiteral(json.dumps(self.span_sets), XMLSchema.STRING)

        for node in sides:
            conn.addTriple(id, d, node)
        conn.addTriple(id, ss, span_sets)


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

    def test_pickle(self):
        self.assertEqual(
            decompress_pickle(compressed_pickle(TestSpanMethods.dss)).subjects,
            self.dss.subjects,
        )

    def test_subjects(self):
        self.assertEqual(self.dss.subjects.text, ["Catholicism", "Buddhism"])

    def test_ids(self):
        self.assertEqual(
            self.dss.subjects.nlp_id,
            [
                "eba3e5c681e84bc26e3a3544bf9b0a37bbf627cdbc60e2afb9ff081d97718660",
                "ec9e19bda8bfce78abb29dee3228fa696681b07f759d836770989b6c5e2b5375",
            ],
        )

    def test_subj_hash(self):
        self.assertEqual(
            self.dss.subject_hash,
            "488dbb73798839778a1f3f0078b63025cb9760f13fc5be1d8ec11de60d7f5edb",
        )

    def test_subj_hash_int(self):
        self.assertEqual(
            self.dss.subject_hash_int,
            605655766414173305614492906248267245040171940863844408278379738501985147138083118269722709201217,
        )

    def test_truth(self):
        errors = []
        for _a, _b in [("truth", "true"), ("valid", "validity"), ("proof", "prove")]:
            a = Span(SUBJECT, _a)
            b = Span(SUBJECT, _b)
            print(a.stems(), b.stems())
            if not a.same_root(b):

                errors.append((a, b))
        self.assertEqual(errors, [], "not equal")

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

    def test_valid(self):
        self.assertEqual( True, self.dss.valid)



if __name__ == "__main__":
    unittest.main()
