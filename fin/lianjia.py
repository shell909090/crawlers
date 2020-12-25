#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
@date: 2020-12-25
@author: Shell.Xu
@copyright: 2020, Shell.Xu <shell909090@gmail.com>
@license: BSD-3-clause
'''
# import gevent
# from gevent import pool, monkey
# monkey.patch_all()

import os
import csv
import sys
import time
import logging
import datetime
from urllib import parse

import bs4
import requests
import pandas as pd


logger = logging.getLogger()
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'


session = requests.Session()
session.mount("http://", requests.adapters.HTTPAdapter(max_retries=3))
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))


writer = csv.writer(sys.stdout)


def download(url):
    headers = {'user-agent': USER_AGENT}
    resp = session.get(url, headers=headers)
    logging.info('downloaded %s.' % url)
    return resp


def grab_price_page(url):
    data = download(url).text
    doc = bs4.BeautifulSoup(data, 'lxml')
    for div in doc.select('div.info'):
        try:
            title = div.select('div.title')[0].get_text().strip()
            dealdate = div.select('div.dealDate')[0].get_text().strip().replace('.', '')
            totalprice = div.select('div.totalPrice span.number')[0].get_text().strip()
            if '-' in totalprice:
                totalprice = list(map(float, totalprice.split('-')))
                totalprice = sum(totalprice) / len(totalprice)
            unitprice = div.select('div.unitPrice span.number')[0].get_text().strip()
            if '-' in unitprice:
                unitprice = list(map(int, unitprice.split('-')))
                unitprice = sum(unitprice) / len(unitprice)
        except:
            logging.exception('unknown exception')
            continue
        yield title, dealdate, float(totalprice)*10000, int(unitprice)
    time.sleep(1)


def grab_price(city, name):
    today = datetime.date.today()
    for i in range(1, 100):
        url = f'https://{city}.lianjia.com/chengjiao/pg{i}rs{parse.quote(name)}/'
        for title, dealdate, totalprice, unitprice in grab_price_page(url):
            try:
                dealdt = datetime.datetime.strptime(dealdate, '%Y%m%d').date()
            except ValueError:
                dealdt = datetime.datetime.strptime(dealdate, '%Y%m').date()
            if (today - dealdt).days > 750:
                return
            if unitprice < 2000 or unitprice > 1000000:
                continue
            writer.writerow((dealdate, city, name, title, totalprice, unitprice, int(totalprice/unitprice)))


def main():
    writer.writerow(('date', 'city', 'name', 'title', 'total', 'price', 'size'))
    grab_price('bj', '和平里')
    grab_price('bj', '黄庄')
    grab_price('bj', '方庄')
    grab_price('sh', '世纪大道')
    grab_price('sh', '打浦桥')
    grab_price('sh', '古北')
    grab_price('xm', '思明')
    grab_price('xm', '湖里')
    grab_price('gy', '花果园')
    grab_price('km', '五华')
    grab_price('km', '西山')


if __name__ == '__main__':
    main()
