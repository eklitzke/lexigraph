from lexigraph.view import add_route
from lexigraph.handler import RequestHandler, requires_login
from lexigraph import model
from lexigraph.model.query import *
from lexigraph import config

class NewAccount(RequestHandler):

    @requires_login
    def post(self):
        account_name = self.request.get('account_name')
        if not account_name:
            self.redirect('/new/account')
        else:
            model.Account.create(account_name, self.user)
            self.redirect('/dashboard')

class ChooseAccount(RequestHandler):

    @requires_login
    def post(self):
        # XXX: no security here!
        name = self.form_required('account')
        account = maybe_one(model.Account.all().filter('name =', name))
        if account:
            self.session['account'] = account
            self.redirect('/dashboard')
        else:
            self.session['message'] = 'invalid choice'
            self.redirect('/choose/account')

class UpdateAccount(RequestHandler):

    @requires_login
    def get(self):
        mail = self.user.email()
        if config.whitelisted_emails and mail not in config.whitelisted_emails:
            self.session['message'] = 'Sorry, your email (%s) hasn\'t been whitelisted. Ask Evan if you need access.' % (mail,)
            self.redirect('/')
        self.env['accounts'] = fetch_all(model.Account.all().filter('owner =', self.user))
        self.render_template('account.html')


add_route(NewAccount, '/new/account')
add_route(ChooseAccount, '/choose/account')
add_route(UpdateAccount, '/account')
