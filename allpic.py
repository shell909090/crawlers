#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@date: 2012-03-23
@author: shell.xu
'''
import gevent
from gevent import pool, monkey
monkey.patch_all()

import sys
import time
import logging
from os import path
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
# from lxml import etree
import requests


logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'

session = requests.Session()
session.mount("http://", requests.adapters.HTTPAdapter(max_retries=3))
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))


def download(url, **kw):
    logging.info(f'download {url}')
    headers = {'user-agent': USER_AGENT}
    # kw['verify'] = False
    resp = session.get(url, headers=headers, **kw)
    time.sleep(1)
    return resp


def save_pic(img, baseurl):
    url = img.get('lazyload-src') or img.get('src') or img.get('file')
    url = urljoin(baseurl, url)
    filename = path.basename(url)
    if '?' in filename:
        filename = filename.split('?', 1)[0]
    resp = download(url)
    if resp.status_code == 200:
        with open(filename, 'wb') as fo:
            fo.write(resp.content)


def main():
    p = pool.Pool(5)
    for url in sys.argv[1:]:
        baseurl = url
        if baseurl[-1] != '/':
            baseurl = path.dirname(baseurl)
        resp = download(url)
        doc = BeautifulSoup(resp.text, 'lxml')
        for img in doc.select('img'):
            p.spawn(save_pic, img, baseurl)
    p.join()


if __name__ == '__main__':
    main()
