from google.appengine.api.labs import taskqueue

from lexigraph.view.cron._common import *
from lexigraph.view import add_route
from lexigraph import model

class DataPointTrim(CronRequestHandler):

    def get(self):
        for s in model.DataSeries.all():
            key = s.key()
            taskqueue.add(url='/tasks/trim_series', params={'series_key': key})
            self.response.out.write('queued series_key = %r' % (key,))

add_route(DataPointTrim, '/cron/trim/datapoints')
