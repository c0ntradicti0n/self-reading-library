import os

from config import config
from core.pathant.Converter import converter
from core.pathant.Filter import existing_in_dataset_or_database
from core.pathant.PathSpec import PathSpec
from core.event_binding import queue_iter, RestQueue, q, d
from helpers.cache_tools import configurable_cache
import logging

from helpers.conll_tools import conll_file2annotation
from helpers.span_tools import annotation2span_sets

AnnotationSpanToGoldQueueRest = RestQueue(
    service_id="gold_span_annotation", update_data=lambda x: print(x), rated_queue=True
)


@converter(
    "span_annotation.collection",
    "span_annotation.collection.silver",
)
class AnnotationSpanLoader(PathSpec):
    @configurable_cache(
        config.cache + os.path.basename(__file__),
        from_path_glob=config.ELMO_DIFFERENCE_COLLECTION_PATH + "/*.conll",
        filter_path_glob=existing_in_dataset_or_database("/*.conll"),
    )
    def __call__(self, prediction_metas, *args, **kwargs):
        # all span_annotation are coming from the cache, that is read from globbing the files
        # so nothing to do here
        for conll3_path, meta in prediction_metas:
            with open(conll3_path) as f:
                f.read()


@converter(
    "span_annotation.collection.silver",
    "span_annotation.collection.gold",
)
class AnnotatorUnpacker(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, prediction_metas, *args, **kwargs):
        for conll_path, meta in prediction_metas:
            result = conll_file2annotation(conll_path)
            yield conll_path, result


@converter(
    "span_annotation.collection.gold",
    "span_annotation.collection.platinum",
)
class AnnotatorRate(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, prediction_metas, *args, **kwargs):
        self.service = self.flags["service_id"]

        try:
            for _p_m in queue_iter(
                service_id=self.service,
                gen=(p_m for p_m in prediction_metas),
                single=False,
            ):
                value, meta = _p_m
                try:
                    rating_trial, rating_score = d[self.service].scores(value)
                except IndexError:
                    rating_trial = 0
                    rating_score = 0.0
                    logging.error(f"Scores not found for {value}, {self.service}")

                if rating_trial > config.MIN_CAPTCHA_TRIALS:
                    yield _p_m
                else:
                    q[self.service].put(self.service, _p_m)
                    q[self.service].rate(value, rating_score)
        except StopIteration:
            self.logger.error(
                f"End of spans for bathing in gold for {self.flags['service_id']=}"
            )


@converter(
    "span_annotation.collection.platinum",
    "span_annotation.collection.fix",
)
class AnnotatorSaveFinal(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, prediction_metas, *args, **kwargs):
        self.service = self.flags["service_id"]

        for path, meta in prediction_metas:
            filename = path.replace(config.ELMO_DIFFERENCE_COLLECTION_PATH, "")

            new_folder = config.GOLD_DATASET_PATH + "/" + self.flags["service_id"] + "/"
            if meta["rating_score"] == -1:
                new_folder = (
                    config.TRASH_DATASET_PATH + "/" + self.flags["service_id"] + "/"
                )

            if not os.path.isdir(new_folder):
                os.makedirs(new_folder)

            words, tags = list(zip(*meta["annotation"]))
            pos = meta["pos"]
            pos_tags = [
                p if "-" not in tag else tag[:2] + p
                for (word, tag), p in zip(meta["annotation"], pos)
            ]
            content = "\n".join("\t".join(t) for t in zip(words, pos, pos_tags, tags))
            if not os.path.isdir(new_folder):
                os.makedirs(new_folder)
            new_path = new_folder + "/" + filename
            with open(new_path, "w") as f:
                f.write(content)
            yield new_path, meta


@converter(
    "span_annotation.collection.fix",
    "span_annotation.collection.load",
)
class AnnotationSpanLoader(PathSpec):
    @configurable_cache(
        config.cache + os.path.basename(__file__),
        from_path_glob=lambda self: config.GOLD_DATASET_PATH
        + "/"
        + self.flags["service_id"]
        + "/**.conll",
    )
    def __call__(self, prediction_metas, *args, **kwargs):
        raise NotImplementedError("Should come from cache")


@converter(
    "span_annotation.collection.load",
    "span_annotation.collection.span_set",
)
class AnnotationSpanSet(PathSpec):
    def __call__(self, prediction_metas, *args, **kwargs):
        for path, meta in prediction_metas:
            self.logger.debug(f"Reading annotation from '{path}'")
            result = conll_file2annotation(path)
            self.logger.debug(f"Read '{result}'")
            result["span_set"] = annotation2span_sets(result["annotation"])
            yield path, result
