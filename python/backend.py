import falcon
from wsgiref import simple_server
from config.ant_imports import *
from debugger_tools import connect_debugger
from helpers.os_tools import make_fresh_dir
from helpers.time_tools import timeout
from language.knowledge.KnowledgePublisher import KnowledgePublisher
from layout.annotator.annotation_to_gold import AnnotatedToGoldQueueRest


class ExampleMiddleware:
    def process_request(self, req, resp):
        """Process the request before routing it.

        Note:
            Because Falcon routes each request based on req.path, a
            request can be effectively re-routed by setting that
            attribute to a new value from within process_request().

        Args:
            req: Request object that will eventually be
                routed to an on_* responder method.
            resp: Response object that will be routed to
                the on_* responder.
        """
        timeout(lambda : connect_debugger(2345), 1)

    def process_resource(self, req, resp, resource, params):
        """Process the request after routing.

        Note:
            This method is only called when the request matches
            a route to a resource.

        Args:
            req: Request object that will be passed to the
                routed responder.
            resp: Response object that will be passed to the
                responder.
            resource: Resource object to which the request was
                routed.
            params: A dict-like object representing any additional
                params derived from the route's URI template fields,
                that will be passed to the resource's responder
                method as keyword arguments.
        """

    def process_response(self, req, resp, resource, req_succeeded):
        """Post-processing of the response (after routing).

        Args:
            req: Request object.
            resp: Response object.
            resource: Resource object to which the request was
                routed. May be None if no route was found
                for the request.
            req_succeeded: True if no exceptions were raised while
                the framework processed and routed the request;
                otherwise False.
        """


def get_all_routes(api):
    routes_list = []

    def get_children(node):
        if len(node.children):
            for child_node in node.children:
                get_children(child_node)
        else:
            routes_list.append((node.uri_template, node.resource))

    [get_children(node) for node in api._router._roots]
    return routes_list


def create_app():

    logging.info(f"STARTING APP")

    from language.transformer.ElmoDifference import ElmoDifferenceQueueRest

    from core.rest.LayoutPublisher import LayoutPublisher

    make_fresh_dir(config.REST_WORKING)

    publishing = {
        # difference
        "/difference": ElmoDifferenceQueueRest,
        "/difference_annotation": DifferenceAnnotationPublisher,
        # layout
        "/upload_annotation": UploadAnnotationQueueRest,
        "/layout": LayoutPublisher,
        # captcha
        "/difference_captcha": AnnotationSpanToGoldQueueRest,
        "/layout_captcha": AnnotatedToGoldQueueRest,
        # ----
        "/library": TopicsPublisher,
        "/audiobook": AudioPublisher,
        "/knowledge": KnowledgePublisher,
        "/ant": AntPublisher,
    }

    from falcon_cors import CORS

    cors = CORS(
        allow_origins_list=["*"],
        allow_all_origins=True,
        allow_all_headers=True,
        allow_credentials_all_origins=True,
        allow_all_methods=falcon.HTTP_METHODS,
        log_level="DEBUG",
    )

    from falcon_multipart.middleware import MultipartMiddleware
    from falcon_compression.middleware import CompressionMiddleware

    api = falcon.App(
        middleware=[
            cors.middleware,
            MultipartMiddleware(),
            CompressionMiddleware(),
            ExampleMiddleware(),
        ]
    )

    for route, module in publishing.items():
        api.add_route(route, module)

    # from werkzeug.middleware.profiler import ProfilerMiddleware

    # api = ProfilerMiddleware(api, sort_by=["cumtime", "ncalls"])
    # , sort_by=["cum_time"])

    # logging.info(f"API: {api}")

    return api


if __name__ == "__main__":
    api = create_app()

    # logging.debug(get_all_routes(api))
    httpd = simple_server.make_server("0.0.0.0", config.PORT, api)
    httpd.serve_forever()

    import gunicorn.app.base

    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        "bind": f"0.0.0.0:{PORT}",
        "workers": 1,
        "timeout": 500,
    }

    logging.info(f"Starting with simple server at 0.0.0.0:{config.PORT}")
    logging.info(get_all_routes(api))
    StandaloneApplication(api, options).run()
