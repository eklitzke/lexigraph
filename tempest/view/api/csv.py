import time
from tempest.view.api._common import *

LIMIT = 1000

class CSV(ApiRequestHandler):

    def initialize(self, request, response):
        super(CSV, self).initialize(request, response)
        response.headers['Content-Type'] = 'text/csv; charset=us-ascii'

    def get(self):
        series = self.get_series()
        self.log.info('series = %s' % (series,))
        #q = DataPoint.all().filter('series =', series).order('timestamp').fetch(LIMIT)
        q = DataPoint.all().filter('series =', series).fetch(LIMIT)
        self.response.out.write('Timestamp,Value\n')
        for point in q:
            t = time.mktime(point.timestamp.timetuple())

            self.response.out.write('%s,%s\n' % (t, t.value))

__all__ = ['CSV']
