from google.appengine.api.labs import taskqueue

from lexigraph.view.cron._common import *
from lexigraph.view import add_route
from lexigraph import model

class DataPointTrim(CronRequestHandler):

    def get(self):
        series = list(model.DataSeries.all())
        for s in series:
            taskqueue.add(url="/tasks/trim_series", params={'series_key': s.key()})
        self.response.out.write('series trim tasks queued for %d series' % len(series))

add_route(DataPointTrim, '/cron/trim/datapoints')
