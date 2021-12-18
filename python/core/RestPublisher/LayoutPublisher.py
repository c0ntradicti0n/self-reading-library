from core.RestPublisher.PdfCssPublisher import PdfCssPublisher
from core.pathant.Converter import converter

@converter("html", "rest_layout")
class LayoutPublisher(PdfCssPublisher):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, kind="latex", **kwargs )
