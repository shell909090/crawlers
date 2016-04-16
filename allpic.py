#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2012-03-23
@author: shell.xu
'''
import gevent
from gevent import pool, monkey
monkey.patch_all()

import sys, logging
from os import path
from urlparse import urlparse, urljoin
from lxml import etree
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

def download(url):
    headers = {'user-agent': USER_AGENT}
    resp = requests.get(url, headers=headers)
    logging.info('downloaded %s.' % url)
    return resp.content

def get_img(img, baseurl):
    url = img.get('lazyload-src') or img.get('src') or img.get('file')
    u = urlparse(url)
    if u.scheme == '':
        if baseurl[-1] != '/':
            baseurl = path.dirname(baseurl)
        url = path.join(baseurl, url)
        u = urlparse(url)
    return u.geturl()

def save_pic(img, baseurl):
    url = get_img(img, baseurl)
    filename = path.basename(url)
    if '?' in filename:
        filename = filename.split('?')[0]
    with open(filename, 'wb') as fo:
        fo.write(download(url))

def main(baseurls):
    p = pool.Pool(100)
    for url in baseurls:
        doc = etree.HTML(download(url))
        for img in doc.iter(tag='img'):
            p.spawn(save_pic, img, url)
    p.join()

if __name__ == '__main__': main(sys.argv[1:])
