import time
import math
from collections import defaultdict

from google.appengine.api import users

from lexigraph import config
from lexigraph.view import add_route
from lexigraph.view.api._common import *
from lexigraph.handler import SessionHandler

from lexigraph import model

class CollectorTemplate(ApiRequestHandler):

    def get_worker(self):

        result = []

        interval_map = defaultdict(lambda: defaultdict(dict))
        for ds in model.DataSet.all().filter('account =', self.account):
            if not ds.is_allowed(user=self.user, api_key=self.key, write=True):
                continue

            series = list(ds.series())
            if not series:
                self.log.info('skipping dataset due to lack of series')
                continue
            d = interval_map[min(s.interval for s in series)]

            self.log.info('ds.name = %s' % (ds.name,))
            if ds.name in ('load1', 'load5', 'load15', 'cpu_count'):
                d['load'][ds.name] = ds.encode()
            elif ds.name.startswith('cpu_'):
                _, suffix = ds.name.split('_', 1)
                if suffix in ('total', 'user', 'system', 'nice', 'iowait'):
                    d['cpu'][suffix] = ds.encode()
            elif ds.name.startswith('mem_'):
                _, suffix = ds.name.split('_', 1)
                if suffix in ('total', 'buffers', 'cached', 'resident', 'used'):
                    d['memory'][suffix] = ds.encode()

        for k, v in interval_map.iteritems():
            if not dict(v):
                continue
            r = {'key': self.key, 'interval': int(k / 2.0), 'datasets': {}}
            for k, v in v.iteritems():
                r['datasets'][k] = v
            result.append(r)

        s = simplejson.dumps(result, sort_keys=True, indent=2)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(s + '\n')

add_route(CollectorTemplate, '/api/collector.json')
