from lexigraph.view import add_route
from lexigraph.handler import RequestHandler, requires_login
from lexigraph import model

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
            self.redirect('/new/account')
        else:
            model.Account.create(account_name, self.user)
            self.redirect('/dashboard')

add_route(NewDataset, '/new/dataset')