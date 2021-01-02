#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
@date: 2020-12-25
@author: Shell.Xu
@copyright: 2020, Shell.Xu <shell909090@gmail.com>
@license: BSD-3-clause
'''
import os
import csv
import sys
import time
import random
import logging
import argparse
import datetime
from urllib import parse

import bs4
import requests
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument('--startdate', '-s', help='start date, eg 20201213. 750 days ago by default.')
parser.add_argument('cities', nargs='+', help='cities to get.')
args = parser.parse_args()

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

            totalprice = div.select('div.totalPrice span.number')
            if not totalprice:
                continue
            totalprice = totalprice[0].get_text().strip()
            if '-' in totalprice:
                totalprice = list(map(float, totalprice.split('-')))
                totalprice = sum(totalprice) / len(totalprice)

            unitprice = div.select('div.unitPrice span.number')
            if not unitprice:
                continue
            unitprice = unitprice[0].get_text().strip()
            if '-' in unitprice:
                unitprice = list(map(int, unitprice.split('-')))
                unitprice = sum(unitprice) / len(unitprice)

        except:
            logging.exception('unknown exception')
            continue
        yield title, dealdate, float(totalprice)*10000, int(unitprice)
    time.sleep(1)


def grab_price(city, name, baseurl):
    for i in range(1, 100):
        url = f'{baseurl}pg{i}/'
        recs = list(grab_price_page(url))
        if not recs:
            return
        for title, dealdate, totalprice, unitprice in recs:
            try:
                dealdt = datetime.datetime.strptime(dealdate, '%Y%m%d').date()
            except ValueError:
                dealdt = datetime.datetime.strptime(dealdate, '%Y%m').date()
            if dealdt < startdate:
                return
            if unitprice < 2000 or unitprice > 1000000:
                continue
            if title.endswith('平米'):
                title, size = title.rsplit(' ', 1)
                size = size.strip()[:-2]
                try:
                    float(size)
                except ValueError:
                    size = '{:.2f}'.format(totalprice/unitprice)
            else:
                size = '{:.2f}'.format(totalprice/unitprice)
            writer.writerow((dealdate, city, name, title, totalprice, unitprice, size))


def grab_area_info(name, url):
    data = download(url).text
    doc = bs4.BeautifulSoup(data, 'lxml')
    rslt = list(doc.select('div.resultDes div.total span'))
    if not len(rslt):
        return
    number = int(rslt[0].get_text().strip())
    logging.info(f'{name} have {number} records.')
    if number < 5000:
        yield url, name
        return
    for a in list(doc.select('div[data-role=ershoufang] div:nth-child(2) a')):
        yield parse.urljoin(url, a['href']), f'{name}.{a.get_text()}'


def grab_area(city):
    url = f'https://{city}.lianjia.com/chengjiao/'
    data = download(url).text
    doc = bs4.BeautifulSoup(data, 'lxml')
    baseurls = []
    for a in list(doc.select('div[data-role=ershoufang] div a'))[:5]:
        area_url = parse.urljoin(url, a['href'])
        rslt = grab_area_info(a.get_text(), area_url)
        if not rslt:
            continue
        baseurls.extend(list(rslt))
    return baseurls


def main():
    global startdate
    if args.startdate:
        startdate = datetime.datetime.strptime(args.startdate, '%Y%m%d').date()
    else:
        startdate = datetime.date.today() - datetime.timedelta(days=750)

    writer.writerow(('date', 'city', 'name', 'title', 'total', 'price', 'size'))
    for city in args.cities:
        baseurls = dict(grab_area(city))
        for baseurl, name in baseurls.items():
            grab_price(city, name, baseurl)


if __name__ == '__main__':
    main()
