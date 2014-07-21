#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2012-03-23
@author: shell.xu
'''
import sys, urllib, logging, gevent
from os import path
from gevent import pool, monkey
from lxml import etree

monkey.patch_all()
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def download(url):
    try: return urllib.urlopen(url).read()
    finally: logging.info('downloaded %s.' % url)

def save_pic(url):
    with open(path.basename(url), 'wb') as fo: fo.write(download(url))

def main(baseurls):
    p = pool.Pool(100)
    for url in baseurls:
        imgs = [img.get('lazyload-src') or img.get('src')
                for img in etree.HTML(download(url)).iter(tag='img')]
        for img in set(imgs): p.spawn(save_pic, img)
    p.join()

if __name__ == '__main__': main(sys.argv[1:])
