from layouteagle.RestPublisher.Resource import Resource
from layouteagle.RestPublisher.RestPublisher import RestPublisher
from layouteagle.RestPublisher.react import react
from helpers.cache_tools import uri_with_cache
from layouteagle.pathant.Converter import converter
from layouteagle import config
from pprint import pprint


@converter("config",'dict')
class ConfigRest(RestPublisher, react):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs, resource=Resource(
            title="config",
            type="dict",
            path="config",
            route="config",
            access={"fetch": True, "read": True, "upload":True, "correct":True, "delete":True}))

    def __call__(self):
        return {v: getattr(config, v, None) for v in dir(config) if v[:2] != "__"}

    @uri_with_cache
    def on_get(self, req, resp):
        print("giving config info")
        resp.body = json.dumps(self(), ensure_ascii=False)
        resp.status = falcon.HTTP_OK

if __name__== "__main__":
    pprint(ConfigRest())