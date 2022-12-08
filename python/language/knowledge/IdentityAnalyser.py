import itertools

from core.pathant.PathSpec import PathSpec
from core.pathant.Converter import converter
from helpers.list_tools import nest
from language.span.DifferenceSpanSet import Span, SuperList
from helpers.list_tools import unique

SUBJECT = "SUBJECT"
CONTRAST = "CONTRAST"


@converter(
    "span_annotation.collection.span_set",
    "span_annotation.collection.identity",
)
class AnnotationAnalyser(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, prediction_metas, *args, **kwargs):
        from core.pathant.PathAnt import PathAnt

        ant = PathAnt()
        all_subjects = list(
            itertools.chain(
                *map(
                    lambda t: t[1]["span_set"].subjects,
                    ant(
                        "span_annotation.collection.fix",
                        "span_annotation.collection.span_set",
                        service_id="gold_span_annotation",
                    )([]),
                )
            )
        )

        pre_group = list(
            sorted(
                list(
                    (
                        itertools.chain(
                            *map(
                                lambda s: [(s.text, s)]
                                + list(map(lambda d: (d, s), s.derived)),
                                all_subjects,
                            )
                        )
                    )
                ),
                key=lambda x: x[0],
            )
        )
        groups = {
            k: list(map(lambda x: x[1], unique(list(v), key=lambda e: e[1].nlp_id)))
            for k, v in itertools.groupby(pre_group, key=lambda t: t[0])
        }

        clusters = [v for k, v in groups.items() if len(v) > 1]

        identity_clusters = unique(
            clusters, key=lambda c: str(list(sorted(n.nlp_id for n in c)))
        )

        id2span = {s.nlp_id: c for c in identity_clusters for s in c}
        for path, meta in prediction_metas:
            subjects = meta["span_set"].subjects
            new_links = []
            for subject in subjects:
                if subject.nlp_id in id2span:
                    new_links.extend(id2span[subject.nlp_id])

            meta["identity_links"] = unique(new_links, key=lambda s: s.nlp_id)
            yield path, meta


if __name__ == "__main__":
    from helpers.hash_tools import hashval

    from config.ant_imports import *

    ant = PathAnt()

    def node_id(kind, a_num, s_num, words):
        return f"{hashval(words)}"  # f"{kind}+{a_num}-{s_num}"

    gold_span_annotation = ant(
        "span_annotation.collection.fix",
        "span_annotation.collection.linked",
        service_id="gold_span_annotation",
    )

    for i, (path, meta) in enumerate(gold_span_annotation([])):
        nodes = []
        edges = []
        span_sets = meta["span_set"]
        if meta["analysed_links "]:
            print(meta["analysed_links "])
