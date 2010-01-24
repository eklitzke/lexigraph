from lexigraph.view import add_route
from lexigraph.handler import AccountHandler, SessionHandler, InteractiveHandler
from lexigraph import model
from lexigraph.model.query import *

class NewDataSet(SessionHandler):

    requires_login = True

    def post(self):
        dataset_name = self.form_required('dataset')
        aggregate = self.form_required('aggregate')
        group_name = self.form_required('group')
        group = maybe_one(model.AccessGroup.all().filter('account =', self.account).filter('name =', group_name))
        if group is None:
            self.session['error_message'] = 'No such group %r existed' % (group_name,)
            self.redirect('/dashboard')
        if self.user.user_id() not in group.users:
            self.session['error_message'] = "You're not a member of that group"
            self.redirect('/dashboard')

        description = self.request.get('description') or None

        # create the dataset
        ds = model.DataSet(name=dataset_name, aggregate=aggregate, account=self.account, description=description)
        ds.put()
        self.log.debug('created new dataset, with id %s' % (ds.key().id(),))

        # add an access control for it
        access = model.AccessControl.new(group, ds, read=True, write=True, delete=True)
        access.put()
        self.log.debug('created new access control with id %s' % (access.key().id(),))

        self.redirect('/dashboard')

class EditDataSet(InteractiveHandler):

    requires_login = True

    def get(self):
        dataset = self.get_dataset(self.form_required('name', uri='/dashboard'))
        self.load_prefs()
        self.env['dataset'] = dataset
        self.env['series'] = fetch_all(model.DataSeries.all().filter('dataset =', dataset))
        self.env['can_delete'] = dataset.is_allowed(self.user, delete=True)
        self.render_template('edit_dataset.html')

class DeleteDataSet(AccountHandler):

    requires_login = True

    def post(self):
        dataset = self.get_dataset(self.form_required('name'))
        assert dataset.is_allowed(self.user, delete=True)

        # delete all of the data points
        for s in dataset.series():
            while True:
                points = fetch_all(model.DataPoint.all().filter('series =', s))
                if not points:
                    break
                for p in points:
                    p.delete()
            s.delete()
        for ac in fetch_all(model.AccessControl.all().filter('datset =', dataset)):
            ac.delete()
        dataset.delete()
        self.redirect('/dashboard')

add_route(NewDataSet, '/new/dataset')
add_route(EditDataSet, '/edit/dataset')
add_route(DeleteDataSet, '/delete/dataset')
