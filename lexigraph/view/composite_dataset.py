from lexigraph.view import add_route
from lexigraph import model
from lexigraph.handler.interactive import SessionHandler

class NewCompositeDataSet(SessionHandler):

    requires_login = True

    def post(self):
        datasets = self.form_required('datasets')
        datasets = [x.strip() for x in datasets.split(',')]
        self.get_datasets(datasets)

        # TODO: validate tags
        tags = self.form_required('tags')
        tags = set(x.strip() for x in tags.split(','))
        tags.add('composite')

        composite = model.CompositeDataSet(names=datasets, tags=list(tags), account=self.account)
        composite.put()

        self.redirect('/dashboard')

add_route(NewCompositeDataSet, '/new/composite_dataset')
