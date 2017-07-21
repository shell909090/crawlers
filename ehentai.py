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
import logging
import tempfile
import subprocess
from os import path
from urlparse import urlparse, urljoin
import bs4
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


def get_img(tmpdir, url):
    data = download(url)
    doc = bs4.BeautifulSoup(data, 'lxml')
    for img in doc.select('img#img'):
        filename = path.basename(img['src'])
        filepath = path.join(tmpdir, filename)
        data = download(img['src'])
        with open(filepath, 'wb') as fo:
            fo.write(data)


def get_page(baseurl):
    p = pool.Pool(20)
    last = None
    tmpdir = tempfile.mkdtemp()
    for i in xrange(0, 1000):
        url = '%s?p=%d' % (baseurl, i)
        data = download(url)
        if data == last:
            break
        doc = bs4.BeautifulSoup(data, 'lxml')
        for a in doc.select('div.gdtm div a'):
            p.spawn(get_img, tmpdir, a['href'])
        for title in doc.select('h1#gj'):
            pass
        last = data
    p.join()
    print(title.get_text())
    subprocess.call(['zip', '-r', '%s.zip' % title.get_text(), tmpdir])


def main():
    baseurls = sys.argv[1:]
    for baseurl in baseurls:
        get_page(baseurl)


if __name__ == '__main__':
    main()
