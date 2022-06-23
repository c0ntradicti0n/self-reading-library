import json
from pprint import pprint

from core import config
from core.RestPublisher.Resource import Resource
from core.RestPublisher.RestPublisher import RestPublisher
from core.pathant.Converter import converter
from helpers.cache_tools import uri_with_cache
from language.transformer.FilterAlignText import FilterAlignTextPager

@converter("reading_order.filter_align_text.difference", "rest")
class DifferenceAnnotationPublisher(RestPublisher):

    def __init__(self,
                 *args,
                 **kwargs ):
        super().__init__(*args, **kwargs, resource=Resource(
            title="difference_annotation",
            type="difference_annotation",
            path="difference_annotation",
            route="difference_annotation",
            access={"fetch": True, "read": True, "upload": True, "correct": True, "delete": True}))
        self.dir = config.markup_dir
        self.kind = "difference_annotation"

    def on_post(self, req, resp, id=None):
        print (f"Annotating {self.kind}")
        pprint(req)
        pprint(resp)
        id, text, pdf_path = req.media
        pipeline = self.ant("text", "reading_order.filter_align_text.difference")
        result = pipeline([pdf_path, {'filter_text': text}])
        return result


