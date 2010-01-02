#!/usr/bin/env python
import urllib
import simplejson
import sys
import pprint

def main(url, fields={}):
    resp = urllib.urlopen(url, urllib.urlencode(fields)).read()
    try:
        pprint.pprint(simplejson.loads(resp))
    except ValueError:
        print resp

if __name__ == '__main__':
    d = {}
    for arg in sys.argv[2:]:
        k, v = arg.split('=', 1)
        d[k] = v
    main(sys.argv[1], d)
