from lexigraph.view import add_route
from lexigraph.handler import RequestHandler, requires_login
from lexigraph import model

class NewAccount(RequestHandler):

    @requires_login
    def get(self):
        self.render_template('new_account.html')
    
    @requires_login
    def post(self):
        account_name = self.request.get('account_name')
        if not account_name:
            self.redirect('/new/account')
        else:
            model.Account.create(account_name, self.user)
            self.redirect('/dashboard')

add_route(NewAccount, '/new/account')
