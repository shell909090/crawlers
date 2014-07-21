#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys

def f_country(line, country):
	global current_country
	current_country = country
	counter[current_country] = []

def f_mirror(line, mirror):
	if not mirror.strip(): return
	if current_country is None: return
	counter[current_country].append(mirror.strip())

def f_stop(line):
	global current_country
	current_country = None

counter = {}
current_country = None

mapper = [(re.compile('<p class="secthead"><a name=".*"></a><a name=".*">(.*)</a></p>'), f_country),
	  (re.compile('          <a href=".*">(.*)</a>'), f_mirror),
	  (re.compile('            </span>Other Mirrors</p>'), f_stop)]

def main(s):
	for line in s:
		for r, f in mapper:
			m = r.match(line)
			if not m: continue
			f(line, *m.groups())
			break

if __name__ == '__main__':
	s = open(sys.argv[1], 'r')
	main(s)
	s.close()
	for k, v in reversed(sorted(counter.items(), key=lambda i:len(i[1]))): print k, len(v)
	print sum(map(lambda i:len(i[1]), counter.items()))
