import os

from regex import regex

from config import config
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
    file_regex = '([-a-z%A-Z0-9./]+)+\.pdf'

    @configurable_cache(
        config.cache + os.path.basename(__file__), from_path_glob=config.hidden_folder + "/pdfs/**/*.pdf"
    )
    def __call__(self, i_url):
        for id, meta in i_url:
            if "url" in self.flags and self.flags['url']:
                url = self.flags['url']
            else:
                url = None

            if url and url.startswith('http') and regex.match(self.http_regex, url):
                path = id
                if os.path.exists(path):
                    yield path, meta

                path = path.replace("(", "")
                path = path.replace(")", "")
                meta['url'] = self.flags['url']

                if not os.path.exists(path):
                    os.system(f"wkhtmltopdf  {url} {path}")
                yield id, meta
            elif  os.path.exists(id) and regex.match(self.file_regex, id)  is not None:
                yield id, meta
            else:
                logging.error(f"{id} is not a valid url/path")

