import json

from core import config
from core.RestPublisher.Resource import Resource
from core.RestPublisher.RestPublisher import RestPublisher
from helpers.cache_tools import uri_with_cache


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

        # pdf -> reading_order
        #     -> reading_order.page
        #     -> reading_order.page.difference
        #     -> reading_order.page.difference
        #     -> reading_order.difference
        #     -> css.difference

    @uri_with_cache
    def on_post(self, req, resp):
        print (f"KIN{self.kind}")

        self.html_pipeline = self.ant("pdf", "htm")
        self.css_pipeline = self.ant("pdf", f"css.{self.kind}", via='annotation')

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