import datetime
from google.appengine.api import users

from lexigraph.handler import RequestHandler
from lexigraph import model
from lexigraph.model.query import *
import lexigraph.session

class AccountHandler(RequestHandler):
    """A request handler that knows about logged in users and API keys. Nearly
    all handlers should subclass from this (or a subclass of this).
    """

    def initialize_env(self):
        super(AccountHandler, self).initialize_env()
        self.user = users.get_current_user()
        self.user_id = self.user.user_id() if self.user else None
        self.accounts = []
        if self.user:
            self.accounts = model.Account.by_user(self.user)

    @property
    def account(self):
        if not (self.user or self.key):
            return None
        if self.key:
            group = maybe_one(model.AccessGroup.all().filter('api_token =', self.key))
            if not group:
                self.log.info('No AccessGroup associated with key %s' % (self.key,))
                return None
            return group.account
        return self.get_account_by_user()

    def get_account_by_user(self):
        raise NotImplementedError

    def get_dataset(self, name, check_read=True, check_write=False, check_delete=False):
        assert name
        ds = maybe_one(model.DataSet.all().filter('name =', name).filter('account =', self.account))
        if ds is not None and not ds.is_allowed(self.user, self.key, read=check_read, write=check_write, delete=check_delete):
            raise PermissionsError
        return ds

class SessionHandler(AccountHandler):
    """A request handler that knows about sessions and user accounts."""

    def initialize_env(self):
        super(SessionHandler, self).initialize_env()
        if self.user:
            self.session = lexigraph.session.SessionState(self.user)
        else:
            self.session = None

    def get_account_by_user(self):
        account = self.session['account']
        if account is None:
            accounts = model.Account.by_user(self.user)
            if not accounts:
                self.session['error_message'] = 'You must create an account first.'
                account = None
            elif len(accounts) == 1:
                account = accounts[0]
                self.session['account'] = account
            else:
                self.session['info_message'] = 'Select an account.'
                #self.redirect('/choose/account')
                account = None
        else:
            self.log.info('hit account = %s in session' % (account,))
        return account

class InteractiveHandler(SessionHandler):

    def load_prefs(self):
        """Load preferences for the current user. No work is done if this method
        has already been called during this request.
        """
        if 'prefs' not in self.env:
            self.env['prefs'] = model.UserPrefs.load_by_user_id(self.user_id)
        return self.env['prefs']

    def initialize_env(self):
        super(InteractiveHandler, self).initialize_env()

        self.env['accounts'] = self.accounts
        if self.user:
            self.env['account'] = self.account

        if self.session:
            self.env['info_message'] = self.session.get_once('info_message')
            self.env['error_message'] = self.session.get_once('error_message')
        else:
            self.env['info_message'] = self.env['error_message'] = None
        
        # used for the copyright date on the footer
        self.env['copyright_year'] = datetime.date.today().year

    def get_template(self, name):
        return self.jinja_env.get_template(name)

    def render_template(self, name):
        template = self.get_template(name)
        self.response.out.write(template.render(**self.env))
