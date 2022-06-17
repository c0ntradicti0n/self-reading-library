from core.RestPublisher.Resource import Resource
from core.RestPublisher.RestPublisher import RestPublisher
from core.RestPublisher.react import react
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec


@converter("*.css_html.*", "*.html")
class PATH2HTML(RestPublisher, react):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs, resource=Resource(
            title="difference",
            type="html",
            path="difference",
            route="difference",
            access={"add_id": True, "fetch": True, "read": True, "upload": True, "correct": True, "delete": True}))


    def __call__(self, labeled_paths, *args, **kwargs):
        for path, meta in labeled_paths:
            with open(meta['html_path'], "r") as f:
                content = f.read()
            meta['html'] = content
            yield path, meta