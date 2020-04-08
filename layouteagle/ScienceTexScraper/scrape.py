import glob
import hashlib
import os
from itertools import count
import random

import requests
import time
from bs4 import BeautifulSoup

from layouteagle import config
from layouteagle.helpers.cache_tools import persist_to_file

import logging
logging.basicConfig(level = logging.INFO)

class ScienceTexScraper:
    def __init__(self, url, n, add_extension= ".gz.tar"):
        self.url = url
        self.n = n
        self.add_extension = add_extension
        if not os.path.isdir(config.tex_data):
            os.system(f"mkdir {config.tex_data}")

    @persist_to_file(config.scrape_cache + 'scraped_tex_paths.json')
    def __call__(self):
        self.scrape_count = count()
        self.i = 0
        self.yet = []
        return list(self.surf_random(self.url))

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

    def surf_random(self, url):
        logging.info(f"trying {url}")

        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "lxml")
            links = soup.findAll('a')
            random.shuffle(links)
        except:
            logging.error("Connection error, maybe timeout, maybe headers, maybe bad connection, continuing elsewhere")
            links = []

        # First look on the page for downloads, that should be done
        for link in links:
            try:
                new_url = link['href']
            except KeyError:
                continue
            if "e-print" in link.attrs['href']:
                self.i = next(self.scrape_count)
                if self.i >= self.n:
                    break
                else:
                    logging.warning(f"got {self.i + 1} of {self.n}")
                new_url = self.url +  new_url
                logging.warning(f"getting {new_url}")
                name = hashlib.md5(new_url.encode('utf-8')).hexdigest()
                tar_gz_path = config.tex_data + name + self.add_extension
                path  =  config.tex_data + name
                os.system(f'wget --user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" {new_url} -O {tar_gz_path}')
                os.system(f"mkdir -p ./tex_data/{name} & tar -zxvf {tar_gz_path} -C ./tex_data/{name}/")
                tex_files = glob.glob(path + "/*.tex")
                yield from tex_files

        # if not enough, random surf further
        for link in links:
            if self.i >= self.n:
                break
            try:
                new_url = link['href']
            except KeyError:
                continue
            if any(s in new_url for s in ['archive', 'year', 'list', 'format' ]) and not 'pastweek' in new_url and new_url not in self.yet:
                self.yet.append(new_url)
                new_url = self.url +  new_url
                yield from self.surf_random(new_url)
                time.sleep(random.uniform(0.9, 1.9))





