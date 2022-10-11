from core.pathant.Converter import converter
from core.rest.RestPublisher import RestPublisher
from core.rest.RestPublisher import Resource
from core.rest.react import react
from core.event_binding import queue_iter
from config import config
import logging
import os

if not os.path.isdir(config.PDF_UPLOAD_DIR):
    os.makedirs(config.PDF_UPLOAD_DIR)


@converter("reading_order", "upload_annotation")
class UploadAnnotator(RestPublisher, react):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            resource=Resource(
                title="Upload_Annotation",
                type="upload_annotation",
                path="upload_annotation",
                route="upload_annotation",
                access={
                    "add_id": True,
                    "fetch": True,
                    "read": True,
                    "upload": True,
                    "correct": True,
                    "delete": True,
                },
            ),
        )

    def __call__(self, prediction_metas, *args, **kwargs):
        for prediction_meta, meta in prediction_metas:
            try:
                for _p_m in queue_iter(
                    service_id="upload_annotation", gen=(p_m for p_m in prediction_meta)
                ):
                    print(f"yielding annotated {_p_m}")
                    yield _p_m
            except RuntimeError as e:
                logging.info("annotating next uploaded document")
