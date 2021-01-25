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
from python.layouteagle.pathant.PathAnt import PathAnt
from python.nlp.TransformerStuff.ElmoDifference import ElmoDifference
from python.nlp.TransformerStuff.Pager import Pager
from python.nlp.TransformerStuff.UnPager import UnPager

@converter("html", "rest_markup")
class MarkupPublisher(RestPublisher) :
    from python.layout.LayoutReader.PDF2ETC import PDF2ETC
    from python.layouteagle.StandardConverter.Wordi2Css import Wordi2Css
    from python.nlp.TransformerStuff.ElmoDifference import ElmoDifference
    from python.nlp.TransformerStuff.Pager import Pager
    from python.nlp.TransformerStuff.UnPager import UnPager

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


        # pdf -> wordi
        #     -> wordi.page
        #     -> wordi.page.difference
        #     -> wordi.page.difference
        #     -> wordi.difference
        #     -> css.difference


    @uri_with_cache
    def on_post(self, req, resp):

        self.html_pipeline = self.ant("pdf", "htm")
        self.css_pipeline = self.ant("pdf", "css.difference")

        try:
            id = json.loads(req.stream.read())
            print(str(type(id)))
            print(id)
            pdf_s = [f"{config.pdf_dir}/{id}.pdf"]
            self.logger.warning(f"analysing {pdf_s}")
            html_path, html_meta = self(self.html_pipeline, pdf_s)
            css_value, css_meta = self(self.css_pipeline, pdf_s)
            pprint(css_value)
            print (html_path)

            #css_value = ["""
            #     .z5 {
            #        color: #92f !important;
            #        }
            # """]

            with open(html_path[0], "r") as f:
                html = "".join(f.readlines())

                return {
                    "html": html,
                    "css": css_value[0]
                }

        except Exception as e:
            print (html_path)

            self.logger.error("markup backend is called badly")
            raise e
