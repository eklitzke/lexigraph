from lexigraph.view import add_route
from lexigraph.handler import SessionHandler
from lexigraph import model
from lexigraph.model.query import *
from django.utils import simplejson

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

        self.render_json({'success': True})

add_route(NewDataSeries, '/new/dataseries')
