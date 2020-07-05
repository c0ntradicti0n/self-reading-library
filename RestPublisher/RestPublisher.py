import itertools
import logging
import mimetypes
import os
import uuid
from typing import List, Tuple, Dict

import falcon as falcon
import pandas
from pip._vendor import msgpack

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
                 resource = None,
                 **kwargs):

        react.__init__(self, *args, **kwargs)
        PathSpec.__init__(self, *args, **kwargs)
        assert resource
        self.url = url
        self.port = port
        self.resource = resource
        self.contents = []
        self.logger.info("publishing")

        with open(self.npm_project + self.resource.path, "w") as f:
            f.write(self.react_code.format(**self.resource, port = self.port, url=self.url))




    def __iter__(self, incoming):
        if not self.contents:
            self.contents = list(incoming)


    react_code = \
"""

class ??title!! {
    async function which() {

    let response = await fetch('??url!! + ":" + ??port!! + "/" + ??route!!');

    console.log(response.status); // 200
    console.log(response.statusText); // OK

    if (response.status === 200) {
        let data = await response.text();
        // handle data
        return data
    }
    
    // Example POST method implementation:
    async function give(url = '', data = {}) {
      // Default options are marked with *
      const response = await fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
          'Content-Type': 'application/json'
          // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        body: JSON.stringify(data) // body data type must match "Content-Type" header
      });
      return response.json(); // parses JSON response into native JavaScript objects
    }
    
        async function upload(url = '', data = {}) {
    async function correct(url = '', data = {}) {
    async function hide(url = '', data = {}) {

}

""".replace("{", "{{").replace("}", "}}").replace("??", r"{").replace("!!", "}")




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

