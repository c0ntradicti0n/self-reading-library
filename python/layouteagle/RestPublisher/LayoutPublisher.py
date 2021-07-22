from layouteagle.RestPublisher.PdfCssPublisher import PdfCssPublisher
from layouteagle.pathant.Converter import converter

@converter("html", "rest_layout")
class LayoutPublisher(PdfCssPublisher):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, kind="layout", **kwargs )
