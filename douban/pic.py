#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2012-03-23
@author: shell.xu
'''
import os, sys, urllib, getopt, logging, gevent
from os import path
from gevent import pool, monkey
from lxml import etree
from lxml.cssselect import CSSSelector

monkey.patch_all()
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
default_dir = None

def download(url):
    try: return urllib.urlopen(url).read()
    finally: logging.info('downloaded %s.' % url)

def save_pic(url):
    with open(path.join(default_dir, path.basename(url)), 'wb') as fo:
        fo.write(download(url))

sel_get_page_pics = CSSSelector('div.photo_wrap img')
def get_page_pics(p, page):
    for img in sel_get_page_pics(page):
        p.spawn(save_pic, img.get('src').replace('/thumb/', '/photo/'))

sel_next_page = CSSSelector('span.next a')
def get_pages(url):
    while url:
        page = etree.HTML(download(url))
        yield page
        s = sel_next_page(page)
        url = s and s[0].get('href')

def main(baseurls, opts):
    global default_dir
    default_dir = path.expanduser(opts.get('-d', os.getcwd()))
    p = pool.Pool(100)
    for url in baseurls:
        for page in get_pages(url): get_page_pics(p, page)
    p.join()

if __name__ == '__main__':
    optlist, args = getopt.getopt(sys.argv[1:], 'd:')
    main(args, dict(optlist))
