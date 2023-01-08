import json
import os

import falcon

from config import config
from core.event_binding import long_request
from core.rest.Resource import Resource
from core.rest.RestPublisher import RestPublisher
from core.rest.react import react
from core.pathant.Converter import converter
from helpers.cache_tools import configurable_cache
from helpers.list_tools import metaize
from language.text2speech.Txt2Mp3 import get_audio_path


@converter("audio", "rest")
class AudioPublisher(RestPublisher, react):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            resource=Resource(
                title="audiobook",
                type="download",
                path="audiobook",
                route="audiobook",
                access={
                    "fetch": True,
                    "read": True,
                    "upload": True,
                    "correct": True,
                    "delete": True,
                },
            ),
        )

    @configurable_cache(
        filename=config.cache + os.path.basename(__file__),
    )
    def __call__(self, id_meta_mp3):
        yield from id_meta_mp3

    def on_get(self, req, resp, id=None):
        id = id if id else req.params["id"]
        audio_path = get_audio_path(id)
        exists = os.path.exists(
            config.hidden_folder + audio_path.replace(config.hidden_folder, "")
        )
        content = json.dumps(
            {"audio_path": audio_path.replace(config.hidden_folder, ""),
             "exists": exists},

            ensure_ascii=False,
        )
        resp.text = content
        resp.status = falcon.HTTP_OK


    @long_request
    def on_post(self, req, resp, id=None):
        id = req.media
        pipeline = self.ant(
            "feature",
            "audio",
            from_function_only=True,
            layout_model_path=config.layout_model_path,
        )
        id, meta = list(pipeline(metaize([id])))[0]

        resp.status = falcon.HTTP_OK
        resp.text = json.dumps(
            meta["audio_path"].replace(config.hidden_folder, ""), ensure_ascii=False
        )
