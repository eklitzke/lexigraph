from google.appengine.api import users

from lexigraph.view import add_route
from lexigraph.handler import AccountHandler, InteractiveHandler
from lexigraph import model
from lexigraph.model import maybe_one
from lexigraph.validate import validate_name

class GroupLanding(InteractiveHandler):

    requires_login = True

    def get(self):
        self.env['groups'] = model.AccessGroup.groups_for_user(self.account, self.user)
        self.render_template('edit_groups.html')

class EditGroups(InteractiveHandler):

    requires_login = True

    def get(self):
        a, b, group_name = self.uri.lstrip('/').split('/')
        validate_name(group_name)
        group = maybe_one(model.AccessGroup.all()
                          .filter('name =', group_name)
                          .filter('account =', self.account))
        if not group:
            self.log.warning('No group seen with name = %s, account = %s' % (group_name, self.account))
            self.not_found()
        self.env['group'] = group

        self.env['users'] = sorted((users.get_by_id(x) for x in group.users), key=lambda x: x.nickname())
        self.log.info('env = %s' % (env,))
        self.render_template('edit_group.html')

class NewGroup(AccountHandler):

    requires_login = True

    def post(self):
        dataset_name = self.request.get('dataset_name')
        if not dataset_name:
            self.redirect('/new/dataset')
        validate_name(dataset_name)

        aggregate = self.request.get('aggregate')
        
        max_age = self.request.get('max_age')

        if not account_name:
            self.redirect('/account')
        else:
            model.Account.create(account_name, self.user)
            self.redirect('/dashboard')

add_route(GroupLanding, '/groups')
add_route(EditGroups, '/edit/group/[^/]*')
