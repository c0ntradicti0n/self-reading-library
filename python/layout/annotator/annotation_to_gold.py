from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from core.rest.RestPublisher import RestPublisher
from core.rest.RestPublisher import Resource
from core.rest.react import react
from core.event_binding import queue_iter, RestQueue, queue_put
from layout.model_helpers import changed_labels
import logging


AnnotatedToGoldQueueRest = RestQueue(
    service_id="annotation_to_gold", update_data=changed_labels
)


@converter(
    "annotation.collection",
    "reading_order",
)
class Annotator(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, prediction_metas, *args, **kwargs):
        for prediction_meta, meta in prediction_metas:

            if "from_function_only" in self.flags and self.flags["from_function_only"]:
                queue_put(
                    service_id=self.flags["service_id"],
                    gen=(p_m for p_m in meta["layout_predictions"]),
                )

                yield from meta["layout_predictions"]
            else:
                try:
                    for _p_m in queue_iter(
                        service_id="annotation",
                        gen=(p_m for p_m in prediction_meta),
                        single=self.flags["from_function_only"]
                        if "from_function_only" in self.flags
                        else False,
                    ):
                        yield _p_m
                except RuntimeError as e:
                    logging.error("annotating next document", e)
