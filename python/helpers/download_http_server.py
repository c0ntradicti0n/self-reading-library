import sys,os
sys.path.append(os.getcwd())

import os
from pathlib import Path
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
import math

from config import config


def get_links(content):
    soup = BeautifulSoup(content)
    for a in soup.findAll('a'):
        yield a.get('href'), a.get_text()


def download(url, path=None, overwrite=False):
    if path is None:
        path = urlparse(url).path.lstrip('/')
    if url.endswith('/'):
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception('status code is {} for {}'.format(r.status_code, url))
        content = r.text
        Path(path.rstrip('/')).mkdir(parents=True, exist_ok=True)
        for link, name in get_links(content):
            if not link.startswith('.'):  # skip hidden files such as .DS_Store
                download(urljoin(url, link), os.path.join(path, name))
    else:
        if os.path.isfile(path):
            print("#existing", path)
            if not overwrite:
                return
        chunk_size = 1024 * 1024
        r = requests.get(url, stream=True)
        content_size = int(r.headers['content-length'])
        total = math.ceil(content_size / chunk_size)
        print("#", path)
        with open(path, 'wb') as f:
            c = 0
            st = 100
            for chunk in r.iter_content(chunk_size=chunk_size):
                c += 1
                if chunk:
                    f.write(chunk)
                ap = int(c * st / total) - int((c - 1) * st / total)
                if ap > 0:
                    print("#" * ap, end="")
            print("\r  ", " " * int(c * st / total), "\r", end="")


if __name__ == '__main__':
    # the trailing / indicates a folder
    for f in [config.GOLD_DATASET_PATH, config.tex_data]:

        url = f'http://polarity.science:8000/{f.replace(config.hidden_folder, "")}/'
        folder = f"x/{f}"
        os.makedirs(folder, exist_ok=True)
        download(url, f"x/{f}/")