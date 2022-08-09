from core.pathant.Converter import converter
from core.RestPublisher.RestPublisher import RestPublisher
from core.RestPublisher.RestPublisher import Resource
from core.RestPublisher.react import react
from core.event_binding import queue_iter, RestQueue, queue_put
from layout.model_helpers import repaint_image_from_labels, changed_labels
import logging



AnnotationQueueRest = RestQueue(
    service_id="annotation",
    update_data=changed_labels
)



@converter("reading_order", ["annotation", "upload_annotation"])
class Annotator(RestPublisher, react):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="Annotation",
            type="annotation",
            path="annotation",
            route="annotation",
            access={"add_id": True, "fetch": True, "read": True, "upload": True, "correct": True, "delete": True}))


    def __call__(self, prediction_metas, *args, **kwargs):
        for prediction_meta, meta in prediction_metas:

            if 'from_function_only' in self.flags and self.flags['from_function_only']:
                queue_put(
                    service_id=self.flags['service_id'],
                    gen=(p_m for p_m in meta['layout_predictions'])
                )

                yield from meta['layout_predictions']
            else:
                try:
                    for _p_m in queue_iter(
                            service_id="annotation",
                            gen=(p_m for p_m in prediction_meta),
                            single=self.flags['from_function_only'] if 'from_function_only' in self.flags else False
                     ):
                        yield _p_m
                except RuntimeError as e:
                    logging.error("annotating next document", e)
