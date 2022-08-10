import json

from config import config
from core.RestPublisher.Resource import Resource
from core.RestPublisher.RestPublisher import RestPublisher


class PdfCssPublisher(RestPublisher):

    def __init__(self,
                 *args, kind= None,
                 **kwargs ):
        super().__init__(*args, **kwargs, resource=Resource(
            title=kind,
            type="html",
            path=kind,
            route=kind,
            access={"fetch": True, "read": True, "upload": True, "correct": True, "delete": True}))
        self.dir = config.markup_dir
        self.kind = kind

    def on_get(self, req, resp, id=None):
        print (f"Annotating {self.kind}")
        self.html_pipeline = self.ant("pdf", "htm")

        try:
            id = json.loads(req.stream.read())
            pdf_s = [f"{config.pdf_dir}/{id}.pdf"]
            self.logger.warning(f"analysing {pdf_s}")
            html_path, html_meta = self(self.html_pipeline, pdf_s)
            css_value, css_meta = self(self.css_pipeline, pdf_s)

            with open(html_path[0], "r") as f:
                html = "".join(f.readlines())

                return {
                    "html": html,
                    "css": css_value[0]
                }

        except Exception as e:
            print(html_path)
            self.logger.error("PDF and CSS combination failed with: " + str(e))
            raise e
