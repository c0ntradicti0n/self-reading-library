import json
from pprint import pprint

import falcon

from python.layouteagle import config
from python.layouteagle.RestPublisher.Resource import Resource
from python.layouteagle.RestPublisher.RestPublisher import RestPublisher
from python.layouteagle.RestPublisher.react import react
from python.helpers.cache_tools import uri_with_cache
from python.layouteagle.pathant.Converter import converter

from python.layouteagle.StandardConverter.Wordi2Css import Wordi2Css
from python.nlp.TransformerStuff.ElmoDifference import ElmoDifference
from python.nlp.TransformerStuff.Pager import Pager
from python.nlp.TransformerStuff.UnPager import UnPager

@converter("html", "rest_markup")
class MarkupPublisher(RestPublisher, react) :
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="Markup",
            type = "html",
            path="markup",
            route="markup",
            access={"fetch": True, "read": True, "upload":True, "correct":True, "delete":True}))
        self.dir = config.markup_dir

    @uri_with_cache
    def on_post(self, req, resp):
        try:

            id = json.loads(req.stream.read())
            print(str(type(id)))
            print(id)

            with open(f"{config.markup_dir}/{id}.{config.markup_suffix}", "r") as f:
                html = list ("".join(f.readlines()))

                pdf_s = [f"{config.pdf_dir}/{id}.pdf"]
                self.logger.warning(f"analysing {pdf_s}")

                html_value, html_meta = list(
                    zip(
                        *list(
                            self.ant("pdf", "htm")
                            ([(pdf, {})
                              for pdf
                              in pdf_s]))))

                # pdf -> wordi
                #     -> wordi.page
                #     -> wordi.page.difference
                #     -> wordi.page.difference
                #     -> wordi.difference
                #     -> css.difference
                css_value, html_meta = list(
                    zip(
                        *list(
                            self.ant("pdf", "css.difference")
                            ([(pdf, {})
                              for pdf
                              in pdf_s]))))

                pprint (css_value)


        except Exception as e:

            self.logger.error("markup backend is called badly")
            raise e
