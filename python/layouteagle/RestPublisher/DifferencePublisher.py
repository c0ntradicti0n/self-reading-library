from layouteagle.RestPublisher.PdfCssPublisher import PdfCssPublisher
from layouteagle.pathant.Converter import converter

@converter("html", "rest_difference")
class DifferencePublisher(PdfCssPublisher):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, kind = "difference")