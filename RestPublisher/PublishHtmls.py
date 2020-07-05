from RestPublisher.Resource import Resource
from RestPublisher.RestPublisher import RestPublisher
from RestPublisher.react import react
from layouteagle.pathant.Converter import converter


@converter("html", "rest_markup")
class MarkupPublisher(RestPublisher, react) :
    def __init__(self,
                 *args,
                 port=7770,
                 url = "localhost",
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(title="Markup", path="markup", route="markup"))
