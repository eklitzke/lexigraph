from lexigraph.view import add_route
from lexigraph.handler import RequestHandler, requires_login
from lexigraph import model

class EditGroups(RequestHandler):

    @requires_login
    def get(self):
        self.env['groups'] = model.AccessGroup.groups_for_user(self.account, self.user)
        self.render_template('edit_groups.html')

class NewGroup(RequestHandler):

    @requires_login
    def get(self):
        self.redirect('/groups')
    
    @requires_login
    def post(self):
        dataset_name = self.request.get('dataset_name')
        if not dataset_name:
            self.redirect('/new/dataset')
        
        aggregate = self.request.get('aggregate')
        
        max_age = self.request.get('max_age')

        if not account_name:
            self.redirect('/account')
        else:
            model.Account.create(account_name, self.user)
            self.redirect('/dashboard')

add_route(EditGroups, '/groups')
