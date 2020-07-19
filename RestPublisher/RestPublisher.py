import itertools
import logging
import mimetypes
import os
import uuid
from typing import List, Tuple, Dict

import falcon as falcon
import pandas
from pip._vendor import msgpack

from RestPublisher.Resource import Resource
from RestPublisher.react import react
from layouteagle import config
from layouteagle.helpers.cache_tools import file_persistent_cached_generator
from layouteagle.pathant.Converter import converter
from layouteagle.pathant.PathAnt import PathAnt
from layouteagle.pathant.PathSpec import PathSpec

from flask import request, jsonify, Blueprint
from flask_login import login_required, login_user, current_user, logout_user


bp = Blueprint('blueprint', __name__, template_folder='templates')

class RestPublisher(PathSpec, react) :
    """

    publishes path-ant-path on a Representational State Transfer api with autocreated jsvascript class for reading.... to CRUPD class
    """

    # deliver paths
    def on_get(self):
        return jsonify(meta=self.meta), 200

    # get html
    def on_post(self, i):
        return jsonify(page=self.data[i]), 200

    # upload
    def on_put(self, file, meta_data):
        with open(self.upload_docs + self.new_path(), "w") as f:
            f.write(file)

    # correction
    def on_patch(self, text, location, annotation):
        with open(self.upload_docs + self.new_annotation(), "w") as f:
            raise NotImplementedError()

    # hide... or delete all mentioned paths
    def on_delete(self, i):
        self.data.pop(i)
        self.meta.pop(i)


    def __init__(self,
                 *args,
                 port=7770,
                 url = "localhost",
                 resource : Resource = None,
                 **kwargs):

        react.__init__(self, *args, **kwargs)
        PathSpec.__init__(self, *args, **kwargs)
        assert resource and isinstance(resource, Resource)
        self.url = url
        self.port = port
        self.resource = resource
        self.contents = []
        self.logger.warning("publishing")

        self.logger.warning(f"Creating service for {self.resource.title}")

        with open("/".join([self.npm_resources, self.resource.title + ".ts"]), "w") as f:
            f.write(self.react_code.format(**self.resource, port = self.port, url=self.url, access=self.resource.accsess))

        self.logger.warning(f"Creating components for {self.resource.title}")

        self.write_components("/".join([self.npm_components, self.resource.title + ".ts"]))

        self.logger.warning(f"Creating page for {self.resource.title}")

        with open("/".join([self.npm_pages, self.resource.title + ".ts"]), "w") as f:
            f.write(self.page.format(**self.resource, port = self.port, url=self.url, access=self.resource.accsess))


    def __iter__(self, incoming):
        if not self.contents:
            self.contents = list(incoming)


    react_code = \
"""

class ??title!! extends ServerResource<??title!!>{
    constructor () {
        super(
         fetch_allowed = ??access[fetch]!!, 
         read_allowed =  ??access[read]!!, 
         upload_allowed =  ??access[upload]!!,
         correct_allowed =  ??access[correct]!!,
         delete_allowed =  ??access[delete]!!
        )
    }
}

""".replace("{", "{{").replace("}", "}}").replace("??", r"{").replace("!!", "}")


    page = """
import Router from 'next/router'

    
    """.replace("{", "{{").replace("}", "}}").replace("??", r"{").replace("!!", "}")

    components = {
        "??resource!!Container": """
        ??access[fetch]!!Container extends TemplateContainer {
            
        }
        """.replace("{", "{{").replace("}", "}}").replace("??", r"{").replace("!!", "}"),
        "??resource!!Fetch": """
    ??access[fetch]!!Container extends TemplateContainer {

    }
    """.replace("{", "{{").replace("}", "}}").replace("??", r"{").replace("!!", "}")
    }

    def write_components(self, param):
        written_componens= []
        for component, code in self.components.items():
            with open("/".join([self.npm_resources, self.resource.title + ".ts"]), "w") as f:
                f.write(code.format(**self.resource, port=self.port, url=self.url, access=self.resource.accsess))
                written_componens.append(component)





import unittest

class TestPaperPublisher(unittest.TestCase):

    def setUp(self):
        self.ant = PathAnt()
        self.model_pipe = self.ant("arxiv.org", "keras")
        self.prediction_pipe = self.ant("pdf", "layout.html")

    def test_make_model(self):
        model_pipe = self.ant("arxiv.org", "keras")
        print(list(model_pipe("https://arxiv.org")))

    def test_rest(self):
        os.system(" git clone https://github.com/matt-sm/create-react-flask.git ")
        model_pipe = self.ant("arxiv.org", "keras")


if __name__ == '__main__':
    unittest.main()

