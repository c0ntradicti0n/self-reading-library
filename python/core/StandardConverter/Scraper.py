import glob
import hashlib
import itertools
import os
import urllib
from itertools import count
import random

from regex import regex

from helpers.list_tools import metaize, unique
import requests
import time
from bs4 import BeautifulSoup
from core import config
from helpers.cache_tools import configurable_cache

import logging

from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec


@converter("arxiv.org", "tex")
class Scraper(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cwd = os.getcwd() + '/'
        self.save_dir = config.tex_data
        if not os.path.isdir(self.save_dir):
            os.system(f"mkdir {config.tex_data}")

    http_regex = r'(https?:\/\/(?:www\.|(?!www))?[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})'
    file_regex = rf'{config.tex_data}[-a-z0-9./]+\.pdf'

    @configurable_cache(
        config.cache + os.path.basename(__file__), from_path_glob=config.hidden_folder + "/pdfs/**/*.pdf"
    )
    def __call__(self, i_url):
        for url, m in i_url:
            if url.startswith('http') and regex.match(self.http_regex, url):
                path = f"{config.hidden_folder}/pdfs/{urllib.parse.quote_plus(url)}.pdf"
                os.system(f"chromium  --headless \
                                      --disable-gpu \
                                      --disable-translate \
                                      --disable-extensions \
                                      --disable-background-networking \
                                      --safebrowsing-disable-auto-update \
                                      --disable-sync \
                                      --metrics-recording-only \
                                      --disable-default-apps \
                                      --no-first-run \
                                      --mute-audio \
                                      --hide-scrollbars \
                                      --disable-software-rasterizer "
                                    f"--print-to-pdf={path} {url}")
                yield path, m
            elif os.path.exists(url) and regex.match(self.file_regex, url)  is not None:
                yield url, m
            else:
                logging.error(f"{url} is not a valid url/path")
