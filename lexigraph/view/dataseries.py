from lexigraph.view import add_route
from lexigraph.handler import SessionHandler
from lexigraph import model
from lexigraph.model.query import *
from django.utils import simplejson
from google.appengine.ext import db


class NewDataSeries(SessionHandler):

    requires_login = True

    def post(self):
        dataset_name = self.form_required('dataset')
        interval = int(self.form_required('interval'))
        max_age = self.request.get('max_age') or None
        if max_age:
            max_age = int(max_age)

        dataset = maybe_one(model.DataSet.all().filter('name =', dataset_name).filter('account =', self.account))
        if not dataset:
            self.log.warning('no such dataset')
            self.render_json({'success': False})
            return

        if not dataset.is_allowed(user=self.user, write=True):
            self.log.warning('not allowed to write to this dataset')
            self.render_json({'success': False})
            return

        ds = model.DataSeries(dataset=dataset, interval=interval, max_age=max_age)
        ds.put()
        self.log.info('successfully created dataseries with id %s' % (ds.key().id(),))
        self.render_json({'success': True, 'id': ds.key().id()})

class DeleteDataSeries(SessionHandler):

    requires_login = True

    def post(self):
        series_id = int(self.form_required('series_id'))
        series = model.DataSeries.get_by_id(series_id)
        assert series.dataset.is_allowed(self.user, delete=True)

        # XXX: this is racy (i.e. if someone creates points while we're deleting
        # the dataset). This ought to be amended by a cron job that looks for
        # abandoned points, or by implementing locking.

        # delete all of the data points
        while True:
            points = fetch_all(model.DataPoint.all().filter('series =', series))
            if not points:
                break
            for p in points:
                p.delete()
        series.delete()
        self.render_json({'success': True})

add_route(NewDataSeries, '/new/dataseries')
add_route(DeleteDataSeries, '/delete/dataseries')
