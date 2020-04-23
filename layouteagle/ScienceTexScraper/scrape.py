import glob
import hashlib
import os
from itertools import count
import random

import requests
import time
from bs4 import BeautifulSoup

from layouteagle import config
from layouteagle.helpers.cache_tools import file_persistent_cached_generator

import logging

from layouteagle.pathant.Converter import converter
from layouteagle.pathant.PathSpec import PathSpec

logging.basicConfig(level = logging.INFO)

@converter("arxiv.org", "tex")
class ScienceTexScraper(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not os.path.isdir(config.tex_data):
            os.system(f"mkdir {config.tex_data}")

    @file_persistent_cached_generator(config.cache + 'scraped_tex_paths.json')
    def __call__(self, url):
        self.scrape_count = count()
        self.i = 0
        self.yet = []
        self.url = url
        yield from self.surf_random(url)

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

    def surf_random(self, url):
        logging.info(f"trying {url}")

        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "lxml")
            links = soup.findAll('a')
            random.shuffle(links)
            if response.status_code == 404:
                logging.error(f"404 for {url}")
                links = []
        except Exception as e:
            logging.error(f"Connection error, maybe timeout, maybe headers, maybe bad connection, continuing elsewhere: {e}")
            links = []



        hrefs = []
        for link in links:
            try:
                new_href = link['href']
                if not new_href.startswith("http"):
                    new_href= self.url + new_href
                if not (
                        any(s in new_href for s in ['e-print', 'archive', 'year', 'list', 'format'])
                        and not any(forbidden in new_href for forbidden in ['cornell.edu', 'pastweek', 'searchtype', 'recent', 'help'])
                        and new_href not in self.yet):
                    continue
            except KeyError:
                continue
            hrefs.append(new_href)

        # First look on the page for downloads, that should be done
        for href in hrefs:
            if "e-print" in href:
                logging.warning(f"getting {href}")
                name = hashlib.md5(href.encode('utf-8')).hexdigest()
                tar_gz_path = config.tex_data + name + ".tar.gz"
                path  =  config.tex_data + name
                os.system(
                    f'wget '
                    f'--user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" '
                    f'{href} '
                    f'-O {tar_gz_path}')

                unpack_path = config.tex_data + name
                os.system(f"mkdir -p {unpack_path} & "
                          f"tar -zxvf {tar_gz_path} -C {unpack_path}/")
                tex_files = glob.glob(path + "/*" + self.path_spec._to)
                yield from [(tex_file, {'meta':{'url': url}}) for tex_file in tex_files]

        # if not enough, random surf further
        for href in hrefs:
                self.yet.append(href)
                print(f"Got {href}")
                yield from self.surf_random(href)
                time.sleep(random.uniform(0.9, 1.9))





