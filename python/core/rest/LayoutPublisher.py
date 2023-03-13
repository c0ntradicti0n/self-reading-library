from core.rest.PdfCssPublisher import PdfCssPublisher
from core.pathant.Converter import converter


@converter("html", "rest_layout")
class LayoutPublisher(PdfCssPublisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind="layout", **kwargs)

    def on_post(self, req, resp, id=None, **kwargs):
        print(req, resp)
        id = req.params
