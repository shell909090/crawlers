#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2012-12-01
@author: shell.xu
'''
import os, sys, urllib2
from os import path
from bs4 import BeautifulSoup

title = ''

def download(url):
    return urllib2.urlopen(url).read()

def getSection(s, url, name):
    doc = BeautifulSoup(download(url))
    s.write((u'<br/><h1>%s</h1><br/>' % name).encode('utf-8'))
    s.write(str(doc.find('div', id='content')))

def getNovel(url):
    global title
    doc = BeautifulSoup(download(url))
    title = doc.find('div', id='title').string
    for a in doc.findAll('a'):
        if u'href' not in dict(a.attrs): continue
        if a['href'].find('reader.php') != -1: continue
        if a['href'].startswith('http'): continue
        yield '%s/%s' % (path.dirname(url), a['href']), a.string

def main():
    fi, fo = os.popen2('html2text -utf8')
    for url, name in getNovel(sys.argv[1]):
        print url, name
        getSection(fi, url, name)
    fi.close()
    r = fo.read()
    with open(title + '.txt', 'w') as fo: fo.write(r)

if __name__ == '__main__': main()
