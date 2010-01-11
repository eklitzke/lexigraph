from lexigraph.view.cron._common import *

LIMIT = 1000

class DataPointTrim(CronRequestHandler):

    def get(self):
        for series in SeriesSchema.all().fetch(LIMIT):
            series.trim_points()
        self.response.set_status(204)

__all__ = ['DataPointTrim']
