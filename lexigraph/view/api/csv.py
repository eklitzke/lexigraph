import time
from lexigraph.view.api._common import *

LIMIT = 1000

class CSV(ApiRequestHandler):

    def initialize(self, request, response):
        super(CSV, self).initialize(request, response)
        response.headers['Content-Type'] = 'text/csv; charset=us-ascii'

    def get(self):
        series = self.get_series()
        if series is None:
            self.response.headers['Content-Type'] = 'text/plain; charset=us-ascii'
            self.response.out.write('No series was specified (try passing in series=XXX or dataset=XXX&interval=YYY)\n')
            return

        # prefer the most recent data, so order by -timestapm and then use reversed() below
        q = DataPoint.all().filter('series =', series).order('-timestamp').fetch(LIMIT)
        self.response.out.write('Timestamp,Value\n')
        for point in reversed(q):
            self.response.out.write('%s,%s\n' % (point.timestamp.strftime('%Y/%m/%d %H:%M:%S'), point.value))

__all__ = ['CSV']
