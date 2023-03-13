from ant import Ant
from core.pathant.Converter import converter
from core.pathant.PathSpec import cache_flow
import itertools
from config import config


@converter("prediction", "txt")
class Prediction2Text(Ant):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, cached=cache_flow.iterate, **kwargs)
        self.n = n
        self.debug = debug

    def __call__(self, iterator, *args, **kwargs):
        for prediction_metas_per_document, meta in iterator:
            all_text = []
            for prediction, meta in prediction_metas_per_document:
                label_box_text = list(
                    zip(
                        prediction["labels"],
                        prediction["bbox"],
                        prediction["df"].text.to_list()[0],
                    )
                )
                label_groups = [
                    (k, list(g))
                    for k, g in itertools.groupby(
                        list(sorted(label_box_text, key=lambda lbt: lbt[0])),
                        key=lambda l_b_t: l_b_t[0],
                    )
                ]
                label_groups = [g for g in label_groups if g[0] in config.TEXT_LABELS]
                label_box_text_sorted = [
                    list(sorted(list(g), key=lambda x: x[1][0] * x[1][1]))
                    for k, g in label_groups
                ]
                text = [l_b_t[2] for l in label_box_text_sorted for l_b_t in l]

                all_text.extend(text)

            meta["reading_order"] = label_box_text_sorted
            yield all_text, meta
