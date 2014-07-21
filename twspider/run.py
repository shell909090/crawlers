#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2014-03-22
@author: shell.xu
'''
import os, sys, time, getopt, logging
from os import path

import gevent, gevent.pool
from gevent import monkey
monkey.patch_all()
import twitter, requests, redis

LOGFMT = '%(asctime)s.%(msecs)03d[%(levelname)s](%(module)s:%(lineno)d): %(message)s'
def initlog(lv, logfile=None, stream=None, longdate=False):
    if isinstance(lv, basestring): lv = getattr(logging, lv)
    kw = {'format': LOGFMT, 'datefmt': '%H:%M:%S', 'level': lv}
    if logfile: kw['filename'] = logfile
    if stream: kw['stream'] = stream
    if longdate: kw['datefmt'] = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(**kw)

def getcfg(cfgpathes):
    from ConfigParser import SafeConfigParser
    cp = SafeConfigParser()
    cp.read(cfgpathes)
    return cp

def download_pic(url):
    filename = path.basename(url)
    if path.exists(filename) and os.stat(filename).st_size != 0:
        logging.info('hit: ' + url)
        return
    logging.info('download: ' + url)
    res = requests.get(url+':large')
    if res.status_code == 200:
        with open(filename, 'wb') as fo:
            fo.write(res.content)

def run_download(r):
    while True:
        url = r.blpop('media_url', 10)
        if url is not None:
            download_pic(url[1])
        elif stopflag: return

def run_user(r, api, user, max_id=None):
    while True:
        time.sleep(cfg.getint('main', 'intervals'))
        if r.llen('media_url') > cfg.getint('main', 'max_len'):
            continue

        logging.warning('get timeline from id: ' + str(max_id))
        l = None
        for i in xrange(cfg.getint('main', 'retries')):
            try:
                l = api.GetUserTimeline(
                    screen_name=user, count=200, max_id=max_id)
                break
            except Exception, err:
                logging.exception(err)
        if not l:
            logging.info('user %s timeline end' % user)
            return

        urls = []
        for i in l:
            urls.extend([m['media_url'] for m in i.media])
        max_id = i.id
        r.rpush('media_url', *urls)

def main():
    global cfg
    cfg = getcfg(['twspider.conf',])
    initlog(cfg.get('log', 'loglevel'), cfg.get('log', 'logfile'))

    r = redis.StrictRedis(**dict(cfg.items('redis')))
    api = twitter.Api(**dict(cfg.items('oauth')))

    global stopflag
    stopflag = False

    pool = gevent.pool.Pool(cfg.getint('main', 'threads'))
    for i in xrange(cfg.getint('main', 'threads')):
        pool.spawn(run_download, r)
    for user in cfg.get('main', 'users').split(';'):
        run_user(r, api, user)

    stopflag = True
    pool.join()

if __name__ == '__main__': main()
