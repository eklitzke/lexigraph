from lexigraph.view.cron._common import *
from lexigraph.view import add_route
from lexigraph import model
from lexigraph.model.query import *

class DataPointTrim(CronRequestHandler):

    def get(self):
        series = fetch_all(model.DataSeries.all())
        for s in series:
            s.trim_points()
        self.response.out.write('points trimmed for %d series' % len(series))

add_route(DataPointTrim, '/cron/trim/datapoints')
