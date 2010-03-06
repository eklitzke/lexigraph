from lexigraph.view import add_route
from lexigraph.handler import AccountHandler
from lexigraph import model

class NewDataPoint(AccountHandler):

    requires_login = True

    def post(self):
        dataset_name = self.form_required('dataset')
        self.error_uri = '/edit/dataset?name=%s' % (dataset_name,)
        try:
            value = float(self.form_required('value'))
        except ValueError:
            self.redirect(self.error_uri)

        dataset = self.get_dataset(dataset_name)
        assert dataset.is_allowed(self.user, self.key, write=True)
        dataset.add_points(value=value)
        self.redirect('/edit/dataset?name=%s' % (dataset_name,))

add_route(NewDataPoint, '/new/datapoint')
