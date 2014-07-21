#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2012-03-23
@author: shell.xu
'''
import re, os, sys, urllib, getopt, logging, gevent
from os import path
from gevent import pool, monkey
from lxml import etree
from lxml.cssselect import CSSSelector
import utils

monkey.patch_all()
default_dir = None

def download(url):
    logging.info('downloading %s' % url)
    try: return urllib.urlopen(url).read()
    finally: logging.info('downloaded %s.' % url)

def save_pic(url):
    try: urllib.urlretrieve(url, path.join(default_dir, path.basename(url)))
    finally: logging.info('downloaded %s.' % url)

sel_get_page_pics = CSSSelector('a')
re_link = re.compile(r'//.*\.4cdn.org/./src/.*\.jpg')
def get_page_pics(p, url):
    try: page = etree.HTML(download(url))
    except: return
    for alink in sel_get_page_pics(page):
        link = alink.get('href')
        m = re_link.match(link)
        if not m: continue
        if not link.startswith('http:'): link = 'http:' + link
        p.spawn(save_pic, link)

def main():
    global default_dir
    optlist, args = getopt.getopt(sys.argv[1:], 'd:h:l:')
    optdict = dict(optlist)
    if '-h' in optdict:
        print main.__doc__
        return

    utils.initlog(optdict.get('-l', 'DEBUG'))
    default_dir = path.expanduser(optdict.get('-d', os.getcwd()))

    p = pool.Pool(10)
    for i in xrange(0, 11):
        get_page_pics(p, 'http://boards.4chan.org/s/%d' % i)
    p.join()

if __name__ == '__main__': main()
