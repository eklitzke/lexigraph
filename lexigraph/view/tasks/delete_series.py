from google.appengine.api.labs import taskqueue

from lexigraph.view.tasks import TimedTaskHandler, WorkFinished
from lexigraph.view import add_route
from lexigraph import model

class DeleteSeries(TimedTaskHandler):
    """Delete a DataSeries, and all of the points in it."""

    LIMIT = 1000

    def remaining_params(self):
        return {'series_key': self.series_key}

    def before_work(self):
        self.series_key = self.request.get('series_key')
        self.series = model.DataSeries.get_by_key_name(series_key)
        if series is None:
            self.log.warning('No series exists with key %r' % (series_key,))
            return

    def do_piece(self):
        points = list(model.DataSeries.all().filter('series =', self.series).fetch(self.LIMIT))
        if not points:
            self.series.delete()
            raise WorkFinished

        for point in points:
            point.delete()

add_route(DeleteSeries, '/tasks/delete_series')
