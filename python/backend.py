import falcon
from wsgiref import simple_server
from config.ant_imports import *
from layout.annotator.annotation_to_gold import AnnotatedToGoldQueueRest


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

    publishing = {
        "/ant/{id}": AntPublisher,
        # difference
        "/difference/{id}": ElmoDifferenceQueueRest,
        "/difference_annotation/{id}": DifferenceAnnotationPublisher,
        # layout
        "/annotation_captcha/{id}": AnnotationQueueRest,
        "/upload_annotation/{id}": UploadAnnotationQueueRest,
        "/layout/{id}": LayoutPublisher,
        # captcha
        "/difference_captcha/{id}": AnnotationSpanToGoldQueueRest,
        "/layout_captcha/{id}": AnnotatedToGoldQueueRest,
        "/layout_captcha": AnnotatedToGoldQueueRest,
        # topics
        "/library/{id}": TopicsPublisher,
        # audiobook
        "/audiobook/{id}": AudioPublisher,
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

    api = falcon.App(middleware=[cors.middleware, MultipartMiddleware()])

    for route, module in publishing.items():
        api.add_route(route, module)

    logging.info(f"API: {api}")
    return api


if __name__ == "__main__":
    api = create_app()
    logging.debug(get_all_routes(api))
    httpd = simple_server.make_server("0.0.0.0", config.PORT, api)
    httpd.serve_forever()

    import gunicorn.app.base

    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            config = {
                key: value
                for key, value in self.options.items()
            }
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
