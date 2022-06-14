import glob
import hashlib
import itertools
import os
from itertools import count
import random
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
class ScienceTexScraper(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cwd = os.getcwd() + '/'
        self.save_dir = config.tex_data
        if not os.path.isdir(self.save_dir):
            os.system(f"mkdir {config.tex_data}")

    delivered = []

    def __call__(self, url):
        self.scrape_count = count()
        self.i = 0
        self.yet = []
        self.url = None
        if 'texs' in self.flags:
            yield from list(metaize(self.flags['texs']))
        else:
            yield from self.surf(enumerate(url))

    headers = {
        'User-Agent': 'Self-reading Library/1.0'}

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info("navigating backt to " + self.cwd)


    @configurable_cache(
        config.cache + os.path.basename(__file__)
    )
    def surf(self, i_url):
        yield from self.surf_random(i_url)

    def surf_random(self, i_url, depth=5):
        for i, url in i_url:

            url = url[0]
            if not self.url:
                self.url = url

            logging.info(f"trying {url}")

            links = []
            while not links:
                try:
                    response = requests.get(url, headers=self.headers, timeout=30)
                    time.sleep(random.uniform(0.9, 1.9))
                    soup = BeautifulSoup(response.text, "lxml")
                    links = soup.findAll('a')
                    random.shuffle(links)
                    if response.status_code == 404:
                        logging.error(f"404 for {url}")
                        links = []
                except Exception:
                    logging.error(
                        f"Connection error on {url}, maybe timeout, maybe headers, maybe bad connection, keeping trying", exc_info=True)
                    links = []
                    time.sleep(40)

            hrefs = []
            for link in links:
                try:
                    new_href = link['href']
                    if new_href in url:
                        continue
                    if not new_href.startswith("http"):
                        new_href = self.url + new_href
                    if not (
                            any(s in new_href for s in ['e-print', 'archive', 'year', 'list', 'format'])
                            and not any(
                        forbidden in new_href for forbidden in
                        ['cornell.edu', 'pastweek', 'searchtype', 'recent', 'help', 'stat'])
                            and new_href not in self.yet):
                        continue
                except KeyError:
                    continue
                hrefs.append(new_href)

            # First look on the page for downloads, that should be done
            for href in hrefs:
                href = href.replace('format', 'pdf')
                if "pdf" in href:
                    logging.warning(f"getting {href}")
                    name = href.replace(self.url, '').replace('/', '-')
                    path = self.cwd + config.tex_data + name
                    if not path in self.delivered:
                        os.system(
                            f'mkdir {path} &  wget '
                            f'--user-agent="{self.headers["User-Agent"]}" '
                            f'{href} '
                            f'-O {path}/main.pdf')

                        pdf = f"{path}/main.pdf"
                        self.delivered.append(path)

                        yield (pdf, {'pdf': pdf, 'url': url})

            # if not enough, random surf further
            random.shuffle(hrefs)
            for href in hrefs:
                self.yet.append(href)
                print(f"Got {href}")
                if not depth < 0:
                    yield from self.surf_random([(href, (href, {}))], depth=depth - 1)
