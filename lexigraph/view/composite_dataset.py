from lexigraph.view import add_route
from lexigraph import model
from lexigraph.handler.interactive import SessionHandler

class NewCompositeDataSet(SessionHandler):

    requires_login = True

    def check_allowed(self, datasets):
        count = 0
        for ds in model.DataSet.all().filter('account =', self.account).filter('name IN', datasets):
            count += 1
            if not ds.is_allowed(user=self.user, read=True, write=True):
                self.session['error_message'] = 'Insufficient privileges'
                self.redirect('/dashboard')
        if count < len(set(datasets)):
            self.session['error_message'] = 'Failed to find all specified datasets'
            self.redirect('/dashboard')

    def post(self):
        name = self.form_required('name')
        datasets = self.form_required('datasets')
        datasets = [x.strip() for x in datasets.split(',')]
        self.check_allowed(datasets)

        # TODO: validate tags
        tags = self.form_required('tags')
        tags = set(x.strip() for x in tags.split(','))
        tags.add('composite')

        composite = model.CompositeDataSet.create(name=name, names=datasets, tags=list(tags), account=self.account)
        composite.put()

        self.redirect('/dashboard')

add_route(NewCompositeDataSet, '/new/composite_dataset')
