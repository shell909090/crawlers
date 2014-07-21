#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2012-12-01
@author: shell.xu
'''
import os, sys
from os import path
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup

import urllib2

def download(url):
    return urllib2.urlopen(url).read()

def getSection(s, url, name):
    doc = BeautifulSoup(download(url))
    s.write((u'<br/><h1>%s</h1><br/>' % name).encode('utf-8'))
    s.write(str(doc.find('span', id='ChapterBody')))

def getNovel(url):
    uri = urlparse(url)
    doc = BeautifulSoup(download(url))
    for a in doc.findAll('a'):
        if not a['href'].startswith('/Novel/'): continue
        yield '%s://%s%s' % (uri.scheme, uri.hostname, a['href']), a.string

def main():
    fi, fo = os.popen2('html2text -utf8')
    for url, name in getNovel(sys.argv[1]):
        print url, name
        getSection(fi, url, name)
    fi.close()
    r = fo.read()
    with open('novel.txt', 'w') as fo: fo.write(r)

if __name__ == '__main__': main()
