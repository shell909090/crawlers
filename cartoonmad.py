#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2017-02-04
@author: Shell.Xu
@copyright: 2017, Shell.Xu <shell909090@gmail.com>
@license: BSD-3-clause
'''
from __future__ import absolute_import, division,\
    print_function, unicode_literals
# import gevent
# from gevent import pool, monkey
# monkey.patch_all()
import os
import sys
import logging
from os import path
from urlparse import urljoin
from bs4 import BeautifulSoup
import requests

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

session = requests.Session()
session.mount("http://", requests.adapters.HTTPAdapter(max_retries=3))
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))


def download(url):
    headers = {'user-agent': USER_AGENT}
    resp = requests.get(url, headers=headers)
    logging.info('downloaded %s.' % url)
    return resp.content


def parse_page(name, url):
    doc = BeautifulSoup(download(url), 'html5lib')

    imgs = doc.select('td[align=center] a img[onload]')
    assert len(imgs) == 1, "image length not 1"
    imgurl = imgs[0]['src']

    data = download(imgurl)
    logging.warning('download image %s' % imgurl)
    with open(path.join(name, path.basename(imgurl)), 'wb') as fo:
        fo.write(data)

    nexturls = set([p.parent['href'] for p in doc.select(
        'td a.pages img[src=/image/rad.gif]')])
    assert len(nexturls) <= 2, "more then one next page"
    nexturl = list(nexturls)[0]
    if nexturl == u'thend.asp':
        return
    return path.dirname(url) + '/' + nexturl


def parse_directory(url):
    doc = BeautifulSoup(download(url), 'html5lib')

    for a in doc.select('fieldset#info td a[target=_blank]'):
        name = a.get_text().strip()
        pageurl = urljoin(url, a['href'])
        logging.warning('create book %s' % name)
        try:
            os.mkdir(name)
        except OSError:
            pass

        while pageurl:
            pageurl = parse_page(name, pageurl)

        os.system(('zip -r "%s.zip" "%s"' % (name, name)).encode('utf-8'))


def main():
    for url in sys.argv[1:]:
        parse_directory(url)


if __name__ == '__main__':
    main()
