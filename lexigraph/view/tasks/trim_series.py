from google.appengine.api.labs import taskqueue

from lexigraph.view.tasks import TaskRequestHandler
from lexigraph.view import add_route
from lexigraph import model

class SeriesTrim(TaskRequestHandler):

    def post(self):
        series_key = self.request.get('series_key')
        series = model.DataSeries.get_by_key_name(series_key)
        if series is None:
            self.log.warning('No series exists with key %r' % (series_key,))
        else:
            series.trim_points()

add_route(SeriesTrim, '/tasks/trim_series')
