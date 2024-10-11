#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2012-03-23
@author: shell.xu
'''
import gevent
from gevent import pool, monkey
monkey.patch_all()

import sys
import urllib
import logging
from os import path

import requests
from lxml import etree


logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'


def download(url):
    headers = {'user-agent': USER_AGENT}
    try:
        resp = requests.get(url, headers=headers)
        return resp.content
    finally:
        logging.info('downloaded %s.' % url)


def save_pic(url):
    with open(path.basename(url), 'wb') as fo:
        fo.write(download(url))


def main():
    baseurls = sys.argv[1:]
    p = pool.Pool(100)
    for url in baseurls:
        imgs = [img.get('lazyload-src') or img.get('src')
                for img in etree.HTML(download(url)).iter(tag='img')]
        for img in set(imgs): p.spawn(save_pic, img)
    p.join()


if __name__ == '__main__':
    main()
