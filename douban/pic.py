#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2012-03-23
@author: shell.xu
'''
import gevent
from gevent import pool, monkey
monkey.patch_all()

import os
import sys
import getopt
import logging
from os import path
from urllib.parse import urljoin

import requests
from lxml import etree
from lxml.cssselect import CSSSelector


logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

default_dir = None
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'

def download(url):
    headers = {'user-agent': USER_AGENT}
    try:
        resp = requests.get(url, headers=headers)
        return resp.content
    finally:
        logging.info('downloaded %s.' % url)


def save_pic(url):
    with open(path.join(default_dir, path.basename(url)), 'wb') as fo:
        fo.write(download(url))


sel_get_page_pics = CSSSelector('div#wrapper ul.pics img')
def get_page_pics(p, page):
    for img in sel_get_page_pics(page):
        p.spawn(save_pic, img.get('src').replace('/photo/photo/', '/photo/l/'))


sel_next_page = CSSSelector('span.next a')
def get_pages(url):
    while url:
        page = etree.HTML(download(url))
        yield page
        s = sel_next_page(page)
        new = urljoin(url, s and s[0].get('href'))
        if new == url:
            break
        url = new


def main(baseurls, opts):
    global default_dir
    default_dir = path.expanduser(opts.get('-d', os.getcwd()))
    p = pool.Pool(100)
    for url in baseurls:
        for page in get_pages(url):
            get_page_pics(p, page)
    p.join()


if __name__ == '__main__':
    optlist, args = getopt.getopt(sys.argv[1:], 'd:')
    main(args, dict(optlist))
