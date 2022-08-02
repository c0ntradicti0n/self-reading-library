import json
import os
from pprint import pprint

import falcon

from core import config
from core.RestPublisher.Resource import Resource
from core.RestPublisher.RestPublisher import RestPublisher
from core.RestPublisher.react import react
from core.pathant.Converter import converter
from helpers.cache_tools import configurable_cache
from helpers.list_tools import metaize


@converter("audio", "rest")
class AudioPublisher(RestPublisher, react):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="audiobook",
            type="download",
            path="audiobook",
            route="audiobook",
            access={"fetch": True, "read": True, "upload": True, "correct": True, "delete": True}))

    @configurable_cache(
        filename=config.cache + os.path.basename(__file__),
    )
    def __call__(self, id_meta_mp3):
        yield from id_meta_mp3

    def on_post(self, req, resp, id=None):
        id = req.media
        pipeline = self.ant(
            "feature", "audio",
            from_function_only=True,
            layout_model_path=config.layout_model_path
        )
        id, meta = list(pipeline(metaize([id])))[0]
        compute_path = f"{id}.audiobook"
        os.system(f"touch  {compute_path}")
        if os.path.exists(meta["audio_path"]) and not os.path.exists(compute_path):
            resp.status = falcon.HTTP_OK
            resp.body = json.dumps(
                meta["audio_path"].replace(config.hidden_folder, ""),
                ensure_ascii=False
            )
        else:
            if os.path.exists(compute_path):
                resp.status = falcon.HTTP_404
                resp.headers["Retry-After"] = 20
            else:
                resp.status = falcon.HTTP_404
