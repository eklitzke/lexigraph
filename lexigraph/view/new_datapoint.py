from lexigraph.view import add_route
from lexigraph.handler import RequestHandler, requires_login
from lexigraph import model
from lexigraph.model.query import *

class NewDataPoint(RequestHandler):

    @requires_login
    def get(self):
        self.redirect('/dashboard')

    @requires_login
    def post(self):
        dataset_name = self.form_required('dataset')
        value = float(self.form_required('value'))

        dataset = maybe_one(model.DataSet.all().filter('name =', dataset_name).filter('account =', self.current_account))
        if not dataset:
            self.log.warning('no such dataset')
            self.redirect('/dashboard')

        if not dataset.is_allowed(user=self.user, write=True):
            self.log.warning('not allowed to write to this dataset')
            self.redirect('/dashboard')

        dataset.add_points(value=value)
        self.redirect('/dashboard')

add_route(NewDataPoint, '/new/datapoint')
