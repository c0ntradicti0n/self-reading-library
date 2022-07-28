import os
import sys
import time
from collections import namedtuple
from types import SimpleNamespace

import falcon

import core.config

core.config.cache = "./tests/test_cache/"
os.system(f"rm -rf {core.config.cache}")
from backend import *

run_extra_threads()
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

import unittest


class TestRest(unittest.TestCase):
    TEST_PDF = '.layouteagle/pdfs/9912/math9912149.pdf'

    def make_rest_args(self, *args):
        Req = namedtuple("req", ['media'])
        req = Req(media=args[0] if len(args) == 1 else args)
        resp = SimpleNamespace(headers={})
        return req, resp

    def check_result(self, req, resp):
        assert "Content-Disposition" in resp.headers or  resp.body != None
        assert resp.status == falcon.HTTP_OK
        print(resp)

    def test_difference(self):
        rest_vals = self.make_rest_args(self.TEST_PDF)
        ElmoDifferenceQueueRest.on_post(*rest_vals)
        self.check_result(*rest_vals)

    def test_layout(self):
        rest_vals = self.make_rest_args(self.TEST_PDF)
        UploadAnnotationQueueRest.on_post(*rest_vals)
        self.check_result(*rest_vals)

    def test_audio(self):
        rest_vals = self.make_rest_args(self.TEST_PDF)
        AudioPublisher.on_post(*rest_vals)
        self.check_result(*rest_vals)

    def test_topics(self):
        time.sleep(60)
        rest_vals = self.make_rest_args(self.TEST_PDF)
        TopicsPublisher.on_get(*rest_vals)
        self.check_result(*rest_vals)

    def test_annotation(self):
        rest_vals = self.make_rest_args(self.TEST_PDF, """It is a result of Bourgain [1, 2] that M1 may become O(N2/3
) and it is very easy to construct a collection
λj which gives M2 = O(N1/2
), which is the conjectured optimal. For minimizing M2 it is also possible to
have the collection of frequencies relatively well packed, that is with λN ≤ 2N [3], while for any ǫ > 0 and
for any collection λj that makes M1 = O(N1−ǫ
) one can easily see that λN is super-polynomial in N.""", self.TEST_PDF)
        DifferenceAnnotationPublisher.on_post(*rest_vals)
        self.check_result(*rest_vals)


if __name__ == '__main__':
    unittest.main()
