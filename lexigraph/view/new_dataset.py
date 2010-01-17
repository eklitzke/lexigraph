from lexigraph.view import add_route
from lexigraph.handler import RequestHandler, requires_login
from lexigraph import model
from lexigraph.model.query import *

class NewDataSet(RequestHandler):

    @requires_login
    def get(self):
        self.redirect('/dashboard')

    @requires_login
    def post(self):
        dataset_name = self.form_required('dataset')
        aggregate = self.form_required('aggregate')
        group_name = self.form_required('group')
        self.log.info('GETTINg group')
        group = maybe_one(model.AccessGroup.all().filter('account =', self.current_account).filter('name =', group_name))
        if group is None:
            self.log.warning('No such group existed where account = %s, name = %s' % (self.current_account.name, group_name))
            self.redirect('/dashboard')
        if self.user.user_id() not in group.users:
            self.log.warning('User ID %s not present in group %s' % (self.user.user_id(), group_name))
            self.redirect('/dashboard')
        self.log.info('XXX: group = %s' % (group,))

        description = self.request.get('description')

        # create the dataset
        ds = model.DataSet(name=dataset_name, aggregate=aggregate, account=self.current_account)
        ds.put()
        self.log.info('created new dataset with id %s' % (ds.key().id(),))

        # add an access control for it
        access = model.AccessControl.new(group, ds, read=True, write=True, delete=True)
        access.put()
        self.log.debug('created new access control with id %s' % (access.key().id(),))

        self.redirect('/dashboard')

add_route(NewDataSet, '/new/dataset')
