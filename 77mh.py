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
import os
import sys
import logging
import subprocess
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
    output = subprocess.check_output(['phantomjs', '77mh.js', url])
    for i, line in enumerate(output.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        data = download(line)
        with open('%s/%0.4d.jpg' % (name, i), 'wb') as fo:
            fo.write(data)


def main():
    # urlbase = 'http://www.77mh.com/colist_237987.html'
    urlbase = sys.argv[1]

    doc = BeautifulSoup(download(urlbase), 'html5lib')
    for a in doc.select('ul.ar_list_col li a[target=_blank]'):
        name = a.get_text().strip()
        url = urljoin(urlbase, a['href'])
        logging.warning('create book %s' % name)
        try:
            os.mkdir(name)
        except OSError:
            pass

        parse_page(name, url)
        os.system(('zip -r "%s.zip" "%s"' % (name, name)).encode('utf-8'))


if __name__ == '__main__':
    main()
